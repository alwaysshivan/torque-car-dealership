"""Inventory endpoints. Purchases decrement stock and write receipts atomically."""
from decimal import Decimal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from backend.app import admin_user, current_user
from backend.schemas import Quantity, VehicleInput

router = APIRouter(prefix='/api')


def vehicle(row):
    data = dict(row)
    data['price'] = data.pop('price_cents') / 100
    return data


def get_vehicle(conn, vehicle_id):
    row = conn.execute('SELECT * FROM vehicles WHERE id=?', (vehicle_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Vehicle not found')
    return vehicle(row)


def vehicle_values(body):
    return (body.make, body.model, body.category, int(body.price * 100), body.quantity, body.year, body.fuel, body.color)


def escape_like(text):
    return '%' + text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'


@router.get('/vehicles')
@router.get('/vehicles/search')
def list_vehicles(request: Request, q: str = Query('', max_length=100), make: str = '', model: str = '',
                  category: str = '', min_price: Decimal | None = Query(None, ge=0, le=1000000000),
                  max_price: Decimal | None = Query(None, ge=0, le=1000000000),
                  in_stock: bool = False, sort: str = 'newest', user=Depends(current_user)):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(422, 'Minimum price must not exceed maximum price')
    clauses, params = [], []
    for column, value in [('make', make), ('model', model), ('category', category)]:
        if value:
            clauses.append(f"{column} LIKE ? ESCAPE '\\'")
            params.append(escape_like(value))
    if q:
        clauses.append("(make || ' ' || model || ' ' || category) LIKE ? ESCAPE '\\'")
        params.append(escape_like(q))
    for operator, amount in [('>=', min_price), ('<=', max_price)]:
        if amount is not None:
            clauses.append(f'price_cents {operator} ?')
            params.append(int(amount * 100))
    if in_stock:
        clauses.append('quantity > 0')
    ordering = {'newest': 'created_at DESC, rowid DESC', 'price_asc': 'price_cents ASC',
                'price_desc': 'price_cents DESC', 'name': 'make ASC, model ASC'}
    if sort not in ordering:
        raise HTTPException(422, 'Invalid sort order')
    sql = 'SELECT * FROM vehicles' + (' WHERE ' + ' AND '.join(clauses) if clauses else '')
    with request.app.state.db.connect() as conn:
        return [vehicle(row) for row in conn.execute(sql + ' ORDER BY ' + ordering[sort], params).fetchall()]


@router.post('/vehicles', status_code=201)
def add_vehicle(body: VehicleInput, request: Request, user=Depends(admin_user)):
    vehicle_id = str(uuid4())
    with request.app.state.db.connect() as conn:
        conn.execute('INSERT INTO vehicles(id,make,model,category,price_cents,quantity,year,fuel,color) VALUES(?,?,?,?,?,?,?,?,?)',
                     (vehicle_id, *vehicle_values(body)))
        return get_vehicle(conn, vehicle_id)


@router.get('/vehicles/{vehicle_id}')
def read_vehicle(vehicle_id: str, request: Request, user=Depends(current_user)):
    with request.app.state.db.connect() as conn:
        return get_vehicle(conn, vehicle_id)


@router.put('/vehicles/{vehicle_id}')
def update_vehicle(vehicle_id: str, body: VehicleInput, request: Request, user=Depends(admin_user)):
    with request.app.state.db.connect() as conn:
        cursor = conn.execute('UPDATE vehicles SET make=?,model=?,category=?,price_cents=?,quantity=?,year=?,fuel=?,color=? WHERE id=?',
                              (*vehicle_values(body), vehicle_id))
        if cursor.rowcount == 0:
            raise HTTPException(404, 'Vehicle not found')
        return get_vehicle(conn, vehicle_id)


@router.delete('/vehicles/{vehicle_id}', status_code=204)
def delete_vehicle(vehicle_id: str, request: Request, user=Depends(admin_user)):
    with request.app.state.db.connect() as conn:
        cursor = conn.execute('DELETE FROM vehicles WHERE id=?', (vehicle_id,))
        if cursor.rowcount == 0:
            raise HTTPException(404, 'Vehicle not found')
    return Response(status_code=204)


@router.post('/vehicles/{vehicle_id}/purchase', status_code=201)
def purchase(vehicle_id: str, body: Quantity, request: Request, user=Depends(current_user)):
    with request.app.state.db.connect() as conn:
        # Acquire the write lock before reading to serialize competing transactions.
        conn.execute('BEGIN IMMEDIATE')
        car = get_vehicle(conn, vehicle_id)
        cursor = conn.execute('UPDATE vehicles SET quantity=quantity-? WHERE id=? AND quantity>=?',
                              (body.quantity, vehicle_id, body.quantity))
        if not cursor.rowcount:
            raise HTTPException(409, 'Not enough stock available. Refresh and try again.')
        receipt_id = str(uuid4())
        price_cents = int(Decimal(str(car['price'])) * 100)
        conn.execute('INSERT INTO purchases(id,user_id,vehicle_id,make,model,quantity,unit_price_cents) VALUES(?,?,?,?,?,?,?)',
                     (receipt_id, user['id'], vehicle_id, car['make'], car['model'], body.quantity, price_cents))
        return {'id': receipt_id, 'quantity': body.quantity, 'total': price_cents * body.quantity / 100,
                'remaining_stock': car['quantity'] - body.quantity}


@router.post('/vehicles/{vehicle_id}/restock')
def restock(vehicle_id: str, body: Quantity, request: Request, user=Depends(admin_user)):
    with request.app.state.db.connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        car = get_vehicle(conn, vehicle_id)
        if car['quantity'] + body.quantity > 100000:
            raise HTTPException(409, 'Stock cannot exceed 100,000 units')
        conn.execute('UPDATE vehicles SET quantity=quantity+? WHERE id=?', (body.quantity, vehicle_id))
        return get_vehicle(conn, vehicle_id)


@router.get('/purchases')
def purchases(request: Request, user=Depends(current_user)):
    with request.app.state.db.connect() as conn:
        rows = conn.execute('SELECT * FROM purchases WHERE user_id=? ORDER BY created_at DESC, rowid DESC', (user['id'],)).fetchall()
    return [{k: row[k] for k in ('id', 'vehicle_id', 'make', 'model', 'quantity', 'created_at')} |
            {'unit_price': row['unit_price_cents'] / 100, 'total': row['quantity'] * row['unit_price_cents'] / 100} for row in rows]


@router.get('/stats')
def stats(request: Request, user=Depends(current_user)):
    with request.app.state.db.connect() as conn:
        row = conn.execute('SELECT COUNT(*) AS models, COALESCE(SUM(quantity),0) AS stock_units, '
                           'COALESCE(SUM(price_cents*quantity),0) AS value_cents, '
                           'COALESCE(SUM(CASE WHEN quantity<=2 THEN 1 ELSE 0 END),0) AS low_stock FROM vehicles').fetchone()
    return {'models': row['models'], 'stock_units': row['stock_units'], 'inventory_value': row['value_cents'] / 100,
            'low_stock': row['low_stock']}
