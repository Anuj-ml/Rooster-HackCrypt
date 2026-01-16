# backend/api/routers/ingestion.py

"""
Document ingestion endpoints.
Handle PDF uploads, YouTube URL processing, and syllabus generation.
"""

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import Optional

from ..models.requests import YouTubeIngestRequest, SyllabusIngestRequest
from ..models.responses import APIResponse, IngestionResult
from ..config import settings
from ..services.file_handler import FileHandler
from ..services.orchestrator import IngestionOrchestrator
from ..dependencies import get_ingestion_orchestrator, get_file_handler

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post(
    "/pdf",
    response_model=APIResponse[IngestionResult],
    summary="Upload and Ingest PDF",
    description="Upload a PDF file for processing and indexing into the knowledge base"
)
async def ingest_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file to upload"),
    source_id: Optional[str] = Form(None, description="Custom source identifier"),
    orchestrator: IngestionOrchestrator = Depends(get_ingestion_orchestrator),
    file_handler: FileHandler = Depends(get_file_handler)
):
    """
    Upload and process a PDF document.
    
    The PDF will be:
    1. Saved temporarily
    2. Parsed and split into chunks
    3. Decomposed into propositions (if API limits allow)
    4. Indexed into the vector database
    5. Temporary file deleted
    
    Args:
        file: PDF file (multipart/form-data)
        source_id: Optional custom identifier (defaults to filename without extension)
    
    Returns:
        Ingestion result with document and proposition counts
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file_ext}'. Allowed: {settings.allowed_extensions_list}"
        )
    
    # Check file size (read content to verify)
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Reset file position for saving
    await file.seek(0)
    
    # Generate source_id if not provided
    if not source_id:
        source_id = Path(file.filename).stem
        # Sanitize source_id
        source_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in source_id)
    
    temp_path = None
    try:
        # Save file temporarily
        temp_path = await file_handler.save_upload(file, content)
        
        # Process the PDF
        result = await orchestrator.ingest_pdf(
            file_path=str(temp_path),
            source_id=source_id
        )
        
        # Schedule cleanup in background
        background_tasks.add_task(file_handler.cleanup_file, temp_path)
        
        return APIResponse(
            success=True,
            message=f"PDF '{file.filename}' ingested successfully",
            data=IngestionResult(
                source_id=result["source_id"],
                material_type="PDF",
                num_documents=result["num_documents"],
                num_propositions=result["num_propositions"]
            )
        )
        
    except Exception as e:
        # Cleanup on error
        if temp_path and temp_path.exists():
            background_tasks.add_task(file_handler.cleanup_file, temp_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )


@router.post(
    "/youtube",
    response_model=APIResponse[IngestionResult],
    summary="Ingest YouTube Video",
    description="Fetch and index transcript from a YouTube video"
)
async def ingest_youtube(
    request: YouTubeIngestRequest,
    orchestrator: IngestionOrchestrator = Depends(get_ingestion_orchestrator)
):
    """
    Process a YouTube video URL.
    
    The video transcript will be:
    1. Fetched using youtube-transcript-api
    2. Split into chunks
    3. Indexed into the vector database
    
    Args:
        request: YouTube URL and optional source_id
    
    Returns:
        Ingestion result with document and proposition counts
    
    Note:
        - Video must have captions enabled
        - Some videos may be region-restricted or age-gated
    """
    try:
        result = await orchestrator.ingest_youtube(
            url=request.url,
            source_id=request.source_id
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch YouTube transcript. Ensure the video has captions enabled."
            )
        
        return APIResponse(
            success=True,
            message="YouTube video transcript ingested successfully",
            data=IngestionResult(
                source_id=result["source_id"],
                material_type="YOUTUBE",
                num_documents=result["num_documents"],
                num_propositions=result["num_propositions"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process YouTube video: {str(e)}"
        )


@router.post(
    "/syllabus",
    response_model=APIResponse[IngestionResult],
    summary="Generate Syllabus Content",
    description="Generate educational content for a topic using LLM and index it"
)
async def ingest_syllabus(
    request: SyllabusIngestRequest,
    orchestrator: IngestionOrchestrator = Depends(get_ingestion_orchestrator)
):
    """
    Generate and index syllabus content for a topic.
    
    The LLM will:
    1. Generate comprehensive educational content (~1500-2000 words)
    2. Split into chunks
    3. Index into the vector database
    
    Args:
        request: Topic name and optional source_id
    
    Returns:
        Ingestion result with document and proposition counts
    
    Note:
        This operation may take 30-60 seconds depending on LLM response time.
    """
    try:
        result = await orchestrator.ingest_syllabus(
            topic=request.topic,
            source_id=request.source_id
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate syllabus content"
            )
        
        return APIResponse(
            success=True,
            message=f"Syllabus content for '{request.topic}' generated and indexed",
            data=IngestionResult(
                source_id=result["source_id"],
                material_type="SYLLABUS",
                num_documents=result["num_documents"],
                num_propositions=result["num_propositions"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate syllabus: {str(e)}"
        )
