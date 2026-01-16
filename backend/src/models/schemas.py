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