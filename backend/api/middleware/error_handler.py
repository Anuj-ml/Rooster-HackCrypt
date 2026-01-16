# backend/api/middleware/error_handler.py

"""
Global exception handling middleware.
Provides consistent error responses across all endpoints.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime
import traceback


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    Returns a clean 422 response with field-level error details.
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body' prefix
        errors.append({
            "field": field or "request",
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "error": "Invalid request data",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    Returns a clean 500 response without exposing internal details.
    """
    # Log the full error for debugging
    print(f"[ERROR] Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError exceptions (often from business logic validation).
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "Bad request",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def key_error_handler(request: Request, exc: KeyError):
    """
    Handle KeyError exceptions (often missing resources).
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "message": "Resource not found",
            "error": f"Missing key: {str(exc)}",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(KeyError, key_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
