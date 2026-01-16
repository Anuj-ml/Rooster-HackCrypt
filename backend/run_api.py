#!/usr/bin/env python
# backend/run_api.py

"""
Convenience script to run the FastAPI server.
Run from the backend directory: python run_api.py
"""

import os
import sys
from pathlib import Path

# Ensure we're running from the right directory
backend_dir = Path(__file__).parent.resolve()
os.chdir(backend_dir)

# Add backend to path
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    # Load environment
    load_dotenv(backend_dir / ".env")
    
    # Import settings after path is configured
    from api.config import settings
    
    print(f"\n🚀 Starting Rooster-HackCrypt API Server...")
    print(f"   Backend dir: {backend_dir}")
    print(f"   Host: {settings.API_HOST}")
    print(f"   Port: {settings.API_PORT}")
    print(f"   Docs: http://localhost:{settings.API_PORT}/docs\n")
    
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
