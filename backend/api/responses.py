"""
backend/api/responses.py
========================

Helper functions for consistent API response formatting.
"""

from typing import Any, Dict, TypeVar
from fastapi.responses import JSONResponse

T = TypeVar('T')


def api_response(data: T) -> Dict[str, Any]:
    """
    Wrap API response data in consistent format.
    
    All backend endpoints should use this to ensure consistent
    response structure matching frontend ApiResponse<T> type.
    
    Args:
        data: The response payload
        
    Returns:
        Dictionary with 'data' key containing the payload
    """
    return {"data": data}


def api_error_response(
    error: str,
    error_type: str = "ApiError",
    path: str = "",
    detail: str = ""
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error: Error message
        error_type: Type of error
        path: API path where error occurred
        detail: Additional error details
        
    Returns:
        Dictionary with error information
    """
    return {
        "error": error,
        "type": error_type,
        "path": path,
        "detail": detail
    }

