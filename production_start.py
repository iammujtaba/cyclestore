#!/usr/bin/env python3
"""
Production startup script for Supreme Cycle & Rickshaw Company
Handles production environment setup and starts the FastAPI application with Uvicorn
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", mode="a")
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main production startup function"""
    try:
        # Ensure we're in production mode
        os.environ.setdefault("ENVIRONMENT", "production")
        
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("Starting Supreme Cycle & Rickshaw Company application in production mode")
        
        # Import and start the application
        import uvicorn
        from app.main import app
        from app.config import settings
        
        # Get configuration from environment or defaults
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        workers = int(os.getenv("WORKERS", 4))
        
        logger.info(f"Starting server on {host}:{port} with {workers} workers")
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level="info",
            access_log=True,
            loop="auto",
            reload=False  # Never reload in production
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
