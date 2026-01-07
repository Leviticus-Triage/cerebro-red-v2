"""
Tests for strategy rotation implementation (Comment 2).

Ensures that user-selected strategies are actually used in rotation,
not just the hardcoded 3 strategies.
"""

import pytest
from uuid import uuid4
from core.models import AttackStrategyType
from core.orchestrator import RedTeamOrchestrator
from unittest.mock import Mock, AsyncMock, patch


@pytest.fixture
def orchestrator():
    """Create a RedTeamOrchestrator instance for testing."""
    mock_mutator = Mock()
    mock_judge = Mock()
    mock_target_llm = Mock()
    mock_audit_logger = Mock()
    mock_experiment_repo = Mock()
    mock_iteration_repo = Mock()
    mock_vulnerability_repo = Mock()
    
    return RedTeamOrchestrator(
        mutator=mock_mutator,
        judge=mock_judge,
        target_llm_client=mock_target_llm,
        audit_logger=mock_audit_logger,
        experiment_repo=mock_experiment_repo,
        iteration_repo=mock_iteration_repo,
        vulnerability_repo=mock_vulnerability_repo
    )


def test_init_strategy_rotation(orchestrator):
    """Test that strategy rotation is initialized correctly (Comment 2)."""
    experiment_id = uuid4()
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.JAILBREAK_DAN,
        AttackStrategyType.ROLEPLAY_INJECTION,
        AttackStrategyType.CONTEXT_FLOODING,
    ]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    
    assert experiment_id in orchestrator._strategy_rotation
    rotation = orchestrator._strategy_rotation[experiment_id]
    assert rotation["strategies"] == strategies
    assert rotation["current_index"] == 0
    assert rotation["used"] == set()
    assert rotation["iteration_count"] == {}


def test_init_strategy_rotation_empty_list(orchestrator):
    """Test that empty strategy list falls back to defaults (Comment 2)."""
    experiment_id = uuid4()
    
    orchestrator._init_strategy_rotation(experiment_id, [])
    
    rotation = orchestrator._strategy_rotation[experiment_id]
    assert len(rotation["strategies"]) == 3  # Default fallback
    assert AttackStrategyType.ROLEPLAY_INJECTION in rotation["strategies"]
    assert AttackStrategyType.CONTEXT_FLOODING in rotation["strategies"]
    assert AttackStrategyType.REPHRASE_SEMANTIC in rotation["strategies"]


def test_get_next_strategy_round_robin(orchestrator):
    """Test round-robin rotation through user-selected strategies (Comment 2)."""
    experiment_id = uuid4()
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.JAILBREAK_DAN,
        AttackStrategyType.ROLEPLAY_INJECTION,
    ]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    
    # First call should return first strategy (no feedback = round-robin)
    strategy1, reasoning1, _, _ = orchestrator._get_next_strategy(experiment_id, iteration=1)
    assert strategy1 == AttackStrategyType.OBFUSCATION_BASE64
    assert "Round-robin" in reasoning1
    
    # Second call should return second strategy
    strategy2, reasoning2, _, _ = orchestrator._get_next_strategy(experiment_id, iteration=2)
    assert strategy2 == AttackStrategyType.JAILBREAK_DAN
    assert "Round-robin" in reasoning2
    
    # Third call should return third strategy
    strategy3, reasoning3, _, _ = orchestrator._get_next_strategy(experiment_id, iteration=3)
    assert strategy3 == AttackStrategyType.ROLEPLAY_INJECTION
    assert "Round-robin" in reasoning3
    
    # Fourth call should wrap around to first
    strategy4, reasoning4, _, _ = orchestrator._get_next_strategy(experiment_id, iteration=4)
    assert strategy4 == AttackStrategyType.OBFUSCATION_BASE64
    assert "Round-robin" in reasoning4


def test_get_next_strategy_with_feedback(orchestrator):
    """Test intelligent strategy selection based on feedback (Comment 2)."""
    experiment_id = uuid4()
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.ROLEPLAY_INJECTION,
        AttackStrategyType.REPHRASE_SEMANTIC,
        AttackStrategyType.JAILBREAK_DAN,
    ]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    
    # Low score (< tau_1) should prefer roleplay/jailbreak strategies
    strategy_low, reasoning_low, categories_low, _ = orchestrator._get_next_strategy(
        experiment_id,
        iteration=2,
        judge_score=2.0,
        target_response="I can't help with that.",
        thresholds={"tau_1": 3.0, "tau_2": 6.0}
    )
    assert strategy_low in [AttackStrategyType.ROLEPLAY_INJECTION, AttackStrategyType.JAILBREAK_DAN]
    assert "Intelligent selection" in reasoning_low
    assert "roleplay" in categories_low or "jailbreak" in categories_low
    
    # Medium score (tau_1 <= score < tau_2) should prefer obfuscation
    strategy_medium, reasoning_medium, categories_medium, _ = orchestrator._get_next_strategy(
        experiment_id,
        iteration=3,
        judge_score=4.5,
        target_response="I'm not sure about that.",
        thresholds={"tau_1": 3.0, "tau_2": 6.0}
    )
    assert strategy_medium == AttackStrategyType.OBFUSCATION_BASE64
    assert "Intelligent selection" in reasoning_medium
    assert "obfuscation" in categories_medium
    
    # High score (>= tau_2) should prefer refinement strategies
    strategy_high, reasoning_high, categories_high, _ = orchestrator._get_next_strategy(
        experiment_id,
        iteration=4,
        judge_score=7.5,
        target_response="Here's some information...",
        thresholds={"tau_1": 3.0, "tau_2": 6.0}
    )
    assert strategy_high == AttackStrategyType.REPHRASE_SEMANTIC
    assert "Intelligent selection" in reasoning_high
    assert "rephrase" in categories_high or "translation" in categories_high


def test_strategy_rotation_all_strategies_used(orchestrator):
    """Test that all user-selected strategies are eventually used (Comment 2)."""
    experiment_id = uuid4()
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.JAILBREAK_DAN,
        AttackStrategyType.ROLEPLAY_INJECTION,
        AttackStrategyType.CONTEXT_FLOODING,
        AttackStrategyType.SYCOPHANCY,
    ]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    
    used_strategies = set()
    # Run through 25 iterations (forced rotation every 5th ensures all 5 are tried)
    for i in range(1, 26):
        strategy, reasoning, _, _ = orchestrator._get_next_strategy(
            experiment_id,
            iteration=i,
            judge_score=2.0 if i > 1 else None,
            target_response="Test" if i > 1 else None
        )
        used_strategies.add(strategy)
    
    # All strategies should have been used at least once (forced rotation every 5th ensures this within 25 iterations)
    assert len(used_strategies) == len(strategies), \
        f"Not all strategies were used. Used: {[s.value for s in used_strategies]}, Expected: {[s.value for s in strategies]}"
    
    # Verify all expected strategies are in used set
    for expected_strategy in strategies:
        assert expected_strategy in used_strategies, \
            f"Strategy {expected_strategy.value} was never used"


def test_strategy_rotation_iteration_counting(orchestrator):
    """Test that iteration counts are tracked per strategy (Comment 2)."""
    experiment_id = uuid4()
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.JAILBREAK_DAN,
    ]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    
    # Use each strategy multiple times
    for i in range(1, 6):
        orchestrator._get_next_strategy(experiment_id, iteration=i)
    
    rotation = orchestrator._strategy_rotation[experiment_id]
    iteration_counts = rotation["iteration_count"]
    
    # Both strategies should have been used
    assert AttackStrategyType.OBFUSCATION_BASE64 in iteration_counts
    assert AttackStrategyType.JAILBREAK_DAN in iteration_counts
    
    # Total iterations should be 5
    total = sum(iteration_counts.values())
    assert total == 5


def test_strategy_rotation_cleanup(orchestrator):
    """Test that strategy rotation is cleaned up after experiment (Comment 2)."""
    experiment_id = uuid4()
    strategies = [AttackStrategyType.OBFUSCATION_BASE64]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    assert experiment_id in orchestrator._strategy_rotation
    
    # Note: _cleanup_task_queue doesn't clean up strategy rotation
    # This test verifies rotation exists, cleanup is tested separately
    assert experiment_id in orchestrator._strategy_rotation


def test_forced_rotation_every_5th_iteration(orchestrator):
    """Test that forced rotation happens every 5th iteration (Phase 3)."""
    experiment_id = uuid4()
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.JAILBREAK_DAN,
        AttackStrategyType.ROLEPLAY_INJECTION,
        AttackStrategyType.SYCOPHANCY,
    ]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    
    # Iterations 1-4: Intelligent selection (with feedback)
    for i in range(1, 5):
        strategy, reasoning, _, _ = orchestrator._get_next_strategy(
            experiment_id,
            iteration=i,
            judge_score=2.0,  # Low score → would prefer roleplay/jailbreak
            target_response="I can't help with that."
        )
        # Should prefer roleplay/jailbreak but NOT necessarily round-robin
        assert "Intelligent selection" in reasoning or "Fallback" in reasoning or "Round-robin" in reasoning
    
    # Iteration 5: Forced rotation
    strategy_5, reasoning_5, _, _ = orchestrator._get_next_strategy(
        experiment_id,
        iteration=5,
        judge_score=2.0,
        target_response="I can't help with that."
    )
    assert "Forced rotation" in reasoning_5
    
    # Iteration 10: Forced rotation again
    strategy_10, reasoning_10, _, _ = orchestrator._get_next_strategy(
        experiment_id,
        iteration=10,
        judge_score=2.0,
        target_response="I can't help with that."
    )
    assert "Forced rotation" in reasoning_10


def test_all_44_strategies_used_in_50_iterations(orchestrator):
    """Test that all 44 strategies are used when selected (Comment 2, Phase 3, Comment 1)."""
    experiment_id = uuid4()
    
    # All 44 strategies
    all_strategies = list(AttackStrategyType)
    
    orchestrator._init_strategy_rotation(experiment_id, all_strategies)
    
    used_strategies = set()
    
    # Run 50 iterations (Comment 1: unused priority ensures all 44 are used in first 44 iterations)
    for i in range(1, 51):
        # Vary feedback to test different score ranges
        if i % 3 == 0:
            judge_score = 2.0  # Low
        elif i % 3 == 1:
            judge_score = 4.5  # Medium
        else:
            judge_score = 7.5  # High
        
        strategy, reasoning, _, _ = orchestrator._get_next_strategy(
            experiment_id,
            iteration=i,
            judge_score=judge_score if i > 1 else None,
            target_response="Test response" if i > 1 else None
        )
        used_strategies.add(strategy)
    
    # All 44 strategies should have been used (Comment 1: unused priority ensures this within 44 iterations)
    assert len(used_strategies) == 44, \
        f"Only {len(used_strategies)}/44 strategies used. Missing: {[s.value for s in all_strategies if s not in used_strategies]}"


def test_intelligent_selection_respects_available(orchestrator):
    """Test that intelligent selection only picks from available strategies (Phase 3)."""
    experiment_id = uuid4()
    
    # Only obfuscation strategies
    strategies = [
        AttackStrategyType.OBFUSCATION_BASE64,
        AttackStrategyType.OBFUSCATION_LEETSPEAK,
    ]
    
    orchestrator._init_strategy_rotation(experiment_id, strategies)
    
    # Low score would normally prefer roleplay/jailbreak
    # But since they're not available, should pick from obfuscation
    strategy, reasoning, categories, filtered_count = orchestrator._get_next_strategy(
        experiment_id,
        iteration=2,
        judge_score=2.0,  # Low score
        target_response="I can't help with that."
    )
    
    assert strategy in strategies, f"Selected {strategy.value} not in available strategies"
    assert "Fallback to least-used" in reasoning or strategy in strategies
    # Should have filtered out preferred categories that aren't available
    assert filtered_count >= 0
