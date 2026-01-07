"""
backend/api/scans.py
====================

Scan execution and control endpoints for CEREBRO-RED v2 API.
"""

import asyncio
import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session, AsyncSessionLocal, ExperimentRepository, AttackIterationRepository, VulnerabilityRepository, JudgeScoreRepository
from core.models import ExperimentConfig, ExperimentStatus, AttackStrategyType
from core.orchestrator import RedTeamOrchestrator
from core.mutator import PromptMutator
from core.judge import SecurityJudge
from core.telemetry import get_audit_logger
from utils.llm_client import get_llm_client, LLMClient
from api.auth import verify_api_key
from api.exceptions import ExperimentNotFoundException, ExperimentAlreadyRunningException
from api.responses import api_response

router = APIRouter()
logger = logging.getLogger(__name__)
logger.debug('[DEBUG TEST] This should appear')

# Keep references to background tasks to prevent garbage collection
# background_tasks_set = set()  # Not needed with FastAPI BackgroundTasks


# ============================================================================
# Helper Functions
# ============================================================================

async def _run_experiment_with_error_handling(
    config: ExperimentConfig,
    orchestrator: RedTeamOrchestrator
):
    """
    Wrapper to run experiment with comprehensive error handling.
    
    Updates experiment status to FAILED if any exception occurs.
    Logs full traceback for debugging.
    """
    import traceback
    logger.info(f"[DIAG-TASK] WRAPPER CALLED for {config.experiment_id}")
    logger.info(f"[DIAG-WRAPPER] Experiment: {config.name}")
    logger.info(f"[DIAG-WRAPPER] About to call orchestrator.run_experiment()")
    
    try:
        await orchestrator.run_experiment(config)
        logger.info(f"[DIAG-WRAPPER] run_experiment completed successfully for {config.experiment_id}")
    except Exception as e:
        logger.error(f"[DIAG-WRAPPER] ========== EXPERIMENT FAILED ==========")
        logger.error(f"[DIAG-WRAPPER] Experiment ID: {config.experiment_id}")
        logger.error(f"[DIAG-WRAPPER] Experiment Name: {config.name}")
        logger.error(f"[DIAG-WRAPPER] Exception Type: {type(e).__name__}")
        logger.error(f"[DIAG-WRAPPER] Exception Message: {str(e)}")
        logger.error(f"[DIAG-WRAPPER] Exception Args: {e.args}")
        logger.error(f"[DIAG-WRAPPER] Full Traceback:")
        logger.error(f"\n{traceback.format_exc()}")
        logger.error(f"[DIAG-WRAPPER] ========================================")
        
        # Log to telemetry for analysis
        try:
            audit_logger = get_audit_logger()
            audit_logger.log_error(
                experiment_id=config.experiment_id,
                error_type=type(e).__name__,
                error_message=str(e),
                metadata={
                    "traceback": traceback.format_exc(),
                    "experiment_name": config.name,
                    "initial_prompts_count": len(config.initial_prompts),
                    "strategies_count": len(config.strategies) if config.strategies else 0
                }
            )
        except Exception as log_error:
            logger.warning(f"[DIAG-WRAPPER] Failed to log error to telemetry: {log_error}")
        
        # Update experiment status to FAILED
        async with AsyncSessionLocal() as error_session:
            error_repo = ExperimentRepository(error_session)
            await error_repo.update_status(config.experiment_id, ExperimentStatus.FAILED.value)
            await error_session.commit()


async def _run_batch_experiments_concurrently(
    experiments: List[ExperimentConfig],
    orchestrator: RedTeamOrchestrator
):
    """
    Run multiple experiments concurrently using asyncio.create_task.
    
    Each experiment runs independently with its own error handling wrapper.
    This ensures true parallelism for batch scans.
    """
    logger.info(f"[DIAG-BATCH] Starting concurrent execution of {len(experiments)} experiments")
    
    # Create concurrent tasks for each experiment
    tasks = []
    for experiment_config in experiments:
        logger.info(f"[DIAG-BATCH] Creating task for experiment {experiment_config.experiment_id}")
        task = asyncio.create_task(
            _run_experiment_with_error_handling(experiment_config, orchestrator)
        )
        tasks.append(task)
    
    logger.info(f"[DIAG-BATCH] All {len(tasks)} tasks created, waiting for completion")
    
    # Wait for all tasks to complete (each has its own error handling)
    await asyncio.gather(*tasks, return_exceptions=True)
    
    logger.info(f"[DIAG-BATCH] All {len(experiments)} experiments completed")


# ============================================================================
# Request/Response Models
# ============================================================================

class ScanStartRequest(BaseModel):
    """Request to start a new scan."""
    
    experiment_config: ExperimentConfig


class BatchScanRequest(BaseModel):
    """Request to start batch scans."""
    
    experiments: List[ExperimentConfig]


class ScanStatusResponse(BaseModel):
    """Scan status response."""
    
    experiment_id: UUID
    status: str
    current_iteration: int
    total_iterations: int
    progress_percent: float
    elapsed_time_seconds: float
    estimated_remaining_seconds: Optional[float] = None


# ============================================================================
# Dependency Injection
# ============================================================================

async def get_orchestrator(session: AsyncSession = Depends(get_session)) -> RedTeamOrchestrator:
    """
    Dependency injection for RedTeamOrchestrator.
    
    Initializes all required dependencies (Mutator, Judge, LLM Clients, etc.)
    and creates orchestrator instance.
    """
    from uuid import uuid4
    
    # Initialize LLM clients
    llm_client = get_llm_client()
    target_llm_client = get_llm_client()  # Same client, different role
    
    # Initialize audit logger
    audit_logger = get_audit_logger()
    
    # Initialize mutator
    mutator = PromptMutator(
        llm_client=llm_client,
        audit_logger=audit_logger,
        experiment_id=uuid4()  # Will be set per experiment
    )
    
    # Initialize judge
    judge = SecurityJudge(
        llm_client=llm_client,
        audit_logger=audit_logger,
        experiment_id=uuid4()  # Will be set per experiment
    )
    
    # Initialize repositories
    experiment_repo = ExperimentRepository(session)
    iteration_repo = AttackIterationRepository(session)
    vulnerability_repo = VulnerabilityRepository(session)
    judge_score_repo = JudgeScoreRepository(session)
    
    # Create orchestrator
    return RedTeamOrchestrator(
        mutator=mutator,
        judge=judge,
        target_llm_client=target_llm_client,
        audit_logger=audit_logger,
        experiment_repo=experiment_repo,
        iteration_repo=iteration_repo,
        vulnerability_repo=vulnerability_repo,
        judge_score_repo=judge_score_repo
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/start", dependencies=[Depends(verify_api_key)])
async def start_scan(
    request: ScanStartRequest,
    background_tasks: BackgroundTasks,
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator),
    session: AsyncSession = Depends(get_session)
):
    """
    Start a new scan (experiment execution).
    
    Runs experiment in background and returns immediately with experiment_id.
    Use WebSocket endpoint or status endpoint to track progress.
    """
    experiment_config = request.experiment_config
    experiment_id = experiment_config.experiment_id
    
    # CRITICAL: Validate and convert strategies from strings to enums if needed
    if experiment_config.strategies:
        logger.info(f"[start_scan] Strategies type: {type(experiment_config.strategies)}")
        logger.info(f"[start_scan] Strategies: {experiment_config.strategies}")
        if experiment_config.strategies and isinstance(experiment_config.strategies[0], str):
            logger.warning(f"[start_scan] Strategies are strings, converting to AttackStrategyType enums")
            experiment_config.strategies = [AttackStrategyType(s) for s in experiment_config.strategies]
            logger.info(f"[start_scan] Converted strategies: {[s.value for s in experiment_config.strategies]}")
        elif experiment_config.strategies and isinstance(experiment_config.strategies[0], AttackStrategyType):
            logger.info(f"[start_scan] Strategies are already AttackStrategyType enums")
        logger.info(f"[start_scan] First strategy type: {type(experiment_config.strategies[0]) if experiment_config.strategies else 'empty'}")
    
    # Check if experiment already exists and is running
    experiment_repo = ExperimentRepository(session)
    existing = await experiment_repo.get_by_id(experiment_id)
    
    if existing:
        if existing.status == ExperimentStatus.RUNNING.value:
            raise ExperimentAlreadyRunningException(experiment_id)
    
    logger.info(f"[DIAG] ========== START_SCAN ENDPOINT CALLED ==========")
    logger.info(f"[DIAG] Experiment ID: {experiment_id}")
    try:
        logger.info(f"[DIAG] Experiment Name: {experiment_config.name}")
        logger.info(f"[DIAG] Initial Prompts Count: {len(experiment_config.initial_prompts)}")
        logger.info(f"[DIAG] Max Iterations: {experiment_config.max_iterations}")
        logger.info(f"[DIAG] Strategies: {[s.value if hasattr(s, 'value') else str(s) for s in experiment_config.strategies]}")
    except Exception as log_err:
        logger.error(f"[DIAG] Error logging experiment config: {type(log_err).__name__}: {str(log_err)}")
        import traceback
        logger.error(f"[DIAG] Traceback: {traceback.format_exc()}")
    
    # Use FastAPI's BackgroundTasks (handles lifecycle automatically)
    logger.info(f"[DIAG-START] About to add task to BackgroundTasks for experiment {experiment_id}")
    logger.info(f"[DIAG-START] Orchestrator type: {type(orchestrator)}")
    
    # Log event loop state before task creation
    import asyncio
    loop = asyncio.get_event_loop()
    logger.info(f"[DIAG] Event loop before task creation: {loop}")
    logger.info(f"[DIAG] Event loop running: {loop.is_running()}")
    logger.info(f"[DIAG] Event loop closed: {loop.is_closed()}")
    logger.info(f"[DIAG] All tasks count before: {len(asyncio.all_tasks())}")
    
    background_tasks.add_task(
        _run_experiment_with_error_handling,
        experiment_config,
        orchestrator
    )
    
    # Log event loop state after task creation
    logger.info(f"[DIAG] Task added to BackgroundTasks successfully")
    logger.info(f"[DIAG] Event loop after task creation: {loop}")
    logger.info(f"[DIAG] Event loop running: {loop.is_running()}")
    logger.info(f"[DIAG] Event loop closed: {loop.is_closed()}")
    logger.info(f"[DIAG] All tasks count after: {len(asyncio.all_tasks())}")
    logger.info(f"[DIAG-START] Experiment {experiment_id} scheduled for execution")
    
    return api_response({
        "experiment_id": experiment_id,
        "status": "started",
        "message": "Experiment started in background. Use /api/scan/status/{experiment_id} to track progress."
    })


# IMPORTANT: More specific routes (pause, cancel, resume) must come BEFORE general routes (status)
# FastAPI matches routes in order, so specific paths must be defined first

@router.post("/{experiment_id}/pause", dependencies=[Depends(verify_api_key)])
async def pause_scan(
    experiment_id: UUID,
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator),
    session: AsyncSession = Depends(get_session)
):
    """
    Pause a running scan.
    """
    # Verify experiment exists
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Pause experiment
    await orchestrator.pause_experiment(experiment_id)
    
    return api_response({
        "experiment_id": experiment_id,
        "status": "paused",
        "message": "Experiment paused successfully"
    })


@router.post("/{experiment_id}/resume", dependencies=[Depends(verify_api_key)])
async def resume_scan(
    experiment_id: UUID,
    background_tasks: BackgroundTasks,
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator),
    session: AsyncSession = Depends(get_session)
):
    """
    Resume a paused scan.
    """
    # Verify experiment exists
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    if experiment.status != ExperimentStatus.PAUSED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Experiment is not paused (current status: {experiment.status})"
        )
    
    # Resume experiment
    await orchestrator.resume_experiment(experiment_id)
    
    # Note: In a real implementation, we would need to restart the experiment loop
    # For now, we just update the status
    return api_response({
        "experiment_id": experiment_id,
        "status": "running",
        "message": "Experiment resumed"
    })


@router.post("/{experiment_id}/cancel", dependencies=[Depends(verify_api_key)])
async def cancel_scan(
    experiment_id: UUID,
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator),
    session: AsyncSession = Depends(get_session)
):
    """
    Cancel a running scan.
    """
    # Verify experiment exists
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Cancel experiment (this already updates status to FAILED in the orchestrator)
    await orchestrator.cancel_experiment(experiment_id)
    
    return api_response({
        "experiment_id": experiment_id,
        "status": "failed",  # Use FAILED status (no CANCELLED in enum)
        "message": "Experiment cancelled successfully"
    })


@router.get("/status/{experiment_id}", dependencies=[Depends(verify_api_key)])
async def get_scan_status(
    experiment_id: UUID,
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator),
    session: AsyncSession = Depends(get_session)
):
    """
    Get current scan status and progress.
    """
    # Get experiment from database
    experiment_repo = ExperimentRepository(session)
    experiment = await experiment_repo.get_by_id(experiment_id)
    
    if not experiment:
        raise ExperimentNotFoundException(experiment_id)
    
    # Get current iteration
    iteration_repo = AttackIterationRepository(session)
    iterations = await iteration_repo.get_by_experiment(experiment_id)
    current_iteration = len(iterations)
    
    # Calculate progress (total = max_iterations × number of prompts)
    num_prompts = len(experiment.initial_prompts) if experiment.initial_prompts else 1
    total_iterations = experiment.max_iterations * num_prompts
    progress_percent = (current_iteration / total_iterations * 100) if total_iterations > 0 else 0.0
    
    # Debug: Print to stdout
    print(f"[DEBUG] Progress: num_prompts={num_prompts}, max_iter={experiment.max_iterations}, total={total_iterations}, current={current_iteration}")
    
    # Calculate elapsed time
    elapsed_time = (datetime.utcnow() - experiment.created_at).total_seconds()
    
    # Estimate remaining time (simplified: average time per iteration)
    estimated_remaining = None
    if current_iteration > 0 and progress_percent > 0:
        avg_time_per_iteration = elapsed_time / current_iteration
        remaining_iterations = total_iterations - current_iteration
        estimated_remaining = avg_time_per_iteration * remaining_iterations
    
    response = ScanStatusResponse(
        experiment_id=experiment_id,
        status=experiment.status,
        current_iteration=current_iteration,
        total_iterations=total_iterations,
        progress_percent=progress_percent,
        elapsed_time_seconds=elapsed_time,
        estimated_remaining_seconds=estimated_remaining
    )
    return api_response(response)


@router.post("/batch", dependencies=[Depends(verify_api_key)])
async def start_batch_scan(
    request: BatchScanRequest,
    background_tasks: BackgroundTasks,
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator)
):
    """
    Start batch scan (multiple experiments in parallel).
    
    Each experiment in the request is executed independently with its own config and prompts.
    Experiments run concurrently using asyncio.create_task within a single background task.
    """
    # Collect experiment IDs for response
    experiment_ids = [exp_config.experiment_id for exp_config in request.experiments]
    
    logger.info(f"[DIAG-BATCH] Starting batch scan for {len(experiment_ids)} experiments")
    logger.info(f"[DIAG-BATCH] Experiment IDs: {[str(eid) for eid in experiment_ids]}")
    
    # Dispatch all experiments concurrently via a single background task
    # This ensures true parallelism (BackgroundTasks executes tasks serially, so we use
    # asyncio.create_task within one background task to achieve concurrency)
    background_tasks.add_task(
        _run_batch_experiments_concurrently,
        request.experiments,
        orchestrator
    )
    
    logger.info(f"[DIAG-BATCH] All {len(experiment_ids)} experiments dispatched for concurrent execution")
    
    return api_response({
        "experiments": [str(exp_id) for exp_id in experiment_ids],
        "status": "started",
        "message": f"Batch scan started for {len(experiment_ids)} experiments",
        "note": "Each experiment runs independently and concurrently with its own configuration and prompts"
    })

