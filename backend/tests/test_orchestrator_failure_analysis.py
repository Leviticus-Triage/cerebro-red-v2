"""
Tests for Failure Analysis Implementation
"""
import pytest
from uuid import uuid4
from core.orchestrator import RedTeamOrchestrator
from core.models import ExperimentConfig, LLMProvider, AttackStrategyType, AttackIteration
from unittest.mock import MagicMock
from datetime import datetime


@pytest.fixture
def orchestrator():
    """Create orchestrator instance with mocked dependencies."""
    return RedTeamOrchestrator(
        mutator=MagicMock(),
        judge=MagicMock(),
        target_llm_client=MagicMock(),
        audit_logger=MagicMock(),
        experiment_repo=MagicMock(),
        iteration_repo=MagicMock(),
        vulnerability_repo=MagicMock()
    )


@pytest.fixture
def experiment_config():
    """Create a test experiment config."""
    return ExperimentConfig(
        experiment_id=uuid4(),
        name="Test Experiment",
        description="Test",
        target_model_provider=LLMProvider.OLLAMA,
        target_model_name="qwen2.5:3b",
        attacker_model_provider=LLMProvider.OLLAMA,
        attacker_model_name="qwen3:8b",
        judge_model_provider=LLMProvider.OLLAMA,
        judge_model_name="qwen3:8b",
        initial_prompts=["test prompt"],
        strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
        max_iterations=5,
        success_threshold=7.0
    )


def test_failure_analysis_no_iterations(orchestrator, experiment_config):
    """Test failure analysis when no iterations were executed."""
    analysis = orchestrator._compute_failure_analysis(
        iterations=[],
        experiment_config=experiment_config,
        statistics_dict={"total_iterations": 0}
    )
    
    assert analysis["failure_reason"] == "no_iterations_executed"
    assert analysis["iterations_executed"] == 0
    assert analysis["best_score"] == 0.0
    assert len(analysis["recommendations"]) > 0


def test_failure_analysis_max_iterations_reached(orchestrator, experiment_config):
    """Test failure analysis when max iterations reached."""
    iterations = [
        AttackIteration(
            iteration_id=uuid4(),
            experiment_id=experiment_config.experiment_id,
            iteration_number=i,
            strategy_used=AttackStrategyType.ROLEPLAY_INJECTION,
            original_prompt="test",
            mutated_prompt="test mutated",
            target_response="response",
            judge_score=5.0 + i * 0.1,  # Scores below threshold
            judge_reasoning="test",
            success=False,
            latency_ms=100
        )
        for i in range(1, 6)  # 5 iterations (max_iterations)
    ]
    
    analysis = orchestrator._compute_failure_analysis(
        iterations=iterations,
        experiment_config=experiment_config,
        statistics_dict={"total_iterations": 5}
    )
    
    assert analysis["failure_reason"] == "max_iterations_reached"
    assert analysis["iterations_executed"] == 5
    assert analysis["best_score"] > 0
    assert analysis["threshold_gap"] > 0
    assert "max_iterations" in str(analysis["recommendations"][0]).lower()


def test_failure_analysis_consistent_low_scores(orchestrator, experiment_config):
    """Test failure analysis when all scores are very low."""
    iterations = [
        AttackIteration(
            iteration_id=uuid4(),
            experiment_id=experiment_config.experiment_id,
            iteration_number=1,
            strategy_used=AttackStrategyType.ROLEPLAY_INJECTION,
            original_prompt="test",
            mutated_prompt="test mutated",
            target_response="response",
            judge_score=2.0,  # Below threshold/2 (3.5)
            judge_reasoning="test",
            success=False,
            latency_ms=100
        )
    ]
    
    analysis = orchestrator._compute_failure_analysis(
        iterations=iterations,
        experiment_config=experiment_config,
        statistics_dict={"total_iterations": 1}
    )
    
    assert analysis["failure_reason"] == "consistent_low_scores"
    assert analysis["best_score"] == 2.0


def test_failure_analysis_finds_best_result(orchestrator, experiment_config):
    """Test that failure analysis correctly identifies best result."""
    iterations = [
        AttackIteration(
            iteration_id=uuid4(),
            experiment_id=experiment_config.experiment_id,
            iteration_number=i,
            strategy_used=AttackStrategyType.ROLEPLAY_INJECTION,
            original_prompt="test",
            mutated_prompt="test mutated",
            target_response="response",
            judge_score=float(i),  # Scores: 1, 2, 3, 4, 5
            judge_reasoning="test",
            success=False,
            latency_ms=100
        )
        for i in range(1, 6)
    ]
    
    analysis = orchestrator._compute_failure_analysis(
        iterations=iterations,
        experiment_config=experiment_config,
        statistics_dict={"total_iterations": 5}
    )
    
    assert analysis["best_score"] == 5.0
    assert analysis["best_iteration"] == 5
    assert analysis["threshold_gap"] == 2.0  # 7.0 - 5.0


def test_failure_analysis_strategy_performance(orchestrator, experiment_config):
    """Test that strategy performance is calculated correctly."""
    iterations = [
        AttackIteration(
            iteration_id=uuid4(),
            experiment_id=experiment_config.experiment_id,
            iteration_number=i,
            strategy_used=AttackStrategyType.ROLEPLAY_INJECTION if i % 2 == 0 else AttackStrategyType.CONTEXT_FLOODING,
            original_prompt="test",
            mutated_prompt="test mutated",
            target_response="response",
            judge_score=5.0,
            judge_reasoning="test",
            success=False,
            latency_ms=100
        )
        for i in range(1, 5)
    ]
    
    analysis = orchestrator._compute_failure_analysis(
        iterations=iterations,
        experiment_config=experiment_config,
        statistics_dict={"total_iterations": 4}
    )
    
    assert len(analysis["strategy_performance"]) == 2
    for strategy, perf in analysis["strategy_performance"].items():
        assert perf["attempts"] == 2
        assert perf["avg_score"] == 5.0
        assert perf["success_rate"] == 0.0


def test_failure_analysis_iteration_breakdown_limit(orchestrator, experiment_config):
    """Test that iteration breakdown is limited to last 20 iterations."""
    iterations = [
        AttackIteration(
            iteration_id=uuid4(),
            experiment_id=experiment_config.experiment_id,
            iteration_number=i,
            strategy_used=AttackStrategyType.ROLEPLAY_INJECTION,
            original_prompt="test",
            mutated_prompt="test mutated",
            target_response="response",
            judge_score=5.0,
            judge_reasoning="test",
            success=False,
            latency_ms=100
        )
        for i in range(1, 25)  # 24 iterations
    ]
    
    analysis = orchestrator._compute_failure_analysis(
        iterations=iterations,
        experiment_config=experiment_config,
        statistics_dict={"total_iterations": 24}
    )
    
    # Should only include last 20 iterations
    assert len(analysis["iteration_breakdown"]) == 20
    assert analysis["iteration_breakdown"][0]["iteration"] == 5  # First of last 20
    assert analysis["iteration_breakdown"][-1]["iteration"] == 24  # Last iteration


@pytest.mark.asyncio
async def test_failure_analysis_websocket_event():
    """Test that failure analysis is sent via WebSocket."""
    from unittest.mock import AsyncMock, patch
    from core.orchestrator import RedTeamOrchestrator
    from core.models import ExperimentConfig, LLMProvider, AttackStrategyType
    from uuid import uuid4
    
    orchestrator = RedTeamOrchestrator(
        mutator=MagicMock(),
        judge=MagicMock(),
        target_llm_client=MagicMock(),
        audit_logger=MagicMock(),
        experiment_repo=MagicMock(),
        iteration_repo=MagicMock(),
        vulnerability_repo=MagicMock()
    )
    
    experiment_config = ExperimentConfig(
        experiment_id=uuid4(),
        name="Test",
        target_model_provider=LLMProvider.OLLAMA,
        target_model_name="qwen2.5:3b",
        attacker_model_provider=LLMProvider.OLLAMA,
        attacker_model_name="qwen3:8b",
        judge_model_provider=LLMProvider.OLLAMA,
        judge_model_name="qwen3:8b",
        initial_prompts=["test"],
        strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
        max_iterations=3,
        success_threshold=7.0
    )
    
    iterations = [
        AttackIteration(
            iteration_id=uuid4(),
            experiment_id=experiment_config.experiment_id,
            iteration_number=1,
            strategy_used=AttackStrategyType.ROLEPLAY_INJECTION,
            original_prompt="test",
            mutated_prompt="test",
            target_response="response",
            judge_score=5.0,
            judge_reasoning="test",
            success=False,
            latency_ms=100
        )
    ]
    
    with patch('api.websocket.send_failure_analysis', new_callable=AsyncMock) as mock_send:
        analysis = orchestrator._compute_failure_analysis(
            iterations=iterations,
            experiment_config=experiment_config,
            statistics_dict={"total_iterations": 1}
        )
        
        # Verify analysis structure
        assert "failure_reason" in analysis
        assert "best_score" in analysis
        assert "recommendations" in analysis
