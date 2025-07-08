from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import os
import logging

from app.config import settings
from app.db.session import get_db, engine, Base
from app.models.product import Bicycle, Accessory, ProductImage
from app.models.user import User, UserSession
from app.models.admin import Admin, AdminSession
from app.api.routes import router as api_router
from app.routes.admin import router as admin_router
from app.services.auth_service import auth_service
from app.services.admin_auth_service import admin_auth_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        from app.db.init_db import seed_database
        seed_database()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        # Continue startup even if seeding fails
    
    # Create default admin user
    try:
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            admin_auth_service.create_default_admin(db)
            logger.info("Default admin created/verified successfully")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Admin creation failed: {e}")
    
    yield
    # Shutdown (if needed)

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add security middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware for development
if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(api_router)
app.include_router(admin_router)

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
