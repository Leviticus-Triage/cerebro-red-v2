"""
Benchmark: Measure memory usage.
"""
import pytest
import os
from uuid import uuid4

from core.orchestrator import RedTeamOrchestrator
from core.mutator import PromptMutator
from core.judge import SecurityJudge
from core.models import ExperimentConfig, AttackStrategyType
from core.telemetry import get_audit_logger
from core.database import (
    AsyncSessionLocal,
    ExperimentRepository,
    AttackIterationRepository,
    VulnerabilityRepository,
    JudgeScoreRepository
)
from utils.llm_client import get_llm_client
from utils.config import get_settings

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@pytest.mark.benchmark
@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed")
@pytest.mark.asyncio
async def test_memory_usage_benchmark():
    """
    Measure memory usage during experiment execution.
    """
    process = psutil.Process(os.getpid())
    
    # Baseline memory
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    settings = get_settings()
    llm_client = get_llm_client()
    audit_logger = get_audit_logger()
    experiment_id = uuid4()
    
    mutator = PromptMutator(
        llm_client=llm_client,
        audit_logger=audit_logger,
        experiment_id=experiment_id
    )
    
    judge = SecurityJudge(
        llm_client=llm_client,
        audit_logger=audit_logger
    )
    
    # Run experiment
    config = ExperimentConfig(
        experiment_id=experiment_id,
        name="Memory Benchmark",
        description="Test memory usage",
        target_model_provider=settings.llm_provider.provider,
        target_model_name=settings.ollama.model_target,
        attacker_model_provider=settings.llm_provider.provider,
        attacker_model_name=settings.ollama.model_attacker,
        judge_model_provider=settings.llm_provider.provider,
        judge_model_name=settings.ollama.model_judge,
        initial_prompts=["Test prompt"] * 10,  # 10 prompts
        strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
        max_iterations=5,
        success_threshold=7.0
    )
    
    async with AsyncSessionLocal() as session:
        experiment_repo = ExperimentRepository(session)
        iteration_repo = AttackIterationRepository(session)
        vulnerability_repo = VulnerabilityRepository(session)
        judge_score_repo = JudgeScoreRepository(session)
        
        orchestrator = RedTeamOrchestrator(
            mutator=mutator,
            judge=judge,
            target_llm_client=llm_client,
            audit_logger=audit_logger,
            experiment_repo=experiment_repo,
            iteration_repo=iteration_repo,
            vulnerability_repo=vulnerability_repo,
            judge_score_repo=judge_score_repo
        )
        
        result = await orchestrator.run_experiment(config)
        await session.commit()
    
    # Peak memory
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = peak_memory - baseline_memory
    
    print(f"\n📊 Memory Usage Benchmark:")
    print(f"   - Baseline Memory: {baseline_memory:.2f} MB")
    print(f"   - Peak Memory: {peak_memory:.2f} MB")
    print(f"   - Memory Increase: {memory_increase:.2f} MB")
    if result.get("total_iterations", 0) > 0:
        print(f"   - Memory per Iteration: {memory_increase / result['total_iterations']:.2f} MB")
    
    # Assertions
    assert memory_increase < 500  # Should not exceed 500 MB

