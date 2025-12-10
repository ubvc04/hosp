"""
Database Initialization Script for Hospital Portal
Creates database tables, generates RSA keys, and creates admin user only (no sample data)
"""

import os
import sys
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Patient, Visit, Bill, Report
from crypto_utils import get_crypto

def init_database(create_admin=True):
    """Initialize the database with tables and admin user only (no sample data)"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Hospital Portal - Database Initialization")
        print("=" * 60)
        
        # Create all tables
        print("\n[1/3] Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Initialize crypto manager (generates RSA keys if needed)
        print("\n[2/3] Initializing RSA-4096 encryption...")
        crypto = get_crypto()
        print("✓ RSA-4096 keys ready")
        
        if not create_admin:
            print("\n✓ Database initialized (admin creation skipped)")
            return
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='amulyachowdary1@gmail.com').first()
        if existing_admin:
            print("\n[!] Admin user already exists.")
            print("    To reset, use the admin dashboard reset feature or delete hospital.db")
            return
        
        # Create admin user only
        print("\n[3/3] Creating admin user...")
        admin = User(
            email='amulyachowdary1@gmail.com',
            password_hash=generate_password_hash('amulya1234'),
            first_name='Amulya',
            last_name='Chowdary',
            phone='+1-555-0100',
            role='ADMIN',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        
        print("✓ Admin user created")
        print("    Email: amulyachowdary1@gmail.com")
        print("    Password: amulya1234")
        
        print("\n" + "=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        print("\nThe database is clean - no sample patient data added.")
        print("Use the admin dashboard to add patients, visits, bills, and reports.")
        print("\nRun the application:")
        print("    python app.py")
        print("\nThen login at: http://127.0.0.1:5000")


def reset_database():
    """Reset database - drop all tables and recreate with admin only"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Hospital Portal - Database Reset")
        print("=" * 60)
        
        print("\n[1/2] Dropping all tables...")
        db.drop_all()
        print("✓ All tables dropped")
        
        print("\n[2/2] Recreating database...")
        
    # Re-run init
    init_database()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Hospital Portal Database')
    parser.add_argument('--reset', action='store_true', help='Reset database (drops all data)')
    parser.add_argument('--no-admin', action='store_true', help='Skip admin user creation')
    
    args = parser.parse_args()
    
    if args.reset:
        confirm = input("WARNING: This will delete ALL data. Type 'RESET' to confirm: ")
        if confirm == 'RESET':
            reset_database()
        else:
            print("Reset cancelled.")
    else:
        init_database(create_admin=not args.no_admin)
