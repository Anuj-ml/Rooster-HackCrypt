# backend/api/dependencies.py

"""
FastAPI dependency injection providers.
Centralized dependency management for all routes.
"""

from functools import lru_cache
from typing import Generator

from .services.file_handler import FileHandler, get_file_handler as _get_file_handler
from .services.orchestrator import (
    IngestionOrchestrator,
    QuizOrchestrator,
    get_ingestion_orchestrator as _get_ingestion_orchestrator,
    get_quiz_orchestrator as _get_quiz_orchestrator
)

# Knowledge base singleton
_knowledge_base = None


def get_knowledge_base():
    """
    Dependency that provides the KnowledgeBase instance.
    Lazily initializes on first request.
    """
    global _knowledge_base
    if _knowledge_base is None:
        from src.rag.ingestion_main import get_knowledge_base as _get_kb
        _knowledge_base = _get_kb()
    return _knowledge_base


def get_file_handler() -> FileHandler:
    """Dependency that provides the FileHandler instance."""
    return _get_file_handler()


def get_ingestion_orchestrator() -> IngestionOrchestrator:
    """Dependency that provides the IngestionOrchestrator instance."""
    return _get_ingestion_orchestrator()


def get_quiz_orchestrator() -> QuizOrchestrator:
    """Dependency that provides the QuizOrchestrator instance."""
    return _get_quiz_orchestrator()
