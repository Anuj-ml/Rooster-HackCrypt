# backend/api/routers/materials.py

"""
Materials management endpoints.
List and manage indexed learning materials.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.responses import APIResponse, MaterialsListResponse
from ..dependencies import get_knowledge_base

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.get(
    "",
    response_model=APIResponse[MaterialsListResponse],
    summary="List All Materials",
    description="Get a list of all indexed learning materials (PDFs, YouTube videos, syllabi)"
)
async def list_materials(kb=Depends(get_knowledge_base)):
    """
    Retrieve all available material sources.
    
    Returns a list of source IDs that can be used for quiz generation.
    """
    try:
        sources = kb.get_all_pdf_sources()
        
        return APIResponse(
            success=True,
            message=f"Found {len(sources)} indexed materials",
            data=MaterialsListResponse(
                sources=sorted(sources),
                count=len(sources)
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve materials: {str(e)}"
        )


@router.get(
    "/{source_id}",
    response_model=APIResponse,
    summary="Get Material Details",
    description="Get details about a specific indexed material"
)
async def get_material_details(
    source_id: str,
    kb=Depends(get_knowledge_base)
):
    """
    Get information about a specific material source.
    
    Currently returns basic existence check.
    Future: add document count, creation date, etc.
    """
    try:
        sources = kb.get_all_pdf_sources()
        
        if source_id not in sources:
            raise HTTPException(
                status_code=404,
                detail=f"Material '{source_id}' not found"
            )
        
        # Count documents for this source
        doc_count = sum(
            1 for doc in kb.docstore.values()
            if doc.metadata.get("pdf_source_id") == source_id
        )
        
        return APIResponse(
            success=True,
            message=f"Material '{source_id}' found",
            data={
                "source_id": source_id,
                "document_count": doc_count,
                "exists": True
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get material details: {str(e)}"
        )


@router.delete(
    "/{source_id}",
    response_model=APIResponse,
    summary="Delete Material",
    description="Delete an indexed material (NOT IMPLEMENTED - placeholder)"
)
async def delete_material(source_id: str):
    """
    Delete a material source and all its indexed content.
    
    NOTE: This endpoint is a placeholder for future implementation.
    Deleting from ChromaDB requires careful handling.
    """
    raise HTTPException(
        status_code=501,
        detail="Material deletion not yet implemented"
    )
