#!/usr/bin/env python3
"""
Start script for the Supreme Cycle and Rickshaw Company FastAPI application.
"""

import uvicorn
import os
import sys

def main():
    """Main function to start the FastAPI application."""
    # Add the current directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Start the uvicorn server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        reload_dirs=[current_dir]
    )

if __name__ == "__main__":
    main()
