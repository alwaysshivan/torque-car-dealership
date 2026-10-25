from concurrent.futures import ThreadPoolExecutor
import pytest

VEHICLE = {'make': 'Tata', 'model': 'Nexon', 'category': 'SUV', 'price': 1450000, 'quantity': 3,
           'year': 2026, 'fuel': 'Petrol', 'color': 'Blue'}


def add(client, admin, **changes):
    response = client.post('/api/vehicles', headers=admin, json=VEHICLE | changes)
    assert response.status_code == 201, response.text
    return response.json()


def test_protected_routes_and_roles(client, user, admin):
    assert client.get('/api/vehicles').status_code == 401
    assert client.post('/api/vehicles', headers=user, json=VEHICLE).status_code == 403
    car = add(client, admin)
    for method, path, body in [('delete', '', None), ('post', '/restock', {'quantity': 2}), ('put', '', VEHICLE)]:
        kwargs = {'headers': user}
        if body is not None:
            kwargs['json'] = body
        assert getattr(client, method)(f"/api/vehicles/{car['id']}{path}", **kwargs).status_code == 403


def test_crud_and_search(client, user, admin):
    car = add(client, admin)
    add(client, admin, make='Hyundai', model='i20', category='Hatchback', price=900000)
    assert len(client.get('/api/vehicles', headers=user).json()) == 2
    queries = ['make=taTA', 'model=Nex', 'category=SUV', 'min_price=1000000&max_price=1500000', 'q=nexon', 'q=%27%20OR%201%3D1--']
    for query in queries:
        result = client.get('/api/vehicles/search?' + query, headers=user)
        assert result.status_code == 200
        assert len(result.json()) == (0 if query.startswith('q=%') else 1)
    assert client.get('/api/vehicles/search?min_price=20&max_price=10', headers=user).status_code == 422
    updated = client.put(f"/api/vehicles/{car['id']}", json=VEHICLE | {'model': 'Nexon EV', 'price': '1600000.25'}, headers=admin)
    assert updated.json()['model'] == 'Nexon EV'
    assert updated.json()['price'] == 1600000.25
    assert client.get(f"/api/vehicles/{car['id']}", headers=user).status_code == 200
    assert client.delete(f"/api/vehicles/{car['id']}", headers=admin).status_code == 204
    assert client.get(f"/api/vehicles/{car['id']}", headers=user).status_code == 404


@pytest.mark.parametrize('change', [{'price': -1}, {'quantity': -1}, {'quantity': 1.5}, {'quantity': True},
                                    {'price': '1.999'}, {'make': ' '}, {'category': 'Boat'}, {'year': 1800}])
def test_invalid_vehicles(client, admin, change):
    assert client.post('/api/vehicles', headers=admin, json=VEHICLE | change).status_code == 422


def test_purchase_and_restock(client, user, admin):
    car = add(client, admin, quantity=1)
    url = f"/api/vehicles/{car['id']}"
    purchase = client.post(url + '/purchase', headers=user, json={'quantity': 1})
    assert purchase.status_code == 201
    assert purchase.json()['remaining_stock'] == 0
    assert client.post(url + '/purchase', headers=user, json={'quantity': 1}).status_code == 409
    assert client.post(url + '/purchase', headers=user, json={'quantity': 0}).status_code == 422
    assert client.post(url + '/restock', headers=admin, json={'quantity': 2}).json()['quantity'] == 2
    assert len(client.get('/api/purchases', headers=user).json()) == 1
    assert client.get('/api/purchases', headers=admin).json() == []
    assert client.get('/api/stats', headers=user).json()['stock_units'] == 2


def test_concurrent_purchases_cannot_oversell(client, user, admin):
    car = add(client, admin, quantity=1)
    def buy(_):
        return client.post(f"/api/vehicles/{car['id']}/purchase", headers=user, json={'quantity': 1}).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        codes = list(pool.map(buy, range(4)))
    assert sorted(codes) == [201, 409, 409, 409]
    assert len(client.get('/api/purchases', headers=user).json()) == 1


def test_missing_ids_and_stock_limits(client, user, admin):
    for endpoint, headers in [('purchase', user), ('restock', admin)]:
        assert client.post('/api/vehicles/missing/' + endpoint, headers=headers, json={'quantity': 1}).status_code == 404
    assert client.put('/api/vehicles/missing', headers=admin, json=VEHICLE).status_code == 404
    assert client.delete('/api/vehicles/missing', headers=admin).status_code == 404
    car = add(client, admin, quantity=100000)
    assert client.post(f"/api/vehicles/{car['id']}/restock", headers=admin, json={'quantity': 1}).status_code == 409


def test_sql_wildcards_are_literal(client, user, admin):
    add(client, admin)
    assert client.get('/api/vehicles/search?q=%25', headers=user).json() == []
    assert client.get('/api/vehicles/search?q=_', headers=user).json() == []
