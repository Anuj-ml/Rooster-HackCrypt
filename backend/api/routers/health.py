# backend/api/routers/health.py

"""
Health check endpoints for monitoring and load balancer health probes.
"""

from fastapi import APIRouter, Depends
from ..models.responses import HealthCheckResponse, APIResponse
from ..config import settings
from ..dependencies import get_knowledge_base
import os

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=APIResponse[HealthCheckResponse],
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """
    Perform health check on all system components.
    
    Checks:
    - API is running
    - Knowledge base is accessible
    - LLM API key is configured
    """
    components = {}
    overall_status = "healthy"
    
    # Check GROQ API key
    if os.getenv("GROQ_API_KEY"):
        components["llm"] = "ok"
    else:
        components["llm"] = "missing_api_key"
        overall_status = "degraded"
    
    # Check data directories exist
    if settings.data_dir.exists():
        components["data_directory"] = "ok"
    else:
        components["data_directory"] = "missing"
        overall_status = "degraded"
    
    # Check temp upload directory
    if settings.temp_upload_dir.exists():
        components["temp_uploads"] = "ok"
    else:
        components["temp_uploads"] = "missing"
    
    # Basic component status
    components["api"] = "ok"
    
    return APIResponse(
        success=overall_status == "healthy",
        message=f"System status: {overall_status}",
        data=HealthCheckResponse(
            status=overall_status,
            components=components,
            version=settings.API_VERSION
        )
    )


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Check if the API is ready to serve requests"
)
async def readiness_check():
    """Simple readiness probe for Kubernetes/load balancers."""
    return {"status": "ready"}


@router.get(
    "/live", 
    summary="Liveness Check",
    description="Check if the API process is alive"
)
async def liveness_check():
    """Simple liveness probe for Kubernetes/load balancers."""
    return {"status": "alive"}
