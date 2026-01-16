# API Routers
from .health import router as health_router
from .materials import router as materials_router
from .ingestion import router as ingestion_router
from .quiz import router as quiz_router
from .flashnotes import router as flashnotes_router
from .doubt_solver import router as doubt_solver_router
from .smart_learning import router as smart_learning_router

__all__ = [
    "health_router",
    "materials_router", 
    "ingestion_router",
    "quiz_router",
    "flashnotes_router",
    "doubt_solver_router",
    "smart_learning_router"
]
