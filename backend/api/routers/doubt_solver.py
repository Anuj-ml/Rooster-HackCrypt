"""
Doubt Solver API Router

Provides endpoints for answering student questions with ELI5 explanations.
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends

from ..dependencies import get_knowledge_base, get_llm
from ..models.responses import APIResponse
from src.models.schemas import DoubtInput
from src.features.doubt_solver import DoubtSolverAgent
from src.rag.storage import KnowledgeBase


router = APIRouter(prefix="/solve-doubt", tags=["Doubt Solver"])


# Dependency injection for DoubtSolverAgent
_doubt_agent_instance = None

async def get_doubt_solver_agent(
    kb: KnowledgeBase = Depends(get_knowledge_base),
    llm = Depends(get_llm)
) -> DoubtSolverAgent:
    """Dependency injection for DoubtSolverAgent with singleton pattern."""
    global _doubt_agent_instance
    
    if _doubt_agent_instance is None:
        _doubt_agent_instance = DoubtSolverAgent(llm=llm, knowledge_base=kb)
        print("✓ DoubtSolverAgent initialized")
    
    return _doubt_agent_instance


@router.post("", response_model=APIResponse)
async def solve_doubt(
    input_data: DoubtInput,
    agent: DoubtSolverAgent = Depends(get_doubt_solver_agent)
):
    """
    Solve a student's doubt with an ELI5 (Explain Like I'm 5) explanation.
    
    **How it works:**
    1. Retrieves relevant context from the specified material (pdf_source_id)
    2. Uses LLM to generate a simplified, conversational explanation
    3. Strictly grounded in the uploaded material - no hallucinations
    
    **Request Body:**
    - **question**: The student's question about the material
    - **pdf_source_id**: Which material to search for the answer
    - **session_id**: Optional - auto-generated if not provided
    
    **Response:**
    - **answer**: Simplified explanation in conversational language
    - **context_found**: Whether relevant information was found in the material
    - **question**: The original question (for reference)
    - **source_id**: The material that was searched
    
    **Use Cases:**
    - Quick clarification of confusing concepts
    - Breaking down complex topics into simple terms
    - Getting real-world analogies for abstract ideas
    - Studying with a friendly AI tutor
    """
    try:
        # Run synchronous agent in thread pool to avoid blocking
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            agent.solve_doubt,
            input_data
        )
        
        if not result.get("context_found"):
            return APIResponse(
                success=True,
                message="No relevant context found in the material",
                data=result
            )
        
        return APIResponse(
            success=True,
            message="Doubt solved successfully",
            data=result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to solve doubt: {str(e)}"
        )


@router.get("/sources", response_model=APIResponse)
async def list_available_sources(kb: KnowledgeBase = Depends(get_knowledge_base)):
    """
    List all available materials that can be used for doubt solving.
    
    Returns the same materials that are available for quiz generation.
    """
    try:
        sources = kb.get_all_pdf_sources()
        
        return APIResponse(
            success=True,
            message=f"Found {len(sources)} available materials",
            data={
                "sources": sources,
                "count": len(sources)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sources: {str(e)}"
        )
