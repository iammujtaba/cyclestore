#!/usr/bin/env python3
"""
Production startup script for Supreme Cycle & Rickshaw Company
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load production environment variables
from dotenv import load_dotenv
load_dotenv('.env.production')

# Import app after loading environment
from app.main import app
from app.config import settings

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("app/static/images/products", exist_ok=True)
    os.makedirs("app/static/images/accessories", exist_ok=True)
    os.makedirs("app/static/images/thumbnails", exist_ok=True)
    
    print(f"🚀 Starting Supreme Cycle v1.0.0.0")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🗄️ Database: {settings.DATABASE_URL}")
    
    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🏠 Server: {host}:{port}")
    
    # Run with uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        access_log=True,
        reload=False
    )
