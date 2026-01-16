# backend/api/models/requests.py

"""
Pydantic models for API request validation.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class DifficultyLevel(str, Enum):
    """Valid difficulty levels."""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class YouTubeIngestRequest(BaseModel):
    """Request model for YouTube video ingestion."""
    url: str = Field(..., description="YouTube video URL")
    source_id: Optional[str] = Field(
        None, 
        max_length=100,
        description="Custom source identifier (auto-generated if not provided)"
    )
    
    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        if not v:
            raise ValueError("URL cannot be empty")
        if 'youtube.com' not in v and 'youtu.be' not in v:
            raise ValueError("Must be a valid YouTube URL")
        return v.strip()


class SyllabusIngestRequest(BaseModel):
    """Request model for syllabus content generation."""
    topic: str = Field(
        ..., 
        min_length=3, 
        max_length=200,
        description="Topic to generate content for"
    )
    source_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Custom source identifier (auto-generated if not provided)"
    )
    
    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        return v.strip()


class AdaptiveSessionRequest(BaseModel):
    """Request model for creating an adaptive learning session."""
    user_id: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Unique user identifier"
    )
    source_id: str = Field(
        ..., 
        min_length=1,
        description="Source material identifier"
    )
    topic: str = Field(
        default="default",
        description="Topic for quiz generation ('default' for entire document)"
    )
    initial_difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.EASY,
        description="Starting difficulty level"
    )


class GrindSessionRequest(BaseModel):
    """Request model for creating a grind mode session."""
    user_id: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Unique user identifier"
    )
    source_id: str = Field(
        ..., 
        min_length=1,
        description="Source material identifier"
    )
    topic: str = Field(
        default="default",
        description="Topic for quiz generation ('default' for entire document)"
    )
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.EASY,
        description="Difficulty level"
    )
    dynamic_difficulty: bool = Field(
        default=True,
        description="Whether difficulty adjusts slowly based on performance"
    )


class QuizGenerateRequest(BaseModel):
    """Request model for generating a quiz batch."""
    num_questions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of questions to generate"
    )


class QuizSubmitRequest(BaseModel):
    """Request model for submitting quiz answers."""
    answers: List[bool] = Field(
        ...,
        min_length=1,
        description="List of boolean results (True=correct, False=incorrect)"
    )
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v: List[bool]) -> List[bool]:
        if len(v) > 20:
            raise ValueError("Maximum 20 answers allowed")
        return v
