"""
backend/api/demo.py
===================

Demo mode API endpoints serving mock experiment data.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from api.responses import api_response
from api.demo_data import get_demo_experiments, get_demo_experiment_by_id
from api.experiments import ExperimentResponse, ExperimentListResponse

router = APIRouter()


@router.get("/experiments", response_model=ExperimentListResponse)
async def list_demo_experiments():
    """
    List demo experiments (read-only mock data).

    Returns 3 pre-configured experiments with different statuses:
    - Running: OWASP Top 10 scan in progress
    - Failed: Translation attack with timeout error
    - Completed: RAG poisoning research with results
    """
    experiments_data = get_demo_experiments()

    # Convert raw dicts to ExperimentResponse instances
    experiments = [ExperimentResponse(**exp) for exp in experiments_data]

    response = ExperimentListResponse(
        items=experiments,
        total=len(experiments),
        page=1,
        page_size=20
    )

    return api_response(response)


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_demo_experiment(experiment_id: UUID):
    """
    Get demo experiment details by ID.

    Args:
        experiment_id: Demo experiment UUID

    Returns:
        Demo experiment data

    Raises:
        404: If experiment ID not found in demo data
    """
    experiment_data = get_demo_experiment_by_id(str(experiment_id))

    if not experiment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo experiment {experiment_id} not found"
        )

    # Convert raw dict to ExperimentResponse instance
    experiment = ExperimentResponse(**experiment_data)

    return api_response(experiment)


# ============================================================================
# Write Operation Blocking (Demo Mode Read-Only Enforcement)
# ============================================================================

def _demo_mode_blocked_response(request: Request, action: str) -> JSONResponse:
    """
    Generate 403 response for blocked demo mode operations.

    Includes:
    - Helpful error message with deployment instructions
    - Link to Quick Start documentation
    - CORS headers for cross-origin requests
    """
    from utils.config import get_settings

    origin = request.headers.get("origin")
    settings = get_settings()

    response = JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": f"Demo mode is read-only. Cannot {action}.",
            "type": "DemoModeRestriction",
            "path": str(request.url.path),
            "detail": "Deploy CEREBRO-RED v2 locally to create and run experiments.",
            "documentation": "https://github.com/your-org/cerebro-red-v2#quick-start",
            "quick_start_guide": "/QUICK_START.md"
        }
    )

    # Add CORS headers (same pattern as backend/api/exceptions.py)
    if origin:
        origins_str = settings.security.cors_origins or "http://localhost:3000,http://localhost:5173"
        allowed_origins = [o.strip() for o in origins_str.split(",") if o.strip()]
        default_origins = [
            "http://localhost:3000", "http://localhost:5173",
            "http://localhost:8000", "http://localhost:9000",
            "http://127.0.0.1:3000", "http://127.0.0.1:5173",
            "http://127.0.0.1:8000", "http://127.0.0.1:9000"
        ]
        allowed_origins.extend(default_origins)

        if origin in allowed_origins or "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"

    return response


@router.post("/experiments", status_code=status.HTTP_403_FORBIDDEN)
async def create_demo_experiment(request: Request):
    """Block experiment creation in demo mode."""
    return _demo_mode_blocked_response(request, "create experiments")


@router.put("/experiments/{experiment_id}", status_code=status.HTTP_403_FORBIDDEN)
async def update_demo_experiment(experiment_id: str, request: Request):
    """Block experiment updates in demo mode."""
    return _demo_mode_blocked_response(request, "update experiments")


@router.delete("/experiments/{experiment_id}", status_code=status.HTTP_403_FORBIDDEN)
async def delete_demo_experiment(experiment_id: str, request: Request):
    """Block experiment deletion in demo mode."""
    return _demo_mode_blocked_response(request, "delete experiments")


@router.post("/experiments/{experiment_id}/start", status_code=status.HTTP_403_FORBIDDEN)
async def start_demo_scan(experiment_id: str, request: Request):
    """Block scan execution in demo mode."""
    return _demo_mode_blocked_response(request, "start scans")
