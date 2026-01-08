"""
Tests for PAIR algorithm implementation in mutator.py.

Validates that the PAIR Algorithm 1 logic correctly adapts strategy
based on feedback scores and implements the mathematical rules from
the PAIR paper (arxiv.org/abs/2310.08419).
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from core.mutator import PromptMutator
from core.models import AttackStrategyType
from core.telemetry import AuditLogger
from utils.llm_client import LLMClient


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock(spec=LLMClient)
    client.settings = MagicMock()
    client.settings.judge.success_threshold = 7.0
    client.settings.get_llm_config.return_value = {
        "model_name": "qwen3:8b",
        "provider": "ollama",
        "api_base": "http://localhost:11434"
    }
    return client


@pytest.fixture
def mock_audit_logger():
    """Create a mock audit logger."""
    logger = MagicMock(spec=AuditLogger)
    return logger


@pytest.fixture
def mutator(mock_llm_client, mock_audit_logger):
    """Create a PromptMutator instance for testing."""
    return PromptMutator(
        llm_client=mock_llm_client,
        audit_logger=mock_audit_logger,
        experiment_id=uuid4()
    )


class TestPAIRFeedbackAnalysis:
    """Test PAIR feedback analysis logic."""
    
    def test_analyze_feedback_strong_refusal(self, mutator):
        """Test that strong refusal (< 3.0) triggers roleplay injection."""
        analysis = mutator._analyze_feedback(
            judge_score=1.5,
            target_response="I can't help with that request."
        )
        
        assert analysis["strategy"] == AttackStrategyType.ROLEPLAY_INJECTION
        assert analysis["confidence"] == 0.8
        assert "Strong refusal" in analysis["reasoning"]
        assert analysis["threshold_used"] == 3.0
    
    def test_analyze_feedback_partial_success(self, mutator):
        """Test that partial success (3.0-6.0) triggers context flooding."""
        analysis = mutator._analyze_feedback(
            judge_score=4.5,
            target_response="While I shouldn't, here's some information..."
        )
        
        assert analysis["strategy"] == AttackStrategyType.CONTEXT_FLOODING
        assert analysis["confidence"] == 0.7
        assert "Partial refusal" in analysis["reasoning"]
    
    def test_analyze_feedback_near_success(self, mutator):
        """Test that near success (≥ 6.0) triggers semantic rephrase."""
        analysis = mutator._analyze_feedback(
            judge_score=7.5,
            target_response="Here's detailed information about..."
        )
        
        assert analysis["strategy"] == AttackStrategyType.REPHRASE_SEMANTIC
        assert analysis["confidence"] == 0.9
        assert "Near success" in analysis["reasoning"]
    
    def test_analyze_feedback_custom_thresholds(self, mutator):
        """Test that custom thresholds work correctly."""
        custom_thresholds = {"tau_1": 2.0, "tau_2": 5.0}
        
        analysis = mutator._analyze_feedback(
            judge_score=2.5,
            target_response="Test response",
            thresholds=custom_thresholds
        )
        
        assert analysis["threshold_used"] == 2.0
        assert analysis["strategy"] == AttackStrategyType.CONTEXT_FLOODING


class TestPAIRStrategyTransitions:
    """Test strategy transition logic."""
    
    @pytest.mark.asyncio
    async def test_strategy_transition_logging(self, mutator, mock_audit_logger):
        """Test that strategy transitions are logged correctly."""
        # First mutation with one strategy
        mutator.previous_strategy = AttackStrategyType.OBFUSCATION_BASE64
        
        mutation = await mutator.mutate(
            original_prompt="Test prompt",
            strategy=AttackStrategyType.ROLEPLAY_INJECTION,
            iteration=2
        )
        
        # Check that log_strategy_transition was called
        assert mock_audit_logger.log_strategy_transition.called
    
    def test_feedback_loop_adaptation(self, mutator):
        """Test that PAIR algorithm adapts strategy based on feedback history."""
        # Simulate feedback loop
        feedback_1 = {
            "target_response": "I can't help with that.",
            "judge_score": 1.5,
            "judge_reasoning": "Standard refusal"
        }
        
        analysis_1 = mutator._analyze_feedback(
            feedback_1["judge_score"],
            feedback_1["target_response"]
        )
        assert analysis_1["strategy"] == AttackStrategyType.ROLEPLAY_INJECTION
        
        # Second iteration: partial success
        feedback_2 = {
            "target_response": "While I shouldn't...",
            "judge_score": 4.5,
            "judge_reasoning": "Partial compliance"
        }
        
        analysis_2 = mutator._analyze_feedback(
            feedback_2["judge_score"],
            feedback_2["target_response"]
        )
        assert analysis_2["strategy"] == AttackStrategyType.CONTEXT_FLOODING
        
        # Third iteration: near success
        feedback_3 = {
            "target_response": "Here's some information...",
            "judge_score": 7.0,
            "judge_reasoning": "Significant compliance"
        }
        
        analysis_3 = mutator._analyze_feedback(
            feedback_3["judge_score"],
            feedback_3["target_response"]
        )
        assert analysis_3["strategy"] == AttackStrategyType.REPHRASE_SEMANTIC


class TestPAIRRephraseSemantic:
    """Test PAIR semantic rephrase implementation."""
    
    @pytest.mark.asyncio
    async def test_pair_rephrase_with_feedback(self, mutator, mock_llm_client):
        """Test that PAIR rephrase uses feedback correctly."""
        # Mock LLM response
        mock_response = AsyncMock()
        mock_response.content = "Improved prompt based on feedback"
        mock_response.model = "qwen3:8b"
        mock_response.provider.value = "ollama"
        mock_response.tokens_used = 50
        mock_response.latency_ms = 200
        
        mock_llm_client.complete = AsyncMock(return_value=mock_response)
        
        feedback = {
            "target_response": "I can't help with that.",
            "judge_score": 7.5,
            "judge_reasoning": "Near success, refine approach"
        }
        
        result = await mutator._mutate_rephrase_semantic(
            prompt="Original prompt",
            feedback=feedback,
            iteration=2
        )
        
        assert result[0] == "Improved prompt based on feedback"
        assert result[1]["feedback_used"] is True
        assert result[1]["pair_algorithm"] == "Algorithm 1"
    
    @pytest.mark.asyncio
    async def test_pair_rephrase_fallback_on_error(self, mutator, mock_llm_client, mock_audit_logger):
        """Test that PAIR rephrase falls back to simple paraphrase on LLM error."""
        # Mock LLM error
        mock_llm_client.complete = AsyncMock(side_effect=Exception("LLM timeout"))
        
        feedback = {
            "target_response": "Test response",
            "judge_score": 7.0,
            "judge_reasoning": "Test reasoning"
        }
        
        result = await mutator._mutate_rephrase_semantic(
            prompt="Original prompt",
            feedback=feedback,
            iteration=1
        )
        
        # Should fallback to simple paraphrase
        assert result[1]["fallback"] is True
        assert result[1]["feedback_used"] is False
        # Error should be logged
        assert mock_audit_logger.log_error.called


class TestPAIRFeedbackValidation:
    """Test feedback validation for PAIR."""
    
    @pytest.mark.asyncio
    async def test_missing_feedback_keys(self, mutator):
        """Test that missing feedback keys raise ValueError."""
        incomplete_feedback = {
            "target_response": "Test",
            # Missing judge_score and judge_reasoning
        }
        
        with pytest.raises(ValueError, match="Feedback missing required keys"):
            await mutator._mutate_rephrase_semantic(
                prompt="Test",
                feedback=incomplete_feedback,
                iteration=1
            )
    
    @pytest.mark.asyncio
    async def test_feedback_validation_in_mutate(self, mutator):
        """Test that mutate() validates feedback before calling PAIR."""
        incomplete_feedback = {
            "target_response": "Test"
            # Missing required keys
        }
        
        with pytest.raises(ValueError, match="Feedback missing required keys"):
            await mutator.mutate(
                original_prompt="Test",
                strategy=AttackStrategyType.REPHRASE_SEMANTIC,
                iteration=1,
                feedback=incomplete_feedback
            )

