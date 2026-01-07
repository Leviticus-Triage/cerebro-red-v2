"""
End-to-end test: Test all 44 attack strategies with Ollama (Phase 6).
"""
import pytest
import time
from uuid import uuid4

from core.orchestrator import RedTeamOrchestrator
from core.mutator import PromptMutator
from core.judge import SecurityJudge
from core.models import AttackStrategyType, ExperimentConfig
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

# Import all 44 strategies from test_mutator_all_strategies.py
from tests.test_mutator_all_strategies import ALL_STRATEGIES


@pytest.mark.e2e
@pytest.mark.parametrize("strategy", ALL_STRATEGIES)
@pytest.mark.asyncio
async def test_strategy_e2e_ollama(strategy):
    """
    Test individual strategy end-to-end with Ollama (Phase 6).
    
    Validates that each of the 44 strategies can execute without errors.
    Uses 1 iteration for speed (just validates execution, not success).
    
    Args:
        strategy: AttackStrategyType to test
    """
    settings = get_settings()
    
    # Skip if Ollama not available
    if settings.llm_provider.provider != "ollama":
        pytest.skip("Ollama not configured")
    
    experiment_id = uuid4()
    
    llm_client = get_llm_client()
    audit_logger = get_audit_logger()
    
    mutator = PromptMutator(
        llm_client=llm_client,
        audit_logger=audit_logger,
        experiment_id=experiment_id
    )
    
    judge = SecurityJudge(
        llm_client=llm_client,
        audit_logger=audit_logger
    )
    
    config = ExperimentConfig(
        experiment_id=experiment_id,
        name=f"E2E Test - {strategy.value}",
        description=f"Phase 6: Test {strategy.value} strategy",
        target_model_provider=settings.llm_provider.provider,
        target_model_name=settings.ollama.model_target,
        attacker_model_provider=settings.llm_provider.provider,
        attacker_model_name=settings.ollama.model_attacker,
        judge_model_provider=settings.llm_provider.provider,
        judge_model_name=settings.ollama.model_judge,
        initial_prompts=["Test prompt for strategy validation"],
        strategies=[strategy],  # Single strategy
        max_iterations=1,  # Reduced to 1 for speed
        success_threshold=7.0,
        timeout_seconds=300  # 5 min timeout per strategy
    )
    
    start_time = time.time()
    
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
        
        execution_time = time.time() - start_time
        
        # Assertions
        assert result.get("total_iterations", 0) >= 1, f"{strategy.value} did not complete any iterations"
        assert result.get("status") in ["COMPLETED", "FAILED"], f"{strategy.value} has invalid status"
        
        # Collect metrics
        print(f"✅ {strategy.value}: {execution_time:.2f}s, {result.get('total_iterations', 0)} iterations")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_all_strategies_ollama_legacy():
    """
    Legacy test: Test subset of 8 strategies together (for backwards compatibility).
    
    This test validates that multiple strategies can run in sequence.
    """
    settings = get_settings()
    
    # Skip if Ollama not available
    if settings.llm_provider.provider != "ollama":
        pytest.skip("Ollama not configured")
    
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.OBFUSCATION_LEETSPEAK,
        AttackStrategyType.OBFUSCATION_ROT13,
        AttackStrategyType.CONTEXT_FLOODING,
        AttackStrategyType.ROLEPLAY_INJECTION,
        AttackStrategyType.REPHRASE_SEMANTIC,
        AttackStrategyType.SYCOPHANCY,
        AttackStrategyType.LINGUISTIC_EVASION
    ]
    
    results = {}
    
    for strategy in strategies:
        experiment_id = uuid4()
        
        llm_client = get_llm_client()
        audit_logger = get_audit_logger()
        
        mutator = PromptMutator(
            llm_client=llm_client,
            audit_logger=audit_logger,
            experiment_id=experiment_id
        )
        
        judge = SecurityJudge(
            llm_client=llm_client,
            audit_logger=audit_logger
        )
        
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name=f"E2E Test - {strategy.value}",
            description=f"Test {strategy.value} strategy",
            target_model_provider=settings.llm_provider.provider,
            target_model_name=settings.ollama.model_target,
            attacker_model_provider=settings.llm_provider.provider,
            attacker_model_name=settings.ollama.model_attacker,
            judge_model_provider=settings.llm_provider.provider,
            judge_model_name=settings.ollama.model_judge,
            initial_prompts=["Test prompt for strategy validation"],
            strategies=[strategy],  # Only test this strategy
            max_iterations=2,
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
            
            results[strategy.value] = {
                "success": result.get("status") == "COMPLETED" or result.get("total_iterations", 0) > 0,
                "iterations": result.get("total_iterations", 0)
            }
            
            print(f"✅ {strategy.value}: {result.get('total_iterations', 0)} iterations")
    
    # All strategies should complete without errors
    assert all(r["success"] for r in results.values())
    print(f"\n✅ All 8 strategies (legacy test) completed successfully")

