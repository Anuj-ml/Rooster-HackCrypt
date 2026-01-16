"""
Study Groups API Router

Provides endpoints for collaborative learning groups with shared resources.
"""

import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict, Any

from ..models.responses import APIResponse
from ..dependencies import get_ingestion_orchestrator
from ..services.orchestrator import IngestionOrchestrator
from src.models.schemas import CreateGroupRequest, JoinGroupRequest
from src.features.multiplayer.state_manager import get_global_state, GlobalState


router = APIRouter(prefix="/groups", tags=["Study Groups"])


# Dependency injection
async def get_state() -> GlobalState:
    """Dependency for GlobalState."""
    return get_global_state()


@router.post("/create")
async def create_study_group(
    request: CreateGroupRequest,
    state: GlobalState = Depends(get_state)
) -> APIResponse:
    """
    Create a new study group.
    
    **Constraints:**
    - Maximum 2 students per group
    - Creator is automatically added as first member
    
    **Example Request:**
    ```json
    {
        "name": "Biology Study Group",
        "creator_id": "user_123"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "group_id": "grp_abc123",
            "name": "Biology Study Group",
            "members": ["user_123"],
            "max_members": 2
        }
    }
    ```
    """
    try:
        # Generate unique group ID
        group_id = f"grp_{uuid.uuid4().hex[:8]}"
        
        # Create group
        group_data = state.create_study_group(
            group_id=group_id,
            name=request.name,
            creator_id=request.creator_id
        )
        
        return APIResponse(
            success=True,
            message="Study group created successfully",
            data=group_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create group: {str(e)}")


@router.post("/join")
async def join_study_group(
    request: JoinGroupRequest,
    state: GlobalState = Depends(get_state)
) -> APIResponse:
    """
    Join an existing study group.
    
    **Requirements:**
    - Group must exist
    - Group must not be full (max 2 members)
    
    **Example Request:**
    ```json
    {
        "group_id": "grp_abc123",
        "user_id": "user_456"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "group_id": "grp_abc123",
            "members": ["user_123", "user_456"]
        }
    }
    ```
    """
    try:
        # Check if group exists
        group = state.get_study_group(request.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        
        # Add member
        success = state.add_group_member(request.group_id, request.user_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to join group (group may be full or user already member)"
            )
        
        # Get updated group
        updated_group = state.get_study_group(request.group_id)
        
        return APIResponse(
            success=True,
            message="Joined study group successfully",
            data=updated_group
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join group: {str(e)}")


@router.get("/{group_id}")
async def get_study_group(
    group_id: str,
    state: GlobalState = Depends(get_state)
) -> APIResponse:
    """
    Get study group details.
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "group_id": "grp_abc123",
            "name": "Biology Study Group",
            "members": ["user_123", "user_456"],
            "resources": ["bio_textbook_001"],
            "created_at": "2026-01-17T10:30:00Z"
        }
    }
    ```
    """
    try:
        group = state.get_study_group(group_id)
        
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        
        return APIResponse(
            success=True,
            data=group
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_study_groups(
    state: GlobalState = Depends(get_state)
) -> APIResponse:
    """
    List all study groups.
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "groups": [
                {
                    "group_id": "grp_abc123",
                    "name": "Biology Study Group",
                    "member_count": 2
                }
            ],
            "total": 1
        }
    }
    ```
    """
    try:
        groups = state.list_study_groups()
        
        # Simplify response
        simplified = [
            {
                "group_id": g["group_id"],
                "name": g["name"],
                "member_count": len(g["members"]),
                "max_members": g["max_members"],
                "has_space": len(g["members"]) < g["max_members"]
            }
            for g in groups
        ]
        
        return APIResponse(
            success=True,
            data={
                "groups": simplified,
                "total": len(simplified)
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{group_id}/upload")
async def upload_group_resource(
    group_id: str,
    file: UploadFile = File(...),
    uploaded_by: str = Form(...),
    title: str = Form(None),
    state: GlobalState = Depends(get_state),
    ingestion: IngestionOrchestrator = Depends(get_ingestion_orchestrator)
) -> APIResponse:
    """
    Upload a PDF resource to a study group.
    
    **Flow:**
    1. Accepts file upload
    2. Ingests PDF into knowledge base
    3. Stores pdf_source_id in group resources
    4. All group members can access this resource
    
    **Form Data:**
    - `file`: PDF file (multipart/form-data)
    - `uploaded_by`: User ID uploading (form field)
    - `title`: Optional resource title (form field)
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "pdf_source_id": "bio_textbook_001",
            "title": "Chapter 5 - Photosynthesis",
            "group_id": "grp_abc123",
            "uploaded_by": "user_123"
        }
    }
    ```
    """
    try:
        # Check if group exists
        group = state.get_study_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        
        # Check if user is a member
        if uploaded_by not in group["members"]:
            raise HTTPException(
                status_code=403,
                detail="Only group members can upload resources"
            )
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Use title from form or filename
        resource_title = title or file.filename
        
        # Generate source ID
        source_id = f"{group_id}_{uuid.uuid4().hex[:8]}"
        
        # Save file temporarily
        temp_dir = "api/temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{source_id}_{file.filename}")
        
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        try:
            # Ingest PDF using orchestrator
            result = await ingestion.ingest_pdf(
                file_path=temp_path,
                source_id=source_id
            )
            
            if not result["success"]:
                raise ValueError(result.get("error", "Ingestion failed"))
            
            # Add resource to group
            state.add_group_resource(group_id, source_id)
            
            # Store resource metadata
            state.add_resource(
                pdf_source_id=source_id,
                title=resource_title,
                uploaded_by=uploaded_by,
                group_id=group_id
            )
            
            return APIResponse(
                success=True,
                message="Resource uploaded and indexed successfully",
                data={
                    "pdf_source_id": source_id,
                    "title": resource_title,
                    "group_id": group_id,
                    "uploaded_by": uploaded_by,
                    "ingestion_result": result
                }
            )
        
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload resource: {str(e)}")


@router.get("/{group_id}/resources")
async def list_group_resources(
    group_id: str,
    state: GlobalState = Depends(get_state)
) -> APIResponse:
    """
    List all resources uploaded to a study group.
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "resources": [
                {
                    "pdf_source_id": "bio_textbook_001",
                    "title": "Chapter 5 - Photosynthesis",
                    "uploaded_by": "user_123",
                    "uploaded_at": "2026-01-17T10:30:00Z"
                }
            ],
            "total": 1
        }
    }
    ```
    """
    try:
        # Check if group exists
        group = state.get_study_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        
        # Get resources
        resources = state.list_group_resources(group_id)
        
        return APIResponse(
            success=True,
            data={
                "resources": resources,
                "total": len(resources)
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
