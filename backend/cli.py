"""Explicit administrative account creation and optional sample inventory."""
import argparse
import getpass
import sqlite3
from uuid import uuid4
from backend.app import create_app
from backend.security import hash_password

SAMPLE = [
    ('Tata', 'Nexon EV', 'SUV', 1749000, 5, 2026, 'Electric', 'Teal'),
    ('Hyundai', 'Creta', 'SUV', 1599000, 3, 2026, 'Diesel', 'White'),
    ('Honda', 'City', 'Sedan', 1249000, 4, 2026, 'Petrol', 'Silver'),
    ('Maruti Suzuki', 'Swift', 'Hatchback', 799000, 8, 2026, 'Petrol', 'Red'),
    ('Mahindra', 'Thar', 'SUV', 1699000, 2, 2026, 'Diesel', 'Black'),
    ('Toyota', 'Innova Hycross', 'MPV', 2599000, 0, 2026, 'Hybrid', 'Blue'),
    ('Kia', 'Seltos', 'SUV', 1849000, 4, 2026, 'Petrol', 'Teal'),
    ('Volkswagen', 'Virtus', 'Sedan', 1649000, 1, 2026, 'Petrol', 'Red'),
]


def main():
    parser = argparse.ArgumentParser(description='Manage local Torque accounts and sample inventory')
    sub = parser.add_subparsers(dest='command', required=True)
    admin = sub.add_parser('create-admin')
    admin.add_argument('--email', required=True)
    admin.add_argument('--name', default='Administrator')
    sub.add_parser('seed')
    args = parser.parse_args()
    app = create_app()
    if args.command == 'create-admin':
        from backend.schemas import Register
        password = getpass.getpass('Choose admin password (minimum 10 characters): ')
        if password != getpass.getpass('Confirm password: '):
            parser.error('Passwords do not match')
        try:
            body = Register(name=args.name, email=args.email, password=password)
            with app.state.db.connect() as conn:
                conn.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)',
                             (body.name, body.email, hash_password(body.password), 'admin'))
        except (ValueError, sqlite3.IntegrityError) as exc:
            parser.error(str(exc))
        print('Administrator account created. Sign in with your chosen credentials.')
    else:
        with app.state.db.connect() as conn:
            if conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]:
                print('Inventory is not empty; sample seed skipped.')
                return
            for make, model, category, price, quantity, year, fuel, color in SAMPLE:
                conn.execute('INSERT INTO vehicles(id,make,model,category,price_cents,quantity,year,fuel,color) VALUES(?,?,?,?,?,?,?,?,?)',
                             (str(uuid4()), make, model, category, price * 100, quantity, year, fuel, color))
        print('Added 8 fictional sample listings. Prices are demonstration data, not market quotes.')


if __name__ == '__main__':
    main()
