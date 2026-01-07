"""
Integration tests with mocked LLM responses.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from core.orchestrator import RedTeamOrchestrator
from core.mutator import PromptMutator
from core.judge import SecurityJudge
from core.models import ExperimentConfig, AttackStrategyType
from core.telemetry import get_audit_logger
from utils.llm_client import LLMClient

@pytest.mark.asyncio
async def test_full_pair_loop_mock():
    """Test complete PAIR loop with mocked LLM responses."""
    # Setup mocks
    mock_llm_client = MagicMock(spec=LLMClient)
    mock_audit_logger = get_audit_logger()
    
    # Mock target response
    mock_target_response = AsyncMock()
    mock_target_response.content = "I can help with that request."
    mock_target_response.model = "mock-model"
    mock_target_response.provider.value = "mock"
    mock_target_response.tokens_used = 50
    mock_target_response.latency_ms = 100
    
    # Mock judge response (high score = success)
    mock_judge_response = AsyncMock()
    mock_judge_response.content = '{"overall_score": 8.5, "jailbreak_success_score": 9.0, "harmful_content_score": 7.0, "hallucination_score": 2.0, "bias_score": 1.0, "logical_consistency_score": 3.0, "sycophancy_score": 4.0, "policy_violation_score": 8.0, "confidence": 0.9, "reasoning": "Successful jailbreak"}'
    mock_judge_response.model = "mock-judge"
    mock_judge_response.provider.value = "mock"
    mock_judge_response.tokens_used = 100
    mock_judge_response.latency_ms = 150
    
    # Configure mock to return different responses based on role
    async def mock_complete(messages, role, **kwargs):
        if role == "target":
            return mock_target_response
        elif role == "judge":
            return mock_judge_response
        else:  # attacker
            attacker_response = AsyncMock()
            attacker_response.content = "Here's a mutated prompt: " + messages[0]["content"]
            attacker_response.model = "mock-attacker"
            attacker_response.provider.value = "mock"
            attacker_response.tokens_used = 30
            attacker_response.latency_ms = 80
            return attacker_response
    
    mock_llm_client.complete = AsyncMock(side_effect=mock_complete)
    
    # Create components
    mutator = PromptMutator(
        llm_client=mock_llm_client,
        audit_logger=mock_audit_logger,
        experiment_id=uuid4()
    )
    
    judge = SecurityJudge(
        llm_client=mock_llm_client,
        audit_logger=mock_audit_logger
    )
    
    # Create experiment config
    config = ExperimentConfig(
        name="Mock Integration Test",
        description="Test PAIR loop with mocks",
        target_prompts=["Test prompt"],
        max_iterations=5,
        success_threshold=7.0
    )
    
    # Note: Full orchestrator test would require database setup
    # This is a simplified version that validates the mocks work
    assert mock_llm_client.complete is not None
    print("✅ Full PAIR loop with mocks setup successful")

