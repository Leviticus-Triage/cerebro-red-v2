"""
Unit tests for strategy performance tracking and unused-first selection.

Tests verify:
1. Unused strategies are prioritized in first N iterations
2. Performance metrics are updated correctly after each iteration
3. Performance-based selection chooses best strategy after all are used
4. Strategy rotation handles edge cases correctly
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, MagicMock
from core.orchestrator import RedTeamOrchestrator
from core.models import AttackStrategyType, ExperimentConfig, LLMProvider
from utils.config import get_settings


@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing with mocked dependencies."""
    # Create mock dependencies
    mock_mutator = Mock()
    mock_judge = Mock()
    mock_llm_client = Mock()
    mock_audit_logger = Mock()
    mock_experiment_repo = Mock()
    mock_iteration_repo = Mock()
    mock_vulnerability_repo = Mock()
    
    # Create orchestrator with mocked dependencies
    orch = RedTeamOrchestrator(
        mutator=mock_mutator,
        judge=mock_judge,
        target_llm_client=mock_llm_client,
        audit_logger=mock_audit_logger,
        experiment_repo=mock_experiment_repo,
        iteration_repo=mock_iteration_repo,
        vulnerability_repo=mock_vulnerability_repo
    )
    
    return orch


@pytest.fixture
def test_strategies():
    """Provide a list of 5 test strategies."""
    return [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.JAILBREAK_DAN,
        AttackStrategyType.ROLEPLAY_INJECTION,
        AttackStrategyType.CONTEXT_FLOODING,
        AttackStrategyType.SYCOPHANCY,
    ]


def test_unused_strategies_prioritized(orchestrator, test_strategies):
    """
    Test that unused strategies are selected before used ones.
    
    Verifies:
    - First 5 iterations use all 5 strategies (one each)
    - Each strategy is marked as used after selection
    - Remaining count decreases correctly
    - Reasoning mentions "Unused-first"
    """
    experiment_id = uuid4()
    
    # Initialize strategy rotation
    orchestrator._init_strategy_rotation(experiment_id, test_strategies)
    
    # Verify initialization
    rotation = orchestrator._strategy_rotation[experiment_id]
    assert len(rotation["strategies"]) == 5
    assert len(rotation["used"]) == 0
    assert "strategy_performance" in rotation
    assert len(rotation["strategy_performance"]) == 5
    
    # First 5 iterations should use all 5 strategies (one each)
    used_in_first_5 = set()
    for i in range(1, 6):
        strategy, reasoning, _, remaining = orchestrator._get_next_strategy(
            experiment_id, iteration=i
        )
        used_in_first_5.add(strategy)
        
        # Verify reasoning mentions "Unused-first"
        assert "Unused-first" in reasoning or "unused" in reasoning.lower(), \
            f"Iteration {i}: Expected 'Unused-first' in reasoning, got: {reasoning}"
        
        # Verify remaining count decreases
        expected_remaining = 5 - i
        assert remaining == expected_remaining, \
            f"Iteration {i}: Expected {expected_remaining} remaining, got {remaining}"
        
        # Verify strategy is marked as used
        rotation = orchestrator._strategy_rotation[experiment_id]
        assert strategy in rotation["used"], \
            f"Iteration {i}: Strategy {strategy.value} not marked as used"
    
    # All 5 strategies should be used in first 5 iterations
    assert len(used_in_first_5) == 5, \
        f"Expected 5 unique strategies, got {len(used_in_first_5)}"
    assert used_in_first_5 == set(test_strategies), \
        "Not all strategies were used in first 5 iterations"
    
    # Verify all strategies are marked as used
    rotation = orchestrator._strategy_rotation[experiment_id]
    assert len(rotation["used"]) == 5, \
        f"Expected 5 strategies marked as used, got {len(rotation['used'])}"


def test_performance_tracking_updates(orchestrator, test_strategies):
    """
    Test that performance metrics are updated correctly after each iteration.
    
    Verifies:
    - total_attempts increments
    - success_count increments on success
    - scores list grows
    - avg_score is calculated correctly
    """
    experiment_id = uuid4()
    orchestrator._init_strategy_rotation(experiment_id, test_strategies)
    
    strategy = test_strategies[0]  # Use first strategy for testing
    
    # Initial state
    rotation = orchestrator._strategy_rotation[experiment_id]
    perf = rotation["strategy_performance"][strategy]
    assert perf["total_attempts"] == 0
    assert perf["success_count"] == 0
    assert perf["avg_score"] == 0.0
    assert len(perf["scores"]) == 0
    
    # Update 1: Failure (score=3.5, success=False)
    orchestrator._update_strategy_performance(
        experiment_id=experiment_id,
        strategy=strategy,
        judge_score=3.5,
        success=False
    )
    
    perf = rotation["strategy_performance"][strategy]
    assert perf["total_attempts"] == 1
    assert perf["success_count"] == 0
    assert perf["avg_score"] == 3.5
    assert perf["scores"] == [3.5]
    
    # Update 2: Success (score=8.0, success=True)
    orchestrator._update_strategy_performance(
        experiment_id=experiment_id,
        strategy=strategy,
        judge_score=8.0,
        success=True
    )
    
    perf = rotation["strategy_performance"][strategy]
    assert perf["total_attempts"] == 2
    assert perf["success_count"] == 1
    assert perf["avg_score"] == (3.5 + 8.0) / 2  # 5.75
    assert perf["scores"] == [3.5, 8.0]
    
    # Update 3: Another success (score=7.5, success=True)
    orchestrator._update_strategy_performance(
        experiment_id=experiment_id,
        strategy=strategy,
        judge_score=7.5,
        success=True
    )
    
    perf = rotation["strategy_performance"][strategy]
    assert perf["total_attempts"] == 3
    assert perf["success_count"] == 2
    assert perf["avg_score"] == pytest.approx((3.5 + 8.0 + 7.5) / 3, rel=0.01)  # 6.33
    assert perf["scores"] == [3.5, 8.0, 7.5]


def test_performance_based_selection(orchestrator, test_strategies):
    """
    Test that performance-based selection chooses the best strategy.
    
    Verifies:
    - After all strategies are used, performance-based selection activates
    - Strategy with highest effectiveness score is selected
    - Effectiveness calculation: 60% success_rate + 40% avg_score
    """
    experiment_id = uuid4()
    orchestrator._init_strategy_rotation(experiment_id, test_strategies)
    
    # Use all 5 strategies first (unused-first phase)
    for i in range(1, 6):
        orchestrator._get_next_strategy(experiment_id, iteration=i)
    
    # Verify all strategies are used
    rotation = orchestrator._strategy_rotation[experiment_id]
    assert len(rotation["used"]) == 5
    
    # Simulate performance data for each strategy
    # Strategy 0: 1/2 success (50%), avg_score=5.0 → effectiveness = 0.5*0.6 + 0.5*0.4 = 50%
    orchestrator._update_strategy_performance(experiment_id, test_strategies[0], 4.0, False)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[0], 6.0, True)
    
    # Strategy 1: 2/2 success (100%), avg_score=8.0 → effectiveness = 1.0*0.6 + 0.8*0.4 = 92%
    orchestrator._update_strategy_performance(experiment_id, test_strategies[1], 8.5, True)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[1], 7.5, True)
    
    # Strategy 2: 0/2 success (0%), avg_score=3.0 → effectiveness = 0.0*0.6 + 0.3*0.4 = 12%
    orchestrator._update_strategy_performance(experiment_id, test_strategies[2], 3.5, False)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[2], 2.5, False)
    
    # Strategy 3: 1/3 success (33%), avg_score=4.5 → effectiveness = 0.33*0.6 + 0.45*0.4 = 38%
    orchestrator._update_strategy_performance(experiment_id, test_strategies[3], 3.0, False)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[3], 5.0, True)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[3], 5.5, False)
    
    # Strategy 4: 2/3 success (67%), avg_score=6.5 → effectiveness = 0.67*0.6 + 0.65*0.4 = 66%
    orchestrator._update_strategy_performance(experiment_id, test_strategies[4], 7.0, True)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[4], 5.0, False)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[4], 7.5, True)
    
    # Iteration 6: Should select Strategy 1 (highest effectiveness: 92%)
    strategy, reasoning, _, remaining = orchestrator._get_next_strategy(
        experiment_id, iteration=6, judge_score=7.0
    )
    
    assert strategy == test_strategies[1], \
        f"Expected {test_strategies[1].value} (best performer), got {strategy.value}"
    assert "Performance-based" in reasoning or "performance" in reasoning.lower(), \
        f"Expected 'Performance-based' in reasoning, got: {reasoning}"
    assert remaining == 0, \
        f"Expected 0 remaining (all used), got {remaining}"
    
    # Verify performance metrics
    rotation = orchestrator._strategy_rotation[experiment_id]
    perf1 = rotation["strategy_performance"][test_strategies[1]]
    assert perf1["total_attempts"] == 2
    assert perf1["success_count"] == 2
    assert perf1["avg_score"] == pytest.approx(8.0, rel=0.01)


def test_strategy_rotation_with_single_strategy(orchestrator):
    """
    Test edge case: Only one strategy configured.
    
    Verifies:
    - Single strategy is selected repeatedly
    - Performance tracking still works
    """
    experiment_id = uuid4()
    single_strategy = [AttackStrategyType.ROLEPLAY_INJECTION]
    
    orchestrator._init_strategy_rotation(experiment_id, single_strategy)
    
    # First 3 iterations should all use the same strategy
    for i in range(1, 4):
        strategy, reasoning, _, remaining = orchestrator._get_next_strategy(
            experiment_id, iteration=i
        )
        
        assert strategy == single_strategy[0], \
            f"Iteration {i}: Expected {single_strategy[0].value}, got {strategy.value}"
        
        # First iteration: unused-first, then performance-based or round-robin
        if i == 1:
            assert "Unused-first" in reasoning or "unused" in reasoning.lower()
            assert remaining == 0  # No more unused after first
        
        # Update performance
        orchestrator._update_strategy_performance(
            experiment_id, strategy, 5.0 + i, i % 2 == 0
        )
    
    # Verify performance tracking
    rotation = orchestrator._strategy_rotation[experiment_id]
    perf = rotation["strategy_performance"][single_strategy[0]]
    assert perf["total_attempts"] == 3
    assert perf["success_count"] == 1  # Only iteration 2 was success


def test_all_strategies_used_in_n_iterations(orchestrator):
    """
    Test that N strategies are all used within first N iterations.
    
    This is the core requirement: ensure all selected strategies
    get tried before any repetition occurs.
    """
    experiment_id = uuid4()
    
    # Test with different strategy counts
    for n in [3, 5, 10]:
        # Get first N strategies
        all_strategies = list(AttackStrategyType)
        strategies = all_strategies[:n]
        
        # Re-initialize for each test
        exp_id = uuid4()
        orchestrator._init_strategy_rotation(exp_id, strategies)
        
        used_strategies = set()
        for i in range(1, n + 1):
            strategy, _, _, _ = orchestrator._get_next_strategy(exp_id, iteration=i)
            used_strategies.add(strategy)
        
        # All N strategies should be used in first N iterations
        assert len(used_strategies) == n, \
            f"With {n} strategies: Expected all {n} used, got {len(used_strategies)}"
        assert used_strategies == set(strategies), \
            f"With {n} strategies: Not all strategies were used"


def test_performance_selection_without_judge_score(orchestrator, test_strategies):
    """
    Test fallback to round-robin when judge_score is None.
    
    Verifies:
    - If all strategies used but no judge_score provided, use round-robin
    - Round-robin formula: idx = (iteration - 1) % len(strategies)
    """
    experiment_id = uuid4()
    orchestrator._init_strategy_rotation(experiment_id, test_strategies)
    
    # Use all strategies first
    for i in range(1, 6):
        orchestrator._get_next_strategy(experiment_id, iteration=i)
    
    # Add some performance data
    for strategy in test_strategies:
        orchestrator._update_strategy_performance(
            experiment_id, strategy, 5.0, False
        )
    
    # Iteration 6 without judge_score should use round-robin
    strategy, reasoning, _, _ = orchestrator._get_next_strategy(
        experiment_id, iteration=6, judge_score=None
    )
    
    # Round-robin: (6-1) % 5 = 0 → first strategy
    expected_strategy = test_strategies[0]
    assert strategy == expected_strategy, \
        f"Expected round-robin to select {expected_strategy.value}, got {strategy.value}"
    assert "Round-robin" in reasoning or "round-robin" in reasoning.lower(), \
        f"Expected 'Round-robin' in reasoning, got: {reasoning}"


def test_strategy_performance_success_rate_calculation(orchestrator, test_strategies):
    """
    Test that success rate is calculated correctly in effectiveness score.
    
    Verifies:
    - Effectiveness = (success_rate * 0.6) + (score_component * 0.4)
    - Strategy with higher success rate is preferred over higher avg_score
    """
    experiment_id = uuid4()
    orchestrator._init_strategy_rotation(experiment_id, test_strategies)
    
    # Use all strategies first
    for i in range(1, 6):
        orchestrator._get_next_strategy(experiment_id, iteration=i)
    
    # Strategy A: High success rate (100%), low avg_score (6.0)
    # Effectiveness = 1.0*0.6 + 0.6*0.4 = 0.84 = 84%
    orchestrator._update_strategy_performance(experiment_id, test_strategies[0], 6.0, True)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[0], 6.0, True)
    
    # Strategy B: Low success rate (0%), high avg_score (9.0)
    # Effectiveness = 0.0*0.6 + 0.9*0.4 = 0.36 = 36%
    orchestrator._update_strategy_performance(experiment_id, test_strategies[1], 9.0, False)
    orchestrator._update_strategy_performance(experiment_id, test_strategies[1], 9.0, False)
    
    # Add minimal data for other strategies
    for strategy in test_strategies[2:]:
        orchestrator._update_strategy_performance(experiment_id, strategy, 5.0, False)
    
    # Next selection should prefer Strategy A (higher effectiveness)
    strategy, _, _, _ = orchestrator._get_next_strategy(
        experiment_id, iteration=6, judge_score=7.0
    )
    
    assert strategy == test_strategies[0], \
        f"Expected strategy with higher success rate, got {strategy.value}"


def test_strategy_rotation_cleanup(orchestrator, test_strategies):
    """
    Test that strategy rotation data is properly cleaned up.
    
    Verifies:
    - Rotation data exists after initialization
    - Rotation data can be manually removed
    """
    experiment_id = uuid4()
    
    # Initialize rotation
    orchestrator._init_strategy_rotation(experiment_id, test_strategies)
    assert experiment_id in orchestrator._strategy_rotation
    
    # Manual cleanup (simulating what happens at experiment end)
    orchestrator._strategy_rotation.pop(experiment_id, None)
    assert experiment_id not in orchestrator._strategy_rotation


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
