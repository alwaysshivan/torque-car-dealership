import pytest
from fastapi.testclient import TestClient
from backend.app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app(tmp_path / 'test.sqlite3', secret='test-only-secret-at-least-32-characters')


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def user(client):
    payload = {'name': 'Siva', 'email': 'siva@example.com', 'password': 'StrongPass123!'}
    client.post('/api/auth/register', json=payload)
    token = client.post('/api/auth/login', json={k: payload[k] for k in ('email', 'password')}).json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin(client, app):
    from backend.security import hash_password
    with app.state.db.connect() as conn:
        conn.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)',
                     ('Admin', 'admin@example.com', hash_password('AdminPass123!'), 'admin'))
    token = client.post('/api/auth/login', json={'email': 'admin@example.com', 'password': 'AdminPass123!'}).json()['access_token']
    return {'Authorization': f'Bearer {token}'}
