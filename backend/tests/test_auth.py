import sqlite3
import jwt
from backend.security import verify_password


def test_registration_hashes_password_and_never_returns_it(client, app):
    response = client.post('/api/auth/register', json={'name': 'Siva', 'email': 'SIVA@example.com', 'password': 'StrongPass123!'})
    assert response.status_code == 201
    assert response.json()['role'] == 'user'
    assert response.json()['email'] == 'siva@example.com'
    assert 'password' not in str(response.json())
    with app.state.db.connect() as conn:
        row = conn.execute('SELECT password_hash FROM users').fetchone()
    assert row[0] != 'StrongPass123!'
    assert verify_password('StrongPass123!', row[0])


def test_duplicate_email_and_invalid_input(client):
    payload = {'name': 'Siva', 'email': 'siva@example.com', 'password': 'StrongPass123!'}
    assert client.post('/api/auth/register', json=payload).status_code == 201
    assert client.post('/api/auth/register', json=payload).status_code == 409
    for change in ({'email': 'not-email'}, {'password': 'short'}, {'name': ' '}, {'role': 'admin'}):
        assert client.post('/api/auth/register', json=payload | change).status_code == 422


def test_login_and_profile(client, user):
    assert client.get('/api/auth/me', headers=user).json()['name'] == 'Siva'
    assert client.post('/api/auth/login', json={'email': 'siva@example.com', 'password': 'wrong'}).status_code == 401
    assert client.post('/api/auth/login', json={'email': 'missing@example.com', 'password': 'wrong'}).status_code == 401
    assert client.get('/api/auth/me').status_code == 401
    assert client.get('/api/auth/me', headers={'Authorization': 'Bearer broken'}).status_code == 401


def test_expired_and_forged_tokens_rejected(client):
    for secret, exp in [('test-only-secret', 1), ('wrong-secret', 9999999999)]:
        token = jwt.encode({'sub': '1', 'exp': exp}, secret, algorithm='HS256')
        assert client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'}).status_code == 401


def test_records_survive_app_restart(tmp_path):
    from backend.app import create_app
    from fastapi.testclient import TestClient
    path = tmp_path / 'persistent.sqlite3'
    payload = {'name': 'Persistent', 'email': 'persist@example.com', 'password': 'StrongPass123!'}
    with TestClient(create_app(path, secret='testing')) as c:
        assert c.post('/api/auth/register', json=payload).status_code == 201
    with TestClient(create_app(path, secret='testing')) as c:
        assert c.post('/api/auth/login', json=payload).status_code == 200
