"""
Benchmark: Measure system throughput.
"""
import pytest
import time
import asyncio
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

@pytest.mark.benchmark
@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.skip(reason="Requires Ollama running and sequential execution to avoid DB locks")
async def test_throughput_benchmark():
    """
    Measure how many experiments can be processed per minute.
    
    Test configuration:
    - 10 concurrent experiments
    - 3 iterations each
    - Measure total time and throughput
    """
    num_experiments = 10
    iterations_per_experiment = 3
    
    settings = get_settings()
    llm_client = get_llm_client()
    audit_logger = get_audit_logger()
    
    start_time = time.time()
    
    # Run experiments sequentially to avoid SQLite database locking
    # SQLite doesn't handle concurrent writes well
    results = []
    for i in range(num_experiments):
        experiment_id = uuid4()
        
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name=f"Throughput Test {i}",
            description="Benchmark experiment",
            target_model_provider=settings.llm_provider.provider,
            target_model_name=settings.ollama.model_target,
            attacker_model_provider=settings.llm_provider.provider,
            attacker_model_name=settings.ollama.model_attacker,
            judge_model_provider=settings.llm_provider.provider,
            judge_model_name=settings.ollama.model_judge,
            initial_prompts=["Test prompt"],
            strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
            max_iterations=iterations_per_experiment,
            success_threshold=7.0
        )
        
        async def run_experiment(config, exp_id):
            """Run a single experiment with its own mutator and judge instances."""
            # Create mutator and judge for this specific experiment
            task_mutator = PromptMutator(
                llm_client=llm_client,
                audit_logger=audit_logger,
                experiment_id=exp_id
            )
            
            task_judge = SecurityJudge(
                llm_client=llm_client,
                audit_logger=audit_logger
            )
            task_judge.experiment_id = exp_id
            
            async with AsyncSessionLocal() as session:
                experiment_repo = ExperimentRepository(session)
                iteration_repo = AttackIterationRepository(session)
                vulnerability_repo = VulnerabilityRepository(session)
                judge_score_repo = JudgeScoreRepository(session)
                
                orchestrator = RedTeamOrchestrator(
                    mutator=task_mutator,
                    judge=task_judge,
                    target_llm_client=llm_client,
                    audit_logger=audit_logger,
                    experiment_repo=experiment_repo,
                    iteration_repo=iteration_repo,
                    vulnerability_repo=vulnerability_repo,
                    judge_score_repo=judge_score_repo
                )
                
                return await orchestrator.run_experiment(config)
        
        result = await run_experiment(config, experiment_id)
        results.append(result)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate metrics
    total_iterations = sum(r.get("total_iterations", 0) for r in results)
    throughput_per_minute = (total_iterations / total_time) * 60 if total_time > 0 else 0
    
    print(f"\n📊 Throughput Benchmark Results:")
    print(f"   - Total Experiments: {num_experiments}")
    print(f"   - Total Iterations: {total_iterations}")
    print(f"   - Total Time: {total_time:.2f}s")
    print(f"   - Throughput: {throughput_per_minute:.2f} iterations/minute")
    if total_iterations > 0:
        print(f"   - Average Time per Iteration: {total_time/total_iterations:.2f}s")
    
    # Assertions
    assert throughput_per_minute > 0
    assert total_time < 600  # Should complete within 10 minutes

