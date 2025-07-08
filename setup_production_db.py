#!/usr/bin/env python3
"""
Production database setup script
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load production environment variables
from dotenv import load_dotenv
load_dotenv('.env.production')

from app.db.session import SessionLocal, engine
from app.models.product import Bicycle, Accessory
from app.models.user import User
from app.models.admin import Admin
from app.db.init_db import seed_database
from app.services.admin_auth_service import admin_auth_service
from app.config import settings

def setup_production_database():
    """Setup production database with initial data"""
    print("🗄️ Setting up production database...")
    
    # Create all tables
    from app.db.session import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Seed with initial data
    try:
        seed_database()
        print("✅ Database seeded with initial products")
    except Exception as e:
        print(f"⚠️ Database seeding: {e}")
    
    # Create default admin
    db = SessionLocal()
    try:
        admin_auth_service.create_default_admin(db)
        print("✅ Default admin user created")
    except Exception as e:
        print(f"⚠️ Admin creation: {e}")
    finally:
        db.close()
    
    print("🎉 Production database setup complete!")
    print(f"📍 Database location: {settings.DATABASE_URL}")
    print("\n👤 Default Admin Credentials:")
    print("   Email: admin@supremecycle.com")
    print("   Password: admin123")
    print("   URL: http://your-domain.com/admin")

if __name__ == "__main__":
    setup_production_database()
