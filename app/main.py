from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from app.config import settings
from app.db.session import get_db, engine, Base
from app.models.product import Bicycle, Accessory, ProductImage
from app.models.user import User, UserSession
from app.models.admin import Admin, AdminSession
from app.api.routes import router as api_router
from app.routes.admin import router as admin_router
from app.services.auth_service import auth_service
from app.services.admin_auth_service import admin_auth_service

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Include API routes
app.include_router(api_router)
app.include_router(admin_router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    """Seed database with sample data on startup"""
    try:
        from app.db.init_db import seed_database
        seed_database()
        print("Database seeded successfully")
    except Exception as e:
        print(f"Database seeding failed: {e}")
        # Continue startup even if seeding fails
    
    # Create default admin user
    try:
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            admin_auth_service.create_default_admin(db)
            print("Default admin created/verified successfully")
        finally:
            db.close()
    except Exception as e:
        print(f"Admin creation failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
