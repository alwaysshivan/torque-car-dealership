import os
import secrets
import sqlite3
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from backend.db import Database
from backend.dependencies import current_user
from backend.schemas import Login, Register
from backend.security import hash_password, issue_token, verify_password

ROOT = Path(__file__).resolve().parent.parent


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
    from backend.vehicles import router
    app.include_router(router)

    dist = ROOT / 'frontend' / 'dist'
    if dist.is_dir():
        app.mount('/', StaticFiles(directory=dist, html=True), name='frontend')
    return app
