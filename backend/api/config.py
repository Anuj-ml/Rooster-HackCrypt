# backend/api/config.py

"""
Configuration management for the FastAPI application.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_TITLE: str = "Rooster-HackCrypt API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-Powered Adaptive Learning Engine API"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # File Upload Settings
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = ".pdf"
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    # Paths - relative to backend directory
    BACKEND_DIR: Path = Path(__file__).parent.parent.resolve()
    
    @property
    def temp_upload_dir(self) -> Path:
        path = self.BACKEND_DIR / "api" / "temp_uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def data_dir(self) -> Path:
        path = self.BACKEND_DIR / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def logs_dir(self) -> Path:
        path = self.BACKEND_DIR / "api" / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    # Temp file cleanup
    TEMP_FILE_MAX_AGE_HOURS: int = 1
    
    # Rate limiting (requests per minute)
    RATE_LIMIT_INGESTION: int = 10
    RATE_LIMIT_QUIZ: int = 30
    
    # LLM Settings (loaded from .env)
    GROQ_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
