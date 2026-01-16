"""
Flash-Note / Cheat-Sheet API Router

Provides endpoints for instant fact retrieval without LLM usage.
"""

import asyncio
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends

from ..dependencies import get_knowledge_base
from ..models.responses import APIResponse
from src.rag.storage import KnowledgeBase
from src.features.flash_note_generator import FlashNoteGenerator


router = APIRouter(prefix="/cheat-sheet", tags=["Flash Notes"])


async def get_flash_note_generator(kb: KnowledgeBase = Depends(get_knowledge_base)) -> FlashNoteGenerator:
    """Dependency injection for FlashNoteGenerator."""
    return FlashNoteGenerator(knowledge_base=kb)


@router.get("", response_model=APIResponse)
async def generate_cheat_sheet(
    topic: str = Query(..., description="Topic to generate facts about"),
    source_id: Optional[str] = Query(None, description="Optional PDF source ID to filter results"),
    num_facts: int = Query(20, ge=1, le=50, description="Number of facts to retrieve (1-50)"),
    generator: FlashNoteGenerator = Depends(get_flash_note_generator)
):
    """
    Generate a cheat sheet of atomic facts for a specific topic.
    
    **Zero LLM Cost** - Retrieves stored propositions directly from ChromaDB.
    
    - **topic**: The subject you want facts about (e.g., "Indian Economy", "Machine Learning")
    - **source_id**: Optional - filter facts from a specific material
    - **num_facts**: How many facts to retrieve (default: 20, max: 50)
    
    Returns a formatted list of bullet-pointed facts perfect for quick review.
    """
    try:
        # Run synchronous operation in thread pool
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            generator.generate_cheat_sheet,
            topic,
            source_id,
            num_facts
        )
        
        if result["fact_count"] == 0:
            return APIResponse(
                success=False,
                message=result.get("message", "No facts found"),
                data=result
            )
        
        return APIResponse(
            success=True,
            message=f"Generated cheat sheet with {result['fact_count']} facts",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate cheat sheet: {str(e)}"
        )


@router.get("/by-source/{source_id}", response_model=APIResponse)
async def generate_cheat_sheet_by_source(
    source_id: str,
    num_facts: int = Query(30, ge=1, le=50, description="Number of facts to retrieve"),
    generator: FlashNoteGenerator = Depends(get_flash_note_generator)
):
    """
    Generate a comprehensive cheat sheet from an entire material source.
    
    **Zero LLM Cost** - Retrieves random propositions from the entire document.
    
    - **source_id**: The material ID to generate facts from
    - **num_facts**: How many facts to retrieve (default: 30, max: 50)
    
    Perfect for getting a broad overview of uploaded materials.
    """
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            generator.generate_cheat_sheet_by_source,
            source_id,
            num_facts
        )
        
        if result["fact_count"] == 0:
            return APIResponse(
                success=False,
                message=f"No facts found for source '{source_id}'",
                data=result
            )
        
        return APIResponse(
            success=True,
            message=f"Generated cheat sheet with {result['fact_count']} facts from '{source_id}'",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate cheat sheet: {str(e)}"
        )
