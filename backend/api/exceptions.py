"""
backend/api/exceptions.py
=========================

Custom exceptions and exception handlers for CEREBRO-RED v2 API.
"""

from uuid import UUID
from fastapi import Request, status
from fastapi.responses import JSONResponse


class CerebroException(Exception):
    """Base exception for CEREBRO-RED."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ExperimentNotFoundException(CerebroException):
    """Exception raised when experiment is not found."""
    
    def __init__(self, experiment_id: UUID):
        super().__init__(f"Experiment {experiment_id} not found", 404)
        self.experiment_id = experiment_id


class ExperimentAlreadyRunningException(CerebroException):
    """Exception raised when experiment is already running."""
    
    def __init__(self, experiment_id: UUID):
        super().__init__(f"Experiment {experiment_id} is already running", 409)
        self.experiment_id = experiment_id


class InvalidConfigurationException(CerebroException):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str):
        super().__init__(f"Invalid configuration: {message}", 400)
        self.config_error = message


class VulnerabilityNotFoundException(CerebroException):
    """Exception raised when vulnerability is not found."""
    
    def __init__(self, vulnerability_id: UUID):
        super().__init__(f"Vulnerability {vulnerability_id} not found", 404)
        self.vulnerability_id = vulnerability_id


class LLMProviderException(CerebroException):
    """Exception raised when LLM provider fails."""
    
    def __init__(self, provider: str, message: str):
        super().__init__(f"LLM provider {provider} error: {message}", 503)
        self.provider = provider


async def cerebro_exception_handler(request: Request, exc: CerebroException) -> JSONResponse:
    """
    Handler for CerebroException.
    
    Returns consistent JSON error responses with CORS headers.
    """
    from fastapi.middleware.cors import CORSMiddleware
    
    # Get origin from request headers
    origin = request.headers.get("origin")
    
    # Create response with error details
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__,
            "path": str(request.url.path)
        }
    )
    
    # Add CORS headers if origin is present
    if origin:
        from utils.config import get_settings
        settings = get_settings()
        origins_str = settings.security.cors_origins or "http://localhost:3000,http://localhost:5173"
        allowed_origins = [o.strip() for o in origins_str.split(",") if o.strip()]
        # Add default origins
        default_origins = [
            "http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://localhost:9000",
            "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8000", "http://127.0.0.1:9000"
        ]
        allowed_origins.extend(default_origins)
        
        if origin in allowed_origins or "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for generic exceptions.
    
    Returns sanitized error responses (detailed in debug mode only) with CORS headers.
    """
    from utils.config import get_settings
    
    settings = get_settings()
    
    # Get origin from request headers
    origin = request.headers.get("origin")
    
    # Create response with error details
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "type": "InternalServerError",
            "path": str(request.url.path),
            "detail": str(exc) if settings.app.debug else "An unexpected error occurred"
        }
    )
    
    # Add CORS headers if origin is present
    if origin:
        origins_str = settings.security.cors_origins or "http://localhost:3000,http://localhost:5173"
        allowed_origins = [o.strip() for o in origins_str.split(",") if o.strip()]
        # Add default origins
        default_origins = [
            "http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://localhost:9000",
            "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8000", "http://127.0.0.1:9000"
        ]
        allowed_origins.extend(default_origins)
        
        if origin in allowed_origins or "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

