#!/usr/bin/env python3
"""
Production-ready database initialization script
This script is designed to run in Docker containers and production environments
"""
import os
import sys
import time
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configure logging
def setup_logging():
    """Setup logging with proper error handling"""
    log_handlers = [logging.StreamHandler(sys.stdout)]
    
    # Try to add file logging if possible
    try:
        if os.path.exists('logs'):
            log_handlers.append(logging.FileHandler('logs/db_init.log', mode='a'))
    except (PermissionError, OSError):
        pass  # Continue with just console logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=log_handlers
    )

setup_logging()
logger = logging.getLogger(__name__)

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv('.env.production')
load_dotenv('.env')

def wait_for_database(max_retries=30, retry_delay=5):
    """Wait for database to become available (useful for Docker)"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment")
        return False
    
    logger.info(f"Waiting for database to become available...")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("Database is ready!")
                return True
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Database connection failed after all retries")
                return False
    
    return False

def initialize_database():
    """Initialize database tables and data"""
    logger.info("Initializing database...")
    
    try:
        # Import models to ensure they're registered
        from app.db.session import Base, engine
        from app.models.product import Bicycle, Accessory, ProductImage
        from app.models.user import User
        from app.models.admin import Admin, AdminSession
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create admin user
        create_admin_user()
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def create_admin_user():
    """Create default admin user if not exists"""
    logger.info("Setting up admin user...")
    
    try:
        from app.db.session import SessionLocal
        from app.models.admin import Admin
        
        db = SessionLocal()
        
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.username == "superuser").first()
        if existing_admin:
            logger.info("Admin user 'superuser' already exists")
            db.close()
            return
        
        # Get admin credentials from environment
        admin_username = os.getenv("ADMIN_USERNAME", "superuser")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # Create admin user
        admin_user = Admin(
            username=admin_username,
            hashed_password=Admin.hash_password(admin_password),
            full_name="Super Administrator",
            email="admin@supremecycle.in",
            is_super_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        logger.info(f"Admin user '{admin_username}' created successfully")
        if admin_password == "admin123":
            logger.warning("Using default admin password - change it after first login!")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise

def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    # Wait for database to become available
    if not wait_for_database():
        logger.error("Database not available, exiting")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        logger.error("Database initialization failed, exiting")
        sys.exit(1)
    
    logger.info("Database initialization completed successfully!")

if __name__ == "__main__":
    main()
