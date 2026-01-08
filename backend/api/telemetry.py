"""
backend/api/telemetry.py
=========================

Telemetry and metrics endpoints for CEREBRO-RED v2 API.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session, ExperimentRepository
from core.telemetry import get_audit_logger
from api.auth import verify_api_key
from api.exceptions import ExperimentNotFoundException
from api.responses import api_response

router = APIRouter()


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/stats", dependencies=[Depends(verify_api_key)])
async def get_telemetry_stats(
    session: AsyncSession = Depends(get_session)
):
    """
    Get aggregate telemetry statistics.
    """
    audit_logger = get_audit_logger()
    stats = audit_logger.get_stats(experiment_id=None)
    
    return api_response({
        "total_events": stats.get("total_events", 0),
        "attack_attempts": stats.get("attack_attempts", 0),
        "judge_evaluations": stats.get("judge_evaluations", 0),
        "successful_attacks": stats.get("successful_attacks", 0),
        "mutations": stats.get("mutations", 0),
        "errors": stats.get("errors", 0),
        "total_latency_ms": stats.get("total_latency_ms", 0),
        "total_tokens": stats.get("total_tokens", 0),
        "avg_latency_ms": (
            stats.get("total_latency_ms", 0) / stats.get("total_events", 1)
            if stats.get("total_events", 0) > 0 else 0
        )
    })


@router.get("/stats/{experiment_id}", dependencies=[Depends(verify_api_key)])
async def get_experiment_telemetry_stats(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get experiment-specific telemetry statistics.
    """
    # Verify experiment exists
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    audit_logger = get_audit_logger()
    stats = audit_logger.get_stats(experiment_id=experiment_id)
    
    return api_response({
        "experiment_id": str(experiment_id),
        "total_events": stats.get("total_events", 0),
        "attack_attempts": stats.get("attack_attempts", 0),
        "judge_evaluations": stats.get("judge_evaluations", 0),
        "successful_attacks": stats.get("successful_attacks", 0),
        "mutations": stats.get("mutations", 0),
        "errors": stats.get("errors", 0),
        "total_latency_ms": stats.get("total_latency_ms", 0),
        "total_tokens": stats.get("total_tokens", 0),
        "avg_latency_ms": (
            stats.get("total_latency_ms", 0) / stats.get("total_events", 1)
            if stats.get("total_events", 0) > 0 else 0
        )
    })


@router.get("/logs/{experiment_id}", dependencies=[Depends(verify_api_key)])
async def get_experiment_logs(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get audit logs for a specific experiment.
    
    Returns JSONL-formatted log entries.
    """
    # Verify experiment exists
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Read logs from audit logger
    audit_logger = get_audit_logger()
    import json
    from pathlib import Path
    
    log_entries = []
    log_path = audit_logger.log_path
    
    # Read all log files
    for log_file in sorted(log_path.glob("audit_*.jsonl")):
        try:
            with open(log_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            # Filter by experiment_id
                            if entry.get("experiment_id") == str(experiment_id):
                                log_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except Exception:
            continue
    
    return api_response({
        "experiment_id": str(experiment_id),
        "total_entries": len(log_entries),
        "entries": log_entries
    })


# Note: /metrics endpoint is defined in main.py at root level (no auth required)

