"""
backend/api/vulnerabilities.py
===============================

Vulnerability management endpoints for CEREBRO-RED v2 API.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_session, VulnerabilityRepository, ExperimentRepository
from core.models import VulnerabilitySeverity, AttackStrategyType
from core.database import VulnerabilityDB
from api.auth import verify_api_key
from api.exceptions import VulnerabilityNotFoundException, ExperimentNotFoundException
from api.responses import api_response

router = APIRouter()


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/statistics", dependencies=[Depends(verify_api_key)])
async def get_vulnerability_statistics(
    session: AsyncSession = Depends(get_session)
):
    """
    Get aggregated vulnerability statistics.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Statistics endpoint called")
    from sqlalchemy import select, func
    
    # Count by severity
    severity_counts = {}
    for severity in VulnerabilitySeverity:
        stmt = select(func.count(VulnerabilityDB.vulnerability_id)).where(
            VulnerabilityDB.severity == severity.value
        )
        result = await session.execute(stmt)
        severity_counts[severity.value] = result.scalar() or 0
    
    # Count by strategy
    strategy_counts = {}
    for strategy in AttackStrategyType:
        stmt = select(func.count(VulnerabilityDB.vulnerability_id)).where(
            VulnerabilityDB.attack_strategy == strategy.value
        )
        result = await session.execute(stmt)
        strategy_counts[strategy.value] = result.scalar() or 0
    
    # Total count
    total_stmt = select(func.count(VulnerabilityDB.vulnerability_id))
    total_result = await session.execute(total_stmt)
    total = total_result.scalar() or 0
    
    return api_response({
        "total_vulnerabilities": total,
        "by_severity": severity_counts,
        "by_strategy": strategy_counts
    })


@router.get("", dependencies=[Depends(verify_api_key)])
async def list_vulnerabilities(
    severity: Optional[VulnerabilitySeverity] = Query(None, description="Filter by severity"),
    experiment_id: Optional[UUID] = Query(None, description="Filter by experiment"),
    strategy: Optional[AttackStrategyType] = Query(None, description="Filter by attack strategy"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    session: AsyncSession = Depends(get_session)
):
    """
    List all vulnerabilities with optional filtering.
    """
    vuln_repo = VulnerabilityRepository(session)
    
    # Build query
    stmt = select(VulnerabilityDB)
    
    if severity:
        stmt = stmt.where(VulnerabilityDB.severity == severity.value)
    
    if experiment_id:
        stmt = stmt.where(VulnerabilityDB.experiment_id == experiment_id)
    
    if strategy:
        stmt = stmt.where(VulnerabilityDB.attack_strategy == strategy.value)
    
    stmt = stmt.order_by(VulnerabilityDB.discovered_at.desc()).limit(limit).offset(offset)
    
    result = await session.execute(stmt)
    vulnerabilities = list(result.scalars().all())
    
    return api_response({
        "vulnerabilities": [
            {
                "vulnerability_id": str(v.vulnerability_id),
                "experiment_id": str(v.experiment_id),
                "severity": v.severity,
                "title": v.title,
                "description": v.description,
                "attack_strategy": v.attack_strategy,
                "iteration_number": v.iteration_number,
                "judge_score": v.judge_score,
                "discovered_at": v.discovered_at.isoformat() if v.discovered_at else None
            }
            for v in vulnerabilities
        ],
        "total": len(vulnerabilities),
        "limit": limit,
        "offset": offset
    })


@router.get("/{vulnerability_id}", dependencies=[Depends(verify_api_key)])
async def get_vulnerability(
    vulnerability_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get detailed vulnerability information.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Get vulnerability endpoint called: {vulnerability_id}")
    from sqlalchemy import select
    
    stmt = select(VulnerabilityDB).where(VulnerabilityDB.vulnerability_id == vulnerability_id)
    result = await session.execute(stmt)
    vulnerability = result.scalar_one_or_none()
    
    if not vulnerability:
        raise VulnerabilityNotFoundException(vulnerability_id)
    
    return api_response({
        "vulnerability_id": str(vulnerability.vulnerability_id),
        "experiment_id": str(vulnerability.experiment_id),
        "severity": vulnerability.severity,
        "title": vulnerability.title,
        "description": vulnerability.description,
        "successful_prompt": vulnerability.successful_prompt,
        "target_response": vulnerability.target_response,
        "attack_strategy": vulnerability.attack_strategy,
        "iteration_number": vulnerability.iteration_number,
        "judge_score": vulnerability.judge_score,
        "reproducible": vulnerability.reproducible,
        "cve_references": vulnerability.cve_references or [],
        "mitigation_suggestions": vulnerability.mitigation_suggestions or [],
        "discovered_at": vulnerability.discovered_at.isoformat() if vulnerability.discovered_at else None,
        "metadata": vulnerability.experiment_metadata or {}
    })


@router.get("/by-severity/{severity}", dependencies=[Depends(verify_api_key)])
async def get_vulnerabilities_by_severity(
    severity: VulnerabilitySeverity,
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """
    Get vulnerabilities filtered by severity level.
    """
    vuln_repo = VulnerabilityRepository(session)
    vulnerabilities = await vuln_repo.get_by_severity(severity.value, limit)
    
    return api_response({
        "vulnerabilities": [
            {
                "vulnerability_id": str(v.vulnerability_id),
                "experiment_id": str(v.experiment_id),
                "severity": v.severity,
                "title": v.title,
                "attack_strategy": v.attack_strategy,
                "judge_score": v.judge_score,
                "discovered_at": v.discovered_at.isoformat() if v.discovered_at else None
            }
            for v in vulnerabilities
        ],
        "total": len(vulnerabilities),
        "severity": severity.value
    })


@router.get("/by-experiment/{experiment_id}", dependencies=[Depends(verify_api_key)])
async def get_vulnerabilities_by_experiment(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get all vulnerabilities for a specific experiment.
    """
    # Verify experiment exists
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get vulnerabilities
    vuln_repo = VulnerabilityRepository(session)
    vulnerabilities = await vuln_repo.get_by_experiment(experiment_id)
    
    return api_response({
        "experiment_id": str(experiment_id),
        "vulnerabilities": [
            {
                "vulnerability_id": str(v.vulnerability_id),
                "severity": v.severity,
                "title": v.title,
                "description": v.description,
                "attack_strategy": v.attack_strategy,
                "iteration_number": v.iteration_number,
                "judge_score": v.judge_score,
                "discovered_at": v.discovered_at.isoformat() if v.discovered_at else None
            }
            for v in vulnerabilities
        ],
        "total": len(vulnerabilities)
    })

