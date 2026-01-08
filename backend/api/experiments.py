"""
backend/api/experiments.py
===========================

Experiment CRUD operations for CEREBRO-RED v2 API.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session, ExperimentRepository
from core.models import ExperimentConfig, ExperimentStatus
from core.database import ExperimentDB
from api.auth import verify_api_key
from api.exceptions import ExperimentNotFoundException
from api.responses import api_response

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class ExperimentResponse(BaseModel):
    """Experiment response with status and timestamps."""
    
    experiment_id: UUID
    name: str
    description: Optional[str]
    target_model_provider: str
    target_model_name: str
    attacker_model_provider: str
    attacker_model_name: str
    judge_model_provider: str
    judge_model_name: str
    initial_prompts: List[str]
    strategies: List[str]
    max_iterations: int
    max_concurrent_attacks: int
    success_threshold: float
    timeout_seconds: int
    status: str
    created_at: str
    metadata: dict
    
    @classmethod
    def from_db(cls, db_experiment: ExperimentDB) -> "ExperimentResponse":
        """Create response from database model."""
        # Convert experiment_metadata to dict (handle SQLAlchemy MetaData vs dict)
        metadata = db_experiment.experiment_metadata
        if metadata is None:
            metadata = {}
        elif not isinstance(metadata, dict):
            # If it's somehow not a dict, convert it
            metadata = dict(metadata) if hasattr(metadata, '__dict__') else {}
        
        return cls(
            experiment_id=db_experiment.experiment_id,
            name=db_experiment.name,
            description=db_experiment.description,
            target_model_provider=db_experiment.target_model_provider,
            target_model_name=db_experiment.target_model_name,
            attacker_model_provider=db_experiment.attacker_model_provider,
            attacker_model_name=db_experiment.attacker_model_name,
            judge_model_provider=db_experiment.judge_model_provider,
            judge_model_name=db_experiment.judge_model_name,
            initial_prompts=db_experiment.initial_prompts,
            strategies=db_experiment.strategies,
            max_iterations=db_experiment.max_iterations,
            max_concurrent_attacks=db_experiment.max_concurrent_attacks,
            success_threshold=db_experiment.success_threshold,
            timeout_seconds=db_experiment.timeout_seconds,
            status=db_experiment.status,
            created_at=db_experiment.created_at.isoformat(),
            metadata=metadata
        )


class ExperimentListResponse(BaseModel):
    """Paginated experiment list response."""
    
    items: List[ExperimentResponse]
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============================================================================
# Endpoints
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def create_experiment(
    experiment_config: ExperimentConfig,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new experiment with enhanced error logging.
    """
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    request_id = datetime.utcnow().isoformat()
    logger.info(f"[{request_id}] Creating experiment: {experiment_config.name}")
    
    try:
        # Validate prompts are not empty
        if not experiment_config.initial_prompts or not all(p.strip() for p in experiment_config.initial_prompts):
            logger.warning(f"[{request_id}] Validation failed: empty prompts")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="initial_prompts must contain at least one non-empty prompt"
            )
        
        # Validate strategies
        if not experiment_config.strategies:
            logger.warning(f"[{request_id}] Validation failed: no strategies")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="strategies must contain at least one strategy"
            )
        
        logger.debug(f"[{request_id}] Validation passed, creating in database")
        
        # Create experiment
        repo = ExperimentRepository(session)
        db_experiment = await repo.create(experiment_config)
        
        logger.debug(f"[{request_id}] Experiment created in DB, committing transaction")
        await session.commit()
        
        logger.info(f"[{request_id}] Experiment created successfully: {db_experiment.experiment_id}")
        
        return api_response(ExperimentResponse.from_db(db_experiment))
        
    except HTTPException as e:
        # Re-raise HTTP exceptions (validation errors)
        logger.warning(f"[{request_id}] HTTP exception: {e.status_code} - {e.detail}")
        await session.rollback()
        raise
        
    except Exception as e:
        # Log full exception details
        logger.error(
            f"[{request_id}] Unexpected error creating experiment",
            exc_info=True,
            extra={
                "experiment_name": experiment_config.name,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )
        await session.rollback()
        
        # Return detailed error in debug mode
        from utils.config import get_settings
        settings = get_settings()
        
        detail = str(e) if settings.app.debug else "Failed to create experiment. Check server logs."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("", dependencies=[Depends(verify_api_key)])
async def list_experiments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session)
):
    """
    List all experiments with pagination.
    """
    from sqlalchemy import select, func
    
    repo = ExperimentRepository(session)
    offset = (page - 1) * page_size
    
    experiments = await repo.list_all(limit=page_size, offset=offset)
    
    # Get total count using SQL count query
    count_stmt = select(func.count(ExperimentDB.experiment_id))
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0
    
    response = ExperimentListResponse(
        items=[ExperimentResponse.from_db(exp) for exp in experiments],
        total=total,
        page=page,
        page_size=page_size
    )
    return api_response(response)


@router.get("/{experiment_id}", dependencies=[Depends(verify_api_key)])
async def get_experiment(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get experiment details by ID.
    """
    repo = ExperimentRepository(session)
    experiment = await repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    return api_response(ExperimentResponse.from_db(experiment))


@router.put("/{experiment_id}", dependencies=[Depends(verify_api_key)])
async def update_experiment(
    experiment_id: UUID,
    status_update: Optional[str] = None,
    metadata: Optional[dict] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Update experiment (only status and metadata allowed).
    """
    repo = ExperimentRepository(session)
    experiment = await repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Update status if provided
    if status_update:
        if status_update not in [s.value for s in ExperimentStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_update}"
            )
        await repo.update_status(experiment_id, status_update)
    
    # Update metadata if provided
    if metadata is not None:
        experiment.experiment_metadata = {**(experiment.experiment_metadata or {}), **metadata}
        await session.flush()
    
    await session.commit()
    
    # Reload from database
    experiment = await repo.get_by_id(experiment_id)
    return api_response(ExperimentResponse.from_db(experiment))


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_api_key)])
async def delete_experiment(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an experiment.
    
    First cancels any running task, then deletes the experiment from database.
    """
    import asyncio
    from api.scans import _running_experiment_tasks
    
    # Cancel running task if exists
    task = _running_experiment_tasks.get(experiment_id)
    if task and not task.done():
        logger.info(f"[DELETE] Cancelling task for experiment {experiment_id} before deletion")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"[DELETE] Task for experiment {experiment_id} cancelled")
    
    repo = ExperimentRepository(session)
    success = await repo.delete(experiment_id)
    
    if not success:
        raise ExperimentNotFoundException(experiment_id)
    
    await session.commit()


@router.post("/{experiment_id}/repeat", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def repeat_experiment(
    experiment_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """
    Repeat (duplicate) an existing experiment with the same configuration.
    
    Creates a new experiment with:
    - Same configuration (models, prompts, strategies, etc.)
    - New experiment_id
    - Name appended with " (Repeat)" or timestamp
    - Status set to "pending"
    """
    from uuid import uuid4
    from datetime import datetime
    from core.models import LLMProvider, AttackStrategyType, ExperimentConfig
    
    repo = ExperimentRepository(session)
    original_experiment = await repo.get_by_id(experiment_id)
    
    if not original_experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Create new experiment config based on original
    new_name = f"{original_experiment.name} (Repeat)"
    
    # Convert database values to enums
    target_provider = LLMProvider(original_experiment.target_model_provider)
    attacker_provider = LLMProvider(original_experiment.attacker_model_provider)
    judge_provider = LLMProvider(original_experiment.judge_model_provider)
    strategies = [AttackStrategyType(s) for s in original_experiment.strategies]
    
    new_config = ExperimentConfig(
        experiment_id=uuid4(),
        name=new_name,
        description=original_experiment.description,
        target_model_provider=target_provider,
        target_model_name=original_experiment.target_model_name,
        attacker_model_provider=attacker_provider,
        attacker_model_name=original_experiment.attacker_model_name,
        judge_model_provider=judge_provider,
        judge_model_name=original_experiment.judge_model_name,
        initial_prompts=original_experiment.initial_prompts.copy(),
        strategies=strategies,
        max_iterations=original_experiment.max_iterations,
        max_concurrent_attacks=original_experiment.max_concurrent_attacks,
        success_threshold=original_experiment.success_threshold,
        timeout_seconds=original_experiment.timeout_seconds,
        metadata={
            **(original_experiment.experiment_metadata or {}),
            "repeated_from": str(experiment_id),
            "repeated_at": datetime.utcnow().isoformat()
        }
    )
    
    # Create the new experiment
    db_experiment = await repo.create(new_config)
    await session.commit()
    
    # Automatically start the experiment using the same pattern as start_scan
    from api.scans import _run_experiment_with_error_handling, get_orchestrator
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get orchestrator using dependency injection pattern
    orchestrator = await get_orchestrator(session)
    
    # Use BackgroundTasks (passed as dependency) instead of asyncio.create_task
    background_tasks.add_task(
        _run_experiment_with_error_handling,
        new_config,
        orchestrator
    )
    
    return api_response(ExperimentResponse.from_db(db_experiment))


@router.get("/{experiment_id}/iterations", dependencies=[Depends(verify_api_key)])
async def get_experiment_iterations(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get all iterations for an experiment with FULL details.
    
    Returns complete iteration data including:
    - Original and mutated prompts
    - Target response
    - Judge score and reasoning
    - Latency and metadata
    """
    from core.database import AttackIterationRepository
    
    # Verify experiment exists
    repo = ExperimentRepository(session)
    experiment = await repo.get_by_id(experiment_id)
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get iterations
    iteration_repo = AttackIterationRepository(session)
    iterations = await iteration_repo.get_by_experiment(experiment_id)
    
    return api_response({
        "experiment_id": str(experiment_id),
        "experiment_name": experiment.name,
        "experiment_status": experiment.status,
        "iterations": [
            {
                "iteration_id": str(it.iteration_id),
                "iteration_number": it.iteration_number,
                
                # IMPROVED: Explicit strategy serialization with validation
                "strategy_used": it.strategy_used,  # Raw string from DB
                "intended_strategy": it.intended_strategy if hasattr(it, 'intended_strategy') else None,  # NEW
                "strategy_fallback_occurred": getattr(it, 'strategy_fallback_occurred', False),  # NEW
                "fallback_reason": getattr(it, 'fallback_reason', None),  # NEW
                
                "success": it.success,
                "judge_score": it.judge_score,
                # FULL DETAILS - Prompts
                "original_prompt": it.original_prompt,
                "mutated_prompt": it.mutated_prompt,
                # FULL DETAILS - Response
                "target_response": it.target_response,
                # FULL DETAILS - Judge
                "judge_reasoning": it.judge_reasoning,
                # FULL DETAILS - Metadata
                "latency_ms": it.latency_ms,
                "timestamp": it.timestamp.isoformat() if it.timestamp else None,
                # Attacker feedback if available
                "attacker_feedback": it.attacker_feedback if hasattr(it, 'attacker_feedback') else None
            }
            for it in iterations
        ],
        "total": len(iterations)
    })


@router.get("/{experiment_id}/statistics", dependencies=[Depends(verify_api_key)])
async def get_experiment_statistics(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get experiment statistics.
    """
    from core.database import AttackIterationRepository, VulnerabilityRepository
    
    # Verify experiment exists
    repo = ExperimentRepository(session)
    experiment = await repo.get_by_id(experiment_id)
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get iterations
    iteration_repo = AttackIterationRepository(session)
    iterations = await iteration_repo.get_by_experiment(experiment_id)
    
    # Get vulnerabilities
    vuln_repo = VulnerabilityRepository(session)
    vulnerabilities = await vuln_repo.get_by_experiment(experiment_id)
    
    # Calculate statistics
    total_iterations = len(iterations)
    successful_iterations = [it for it in iterations if it.success]
    success_rate = len(successful_iterations) / total_iterations if total_iterations > 0 else 0.0
    
    # Strategy distribution with fallback tracking
    strategy_distribution = {}
    fallback_count = 0  # NEW
    
    for it in iterations:
        strategy = it.strategy_used
        strategy_distribution[strategy] = strategy_distribution.get(strategy, 0) + 1
        
        # NEW: Track fallbacks
        if hasattr(it, 'strategy_fallback_occurred') and it.strategy_fallback_occurred:
            fallback_count += 1
    
    severity_distribution = {
        "critical": len([v for v in vulnerabilities if v.severity == "critical"]),
        "high": len([v for v in vulnerabilities if v.severity == "high"]),
        "medium": len([v for v in vulnerabilities if v.severity == "medium"]),
        "low": len([v for v in vulnerabilities if v.severity == "low"])
    }
    
    return api_response({
        "experiment_id": str(experiment_id),
        "status": experiment.status,
        "total_iterations": total_iterations,
        "successful_iterations": len(successful_iterations),
        "success_rate": success_rate,
        "vulnerabilities_found": len(vulnerabilities),
        "strategy_distribution": strategy_distribution,
        "strategy_fallback_count": fallback_count,  # NEW
        "strategy_fallback_rate": fallback_count / total_iterations if total_iterations > 0 else 0.0,  # NEW
        "severity_distribution": severity_distribution,
        "created_at": experiment.created_at.isoformat()
    })

