#!/usr/bin/env python3
"""
Setup and run script for Supreme Cycle Store
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def run_server():
    """Run the FastAPI server"""
    print("🚀 Starting Supreme Cycle Store server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Try to import uvicorn first
        subprocess.check_call([sys.executable, "-c", "import uvicorn"])
        # Run the server
        subprocess.call([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except subprocess.CalledProcessError:
        print("❌ Failed to start server")
        print("💡 Try running: pip install uvicorn")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thank you for using Supreme Cycle Store!")

def main():
    """Main setup and run function"""
    print("🚲 Supreme Cycle Store Setup & Run Script")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Run server
    run_server()

if __name__ == "__main__":
    main()
