#!/usr/bin/env python3
"""
Production deployment script for the Supreme Cycle and Rickshaw Company FastAPI application.
"""

import uvicorn
import os
import sys

def main():
    """Main function to start the FastAPI application in production mode."""
    # Add the current directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Start the uvicorn server with production settings
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        workers=int(os.getenv("WORKERS", 4)),
        reload=False,
        access_log=True
    )

if __name__ == "__main__":
    main()
