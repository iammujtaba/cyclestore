from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import os
import logging

from app.config import settings
from app.api.routes import router as api_router
from app.routes.admin import router as admin_router
from app.services.admin_auth_service import admin_auth_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    title="Supreme Cycle & Rickshaw Company API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url
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
        "service": "SCRC",
        "version": "1.0.0"
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
