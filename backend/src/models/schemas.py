from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
# from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
import uuid

# --- Output Schemas for LLM ---
class PropositionList(BaseModel):
    """Schema for the decomposition LLM output."""
    propositions: List[str] = Field(
        description="A list of atomic, standalone facts derived from the text."
    )

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure exactly 4 options
        while len(self.options) < 4:
            self.options.append(f"[Option {len(self.options) + 1} - Invalid generation]")

class QuizOutput(BaseModel):
    questions: List[QuizQuestion]

# --- Doubt Solver Schemas ---
class DoubtInput(BaseModel):
    """Input schema for doubt solver feature."""
    question: str = Field(description="Student's question about the material")
    pdf_source_id: str = Field(description="PDF source to search for answer")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique session identifier")

class DoubtState(BaseModel):
    """State schema for doubt solver LangGraph workflow."""
    session_id: str
    pdf_source_id: str
    user_query: str
    retrieved_docs: List[Document] = []
    answer: str = ""
    simplification_level: str = "ELI5"  # Explain Like I'm 5
    
    class Config:
        arbitrary_types_allowed = True

# --- Smart Learning Schemas ---
class HintRequest(BaseModel):
    """Input schema for Socratic hint generation."""
    question: str = Field(description="The question the student is trying to answer")
    correct_answer: str = Field(description="The correct answer to the question")
    student_answer: Optional[str] = Field(None, description="The student's incorrect answer (if provided)")

class QuizResultItem(BaseModel):
    """Individual quiz result for session analysis."""
    question: str = Field(description="The quiz question")
    is_correct: bool = Field(description="Whether the student answered correctly")
    user_answer: str = Field(description="The student's answer")
    correct_answer: str = Field(description="The correct answer")

class AnalysisRequest(BaseModel):
    """Input schema for AI Sensei session analysis."""
    results: List[QuizResultItem] = Field(description="List of quiz results to analyze")


# --- Multiplayer Schemas ---
class CreateRoomRequest(BaseModel):
    """Input schema for creating a multiplayer room."""
    host_id: str = Field(description="User ID of the room host")
    topic: str = Field(default="default", description="Quiz topic")
    pdf_source_id: str = Field(description="Source material ID")
    num_questions: int = Field(default=5, ge=3, le=10, description="Number of questions (3-10)")


class JoinRoomRequest(BaseModel):
    """Input schema for joining a room."""
    room_code: str = Field(description="6-character room code")
    user_id: str = Field(description="User ID joining the room")


class SubmitAnswerRequest(BaseModel):
    """Input schema for submitting an answer in multiplayer."""
    room_code: str = Field(description="Room code")
    user_id: str = Field(description="User ID")
    question_index: int = Field(ge=0, description="Question index (0-based)")
    answer: str = Field(description="Player's answer")
    time_taken: float = Field(ge=0, description="Time taken in seconds")


# --- Study Group Schemas ---
class CreateGroupRequest(BaseModel):
    """Input schema for creating a study group."""
    name: str = Field(description="Group name", min_length=3, max_length=50)
    creator_id: str = Field(description="User ID of the creator")


class JoinGroupRequest(BaseModel):
    """Input schema for joining a study group."""
    group_id: str = Field(description="Group ID to join")
    user_id: str = Field(description="User ID joining")


class UploadGroupResourceRequest(BaseModel):
    """Input schema for uploading a resource to a group."""
    group_id: str = Field(description="Group ID")
    uploaded_by: str = Field(description="User ID uploading")
    title: str = Field(description="Resource title")


# --- Agent State Schema ---
class AgentState(BaseModel):
    """The shared state for the LangGraph workflow."""
    session_id: str
    pdf_source_id: str
    current_difficulty: str  # 'EASY', 'MEDIUM', 'HARD'
    topic: str
    retrieved_docs: List[Document] = []
    generated_quiz: Optional[QuizOutput] = None
    
    class Config:
        arbitrary_types_allowed = True