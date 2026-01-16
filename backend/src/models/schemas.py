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