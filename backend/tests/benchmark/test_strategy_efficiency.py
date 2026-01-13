"""
Benchmark test: Strategy efficiency measurement (Phase 6).

Measures mutation latency and performance for all attack strategies.
"""
import pytest
import time
import statistics
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from core.mutator import PromptMutator
from core.models import AttackStrategyType
from core.telemetry import get_audit_logger
from tests.test_mutator_all_strategies import ALL_STRATEGIES


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for benchmark tests (Comment 2: extended with settings)."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value="Mocked LLM response")
    
    # Comment 2: Add settings mock with get_llm_config (complete fix)
    mock_settings = Mock()
    mock_settings.get_llm_config = Mock(return_value={
        "provider": "ollama",
        "model_name": "qwen2.5:3b",
        "temperature": 0.7,
        "max_tokens": 2000
    })
    client.settings = mock_settings
    
    return client


@pytest.fixture
def mutator(mock_llm_client):
    """Create mutator with mocked LLM for benchmarking."""
    audit_logger = get_audit_logger()
    experiment_id = uuid4()
    
    return PromptMutator(
        llm_client=mock_llm_client,
        audit_logger=audit_logger,
        experiment_id=experiment_id
    )


@pytest.mark.benchmark
@pytest.mark.asyncio
@pytest.mark.parametrize("strategy", ALL_STRATEGIES[:10])  # Test subset for speed
async def test_strategy_efficiency(strategy, mutator):
    """
    Benchmark mutation efficiency per strategy.
    
    Measures:
    - Mean latency (ms)
    - Standard deviation
    - Min/Max latency
    
    Args:
        strategy: AttackStrategyType to benchmark
        mutator: PromptMutator fixture
    """
    num_iterations = 10
    latencies = []
    mutation_lengths = []
    
    for i in range(num_iterations):
        start = time.time()
        
        try:
            # Comment 1: mutate returns single PromptMutation object
            mutation = await mutator.mutate(
                original_prompt="Test prompt for benchmarking",
                strategy=strategy,
                iteration=i,
                feedback=None
            )
            
            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)
            mutation_lengths.append(len(mutation.output_prompt))
            
        except Exception as e:
            pytest.fail(f"{strategy.value} failed: {e}")
    
    # Calculate statistics
    mean_latency = statistics.mean(latencies)
    std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
    min_latency = min(latencies)
    max_latency = max(latencies)
    mean_length = statistics.mean(mutation_lengths)
    
    # Performance assertions
    # Non-LLM strategies should be fast (< 500ms mean)
    if strategy not in [AttackStrategyType.REPHRASE_SEMANTIC]:
        assert mean_latency < 500, f"{strategy.value} too slow: {mean_latency:.2f}ms"
    
    # All strategies should produce non-empty mutations
    assert mean_length > 0, f"{strategy.value} produced empty mutations"
    
    # Print benchmark results
    print(f"\n{strategy.value}:")
    print(f"  Mean: {mean_latency:.2f}ms ± {std_latency:.2f}ms")
    print(f"  Range: [{min_latency:.2f}ms, {max_latency:.2f}ms]")
    print(f"  Avg Length: {mean_length:.0f} chars")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_all_strategies_efficiency_summary(mutator):
    """
    Benchmark all 44 strategies and generate summary report.
    
    This test runs all strategies once and collects aggregate metrics.
    """
    results = []
    
    for strategy in ALL_STRATEGIES:
        start = time.time()
        
        try:
            # Comment 1: mutate returns single PromptMutation object
            mutation = await mutator.mutate(
                original_prompt="Test prompt",
                strategy=strategy,
                iteration=0,
                feedback=None
            )
            
            latency_ms = (time.time() - start) * 1000
            
            results.append({
                "strategy": strategy.value,
                "latency_ms": latency_ms,
                "mutation_length": len(mutation.output_prompt),
                "success": True
            })
            
        except Exception as e:
            results.append({
                "strategy": strategy.value,
                "latency_ms": 0,
                "mutation_length": 0,
                "success": False,
                "error": str(e)
            })
    
    # Calculate aggregate statistics
    successful = [r for r in results if r["success"]]
    total_latency = sum(r["latency_ms"] for r in successful)
    mean_latency = total_latency / len(successful) if successful else 0
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"STRATEGY EFFICIENCY SUMMARY (Phase 6)")
    print(f"{'='*80}")
    print(f"Total Strategies: {len(ALL_STRATEGIES)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(results) - len(successful)}")
    print(f"Mean Latency: {mean_latency:.2f}ms")
    print(f"Total Time: {total_latency:.2f}ms")
    print(f"{'='*80}")
    
    # Sort by latency (slowest first)
    successful.sort(key=lambda x: x["latency_ms"], reverse=True)
    
    print(f"\nTop 10 Slowest Strategies:")
    for i, result in enumerate(successful[:10], 1):
        print(f"  {i}. {result['strategy']}: {result['latency_ms']:.2f}ms")
    
    print(f"\nTop 10 Fastest Strategies:")
    for i, result in enumerate(reversed(successful[-10:]), 1):
        print(f"  {i}. {result['strategy']}: {result['latency_ms']:.2f}ms")
    
    # Assert all strategies executed successfully
    assert len(successful) == len(ALL_STRATEGIES), \
        f"{len(results) - len(successful)} strategies failed"
    
    print(f"\n All 44 strategies benchmarked successfully")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_strategy_consistency(mutator):
    """
    Test that strategies produce consistent results across multiple runs.
    
    Validates that the same strategy with the same input produces
    similar output lengths (within 20% variance).
    """
    test_strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.OBFUSCATION_LEETSPEAK,
        AttackStrategyType.CONTEXT_FLOODING,
        AttackStrategyType.ROLEPLAY_INJECTION
    ]
    
    for strategy in test_strategies:
        lengths = []
        
        for i in range(5):
            # Comment 1: mutate returns single PromptMutation object
            mutation = await mutator.mutate(
                original_prompt="Consistent test prompt",
                strategy=strategy,
                iteration=i,
                feedback=None
            )
            lengths.append(len(mutation.output_prompt))
        
        # Calculate coefficient of variation
        mean_length = statistics.mean(lengths)
        std_length = statistics.stdev(lengths) if len(lengths) > 1 else 0
        cv = (std_length / mean_length) * 100 if mean_length > 0 else 0
        
        # Assert consistency (CV < 20%)
        assert cv < 20, f"{strategy.value} inconsistent: CV={cv:.2f}%"
        
        print(f" {strategy.value}: CV={cv:.2f}% (consistent)")
