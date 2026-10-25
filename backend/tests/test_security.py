import pytest
from backend.security import hash_password, verify_password
from backend.app import load_secret


def test_password_salts_and_invalid_hashes():
    a, b = hash_password('StrongPass123!'), hash_password('StrongPass123!')
    assert a != b
    assert verify_password('StrongPass123!', a)
    assert not verify_password('wrong', a)
    assert not verify_password('anything', 'broken')
    assert not verify_password('anything', 'other$123$456')


def test_secret_is_persistent_and_strong(tmp_path, monkeypatch):
    monkeypatch.delenv('JWT_SECRET', raising=False)
    path = tmp_path / 'data' / 'db.sqlite3'
    secret = load_secret(path)
    assert len(secret) >= 32
    assert load_secret(path) == secret
    monkeypatch.setenv('JWT_SECRET', 'weak')
    with pytest.raises(RuntimeError):
        load_secret(path)
    monkeypatch.setenv('JWT_SECRET', 'strong-external-secret-with-over-32-characters')
    assert load_secret(path) == 'strong-external-secret-with-over-32-characters'


def test_deleted_account_token_is_rejected(client, user, app):
    with app.state.db.connect() as conn:
        conn.execute('DELETE FROM users')
    assert client.get('/api/auth/me', headers=user).status_code == 401


def test_health_and_sort_validation(client, user):
    assert client.get('/api/health').json() == {'status': 'ok'}
    assert client.get('/api/vehicles?sort=unsafe', headers=user).status_code == 422
    assert client.get('/api/vehicles?in_stock=true', headers=user).json() == []
