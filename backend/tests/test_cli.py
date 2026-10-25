import pytest
from backend import cli
from backend.app import create_app


def test_seed_is_persistent_and_idempotent(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'seed.db'
    monkeypatch.setenv('DATABASE_PATH', str(path))
    monkeypatch.setattr('sys.argv', ['cli', 'seed'])
    cli.main()
    cli.main()
    with create_app(path).state.db.connect() as conn:
        assert conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0] == 8
    assert 'skipped' in capsys.readouterr().out


def test_create_admin_uses_hidden_prompt(tmp_path, monkeypatch):
    path = tmp_path / 'admin.db'
    monkeypatch.setenv('DATABASE_PATH', str(path))
    monkeypatch.setattr('sys.argv', ['cli', 'create-admin', '--email', 'admin@example.com'])
    monkeypatch.setattr(cli.getpass, 'getpass', lambda _: 'StrongPass123!')
    cli.main()
    with create_app(path).state.db.connect() as conn:
        assert conn.execute('SELECT role FROM users').fetchone()[0] == 'admin'
    with pytest.raises(SystemExit):
        cli.main()  # Duplicate email must fail, never silently replace an account.


def test_admin_password_confirmation_and_validation(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'validation.db'))
    monkeypatch.setattr('sys.argv', ['cli', 'create-admin', '--email', 'admin@example.com'])
    passwords = iter(['first', 'second'])
    monkeypatch.setattr(cli.getpass, 'getpass', lambda _: next(passwords))
    with pytest.raises(SystemExit):
        cli.main()
    monkeypatch.setattr(cli.getpass, 'getpass', lambda _: 'weak')
    with pytest.raises(SystemExit):
        cli.main()
