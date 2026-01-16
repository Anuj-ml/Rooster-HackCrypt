# backend/api/models/responses.py

"""
Pydantic models for API responses.
Provides consistent response structure across all endpoints.
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(default="", description="Human-readable message")
    data: Optional[T] = Field(default=None, description="Response payload")
    error: Optional[str] = Field(default=None, description="Error details if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IngestionResult(BaseModel):
    """Result of a document ingestion operation."""
    source_id: str
    material_type: str
    num_documents: int
    num_propositions: int


class MaterialSource(BaseModel):
    """Information about an indexed material source."""
    source_id: str
    # Future: add metadata like created_at, document_count, etc.


class MaterialsListResponse(BaseModel):
    """Response containing list of available materials."""
    sources: List[str]
    count: int


class QuizQuestionResponse(BaseModel):
    """A single quiz question."""
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    """Response containing generated quiz questions."""
    session_id: str
    difficulty: str
    questions: List[QuizQuestionResponse]
    question_count: int


class SessionInfo(BaseModel):
    """Information about a learning session."""
    session_id: str
    user_id: str
    source_id: str
    topic: str
    mode: str
    current_difficulty: str
    created_at: Optional[datetime] = None


class SessionCreatedResponse(BaseModel):
    """Response when a new session is created."""
    session_id: str
    mode: str
    initial_difficulty: str
    topic: str
    source_id: str


class SessionStatsResponse(BaseModel):
    """Detailed statistics for a session."""
    session_id: str
    mode: str
    current_difficulty: str
    total_questions: int
    correct_answers: int
    mastery_score: float
    streak: int
    difficulty_history: List[str] = []


class SessionListResponse(BaseModel):
    """Response containing list of active sessions."""
    sessions: List[SessionInfo]
    count: int


class QuizSubmitResponse(BaseModel):
    """Response after submitting quiz answers."""
    session_id: str
    correct_count: int
    total_count: int
    score_percentage: float
    new_difficulty: str
    mastery_score: float
    streak: int
    difficulty_changed: bool
    feedback_message: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    components: Dict[str, str]
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str
    message: str
    field: Optional[str] = None
