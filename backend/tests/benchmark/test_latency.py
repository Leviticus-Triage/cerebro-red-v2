"""
Benchmark: Measure latency distribution.
"""
import pytest
import time
import statistics
from uuid import uuid4

from core.mutator import PromptMutator
from core.judge import SecurityJudge
from core.models import AttackStrategyType
from core.telemetry import get_audit_logger
from utils.llm_client import get_llm_client
from utils.config import get_settings

@pytest.mark.benchmark
@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.skip(reason="Requires Ollama running - use with OLLAMA_BASE_URL=http://localhost:11434")
async def test_latency_benchmark():
    """
    Measure latency distribution for different components.
    
    Components tested:
    - Mutator (prompt generation)
    - Target LLM (response generation)
    - Judge (evaluation)
    """
    num_samples = 20
    
    settings = get_settings()
    llm_client = get_llm_client()
    audit_logger = get_audit_logger()
    
    mutator = PromptMutator(
        llm_client=llm_client,
        audit_logger=audit_logger,
        experiment_id=uuid4()
    )
    
    judge = SecurityJudge(
        llm_client=llm_client,
        audit_logger=audit_logger
    )
    
    mutator_latencies = []
    target_latencies = []
    judge_latencies = []
    
    for i in range(num_samples):
        # Measure mutator latency
        start = time.time()
        mutation = await mutator.mutate(
            original_prompt="Test prompt",
            strategy=AttackStrategyType.ROLEPLAY_INJECTION,
            iteration=i
        )
        mutator_latencies.append((time.time() - start) * 1000)
        
        # Measure target latency
        start = time.time()
        target_response = await llm_client.complete(
            [{"role": "user", "content": mutation.output_prompt}],
            role="target"
        )
        target_latencies.append(target_response.latency_ms)
        
        # Measure judge latency
        start = time.time()
        judge_score = await judge.evaluate(
            original_prompt="Test prompt",
            target_response=target_response.content,
            attack_strategy=AttackStrategyType.ROLEPLAY_INJECTION
        )
        judge_latencies.append((time.time() - start) * 1000)
    
    # Calculate statistics
    print(f"\n📊 Latency Benchmark Results:")
    print(f"{'Component':<15} {'Mean (ms)':<12} {'Std Dev':<12} {'Min':<12} {'Max':<12}")
    print("-" * 63)
    
    for name, latencies in [
        ("Mutator", mutator_latencies),
        ("Target LLM", target_latencies),
        ("Judge", judge_latencies)
    ]:
        if latencies:
            mean_latency = statistics.mean(latencies)
            std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            min_latency = min(latencies)
            max_latency = max(latencies)
            print(f"{name:<15} {mean_latency:<12.2f} {std_latency:<12.2f} "
                  f"{min_latency:<12.2f} {max_latency:<12.2f}")

