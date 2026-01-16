# backend/api/main.py

"""
Rooster-HackCrypt FastAPI Application

Main entry point for the REST API server.
Provides endpoints for document ingestion, quiz generation, and session management.
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent.resolve()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv(backend_dir / ".env")

# Now import local modules (after path is set)
from api.config import settings
from api.middleware import setup_exception_handlers
from api.routers import (
    health_router,
    materials_router,
    ingestion_router,
    quiz_router
)
from api.services.file_handler import get_file_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # === STARTUP ===
    print(f"\n{'='*60}")
    print(f"🐓 ROOSTER-HACKCRYPT API")
    print(f"   Version: {settings.API_VERSION}")
    print(f"{'='*60}")
    
    # Ensure directories exist
    settings.temp_upload_dir
    settings.data_dir
    settings.logs_dir
    
    # Cleanup old temp files on startup
    file_handler = get_file_handler()
    cleaned = await file_handler.cleanup_old_files()
    if cleaned > 0:
        print(f"🧹 Cleaned up {cleaned} old temporary files")
    
    print(f"✓ Temp uploads: {settings.temp_upload_dir}")
    print(f"✓ Data directory: {settings.data_dir}")
    print(f"✓ CORS origins: {settings.cors_origins_list}")
    print(f"{'='*60}\n")
    
    yield  # Application runs here
    
    # === SHUTDOWN ===
    print("\n👋 Shutting down Rooster-HackCrypt API...")
    
    # Final cleanup of temp files
    await file_handler.cleanup_old_files()


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Setup global exception handlers
setup_exception_handlers(app)

# Register routers
app.include_router(health_router, prefix="/api")
app.include_router(materials_router, prefix="/api/v1")
app.include_router(ingestion_router, prefix="/api/v1")
app.include_router(quiz_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with basic info."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


# Development server entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
