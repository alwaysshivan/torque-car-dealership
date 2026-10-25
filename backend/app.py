import os
import secrets
import sqlite3
from pathlib import Path
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from backend.db import Database
from backend.schemas import Login, Register
from backend.security import hash_password, issue_token, verify_password

ROOT = Path(__file__).resolve().parent.parent
bearer = HTTPBearer(auto_error=False)


def current_user(request: Request, auth: HTTPAuthorizationCredentials = Depends(bearer)):
    if not auth:
        raise HTTPException(401, 'Please sign in to continue', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(auth.credentials, request.app.state.secret, algorithms=['HS256'], options={'require': ['exp', 'sub']})
        user_id = int(payload['sub'])
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(401, 'Session expired or invalid. Please sign in again.')
    with request.app.state.db.connect() as conn:
        row = conn.execute('SELECT id,name,email,role FROM users WHERE id=?', (user_id,)).fetchone()
    if not row:
        raise HTTPException(401, 'Account no longer exists')
    return dict(row)


def admin_user(user=Depends(current_user)):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Administrator access required')
    return user


def load_secret(database_path):
    if os.getenv('JWT_SECRET'):
        if len(os.environ['JWT_SECRET']) < 32:
            raise RuntimeError('JWT_SECRET must contain at least 32 characters')
        return os.environ['JWT_SECRET']
    path = Path(database_path).parent / '.jwt-secret'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        try:
            with path.open('x') as stream:
                stream.write(secrets.token_urlsafe(48))
            path.chmod(0o600)
        except FileExistsError:
            pass
    return path.read_text().strip()


def create_app(database_path=None, secret=None):
    database_path = database_path or os.getenv('DATABASE_PATH', str(ROOT / 'data' / 'dealership.sqlite3'))
    app = FastAPI(title='Torque | Dealership Inventory', version='1.0.0')
    app.state.db = Database(database_path)
    app.state.secret = secret or load_secret(database_path)

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    @app.post('/api/auth/register', status_code=201)
    def register(body: Register):
        try:
            with app.state.db.connect() as conn:
                cursor = conn.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',
                                      (body.name, body.email, hash_password(body.password)))
                return {'id': cursor.lastrowid, 'name': body.name, 'email': body.email, 'role': 'user'}
        except sqlite3.IntegrityError:
            raise HTTPException(409, 'An account with this email already exists')

    @app.post('/api/auth/login')
    def login(body: Login):
        with app.state.db.connect() as conn:
            row = conn.execute('SELECT * FROM users WHERE email=?', (body.email,)).fetchone()
        if not row or not verify_password(body.password, row['password_hash']):
            raise HTTPException(401, 'Incorrect email or password')
        return {'access_token': issue_token(row['id'], app.state.secret), 'token_type': 'bearer',
                'user': {key: row[key] for key in ('id', 'name', 'email', 'role')}}

    @app.get('/api/auth/me')
    def me(user=Depends(current_user)):
        return user

    # API routes are registered before the frontend fallback.
    try:
        from backend.vehicles import router
    except ModuleNotFoundError as exc:
        if exc.name != 'backend.vehicles':
            raise
    else:
        app.include_router(router)

    dist = ROOT / 'frontend' / 'dist'
    if dist.is_dir():
        app.mount('/', StaticFiles(directory=dist, html=True), name='frontend')
    return app
