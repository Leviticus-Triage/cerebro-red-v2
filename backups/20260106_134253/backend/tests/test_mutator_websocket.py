"""
Unit tests for WebSocket event emission in PromptMutator.

Tests verify that the mutator correctly sends WebSocket events for
attacker LLM interactions during PAIR semantic rephrase operations.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from core.mutator import PromptMutator
from core.models import AttackStrategyType


@pytest.mark.asyncio
async def test_mutator_sends_websocket_events_for_attacker_llm():
    """Test that mutator sends WebSocket events for attacker LLM calls."""
    experiment_id = uuid4()
    
    # Mock dependencies
    mock_llm_client = AsyncMock()
    mock_llm_client.settings.get_llm_config.return_value = {
        "provider": "ollama",
        "model_name": "qwen3:8b"
    }
    mock_llm_client.complete.return_value = MagicMock(
        content="Rephrased prompt",
        model="qwen3:8b",
        provider=MagicMock(value="ollama"),
        latency_ms=150,
        tokens_used=50
    )
    
    mock_audit_logger = MagicMock()
    
    mutator = PromptMutator(
        llm_client=mock_llm_client,
        audit_logger=mock_audit_logger,
        experiment_id=experiment_id
    )
    
    # Mock WebSocket functions
    with patch('api.websocket.send_llm_request', new_callable=AsyncMock) as mock_request, \
         patch('api.websocket.send_llm_response', new_callable=AsyncMock) as mock_response:
        
        # Call mutate with REPHRASE_SEMANTIC strategy
        feedback = {
            "target_response": "I cannot help with that",
            "judge_score": 3.5,
            "judge_reasoning": "Partial refusal detected"
        }
        
        result = await mutator._mutate_rephrase_semantic(
            prompt="Original prompt",
            feedback=feedback,
            iteration=2
        )
        
        # Verify WebSocket events were sent
        assert mock_request.called, "send_llm_request should be called"
        assert mock_response.called, "send_llm_response should be called"
        
        # Verify request event parameters
        request_call = mock_request.call_args
        assert request_call.kwargs['experiment_id'] == experiment_id
        assert request_call.kwargs['role'] == 'attacker'
        assert request_call.kwargs['iteration'] == 2
        
        # Verify response event parameters
        response_call = mock_response.call_args
        assert response_call.kwargs['experiment_id'] == experiment_id
        assert response_call.kwargs['role'] == 'attacker'
        assert response_call.kwargs['latency_ms'] == 150
        assert response_call.kwargs['tokens'] == 50


@pytest.mark.asyncio
async def test_mutator_sends_error_event_on_llm_failure():
    """Test that mutator sends error event when attacker LLM fails."""
    experiment_id = uuid4()
    
    # Mock LLM client to raise exception
    mock_llm_client = AsyncMock()
    mock_llm_client.settings.get_llm_config.return_value = {
        "provider": "ollama",
        "model_name": "qwen3:8b"
    }
    mock_llm_client.complete.side_effect = RuntimeError("LLM timeout")
    
    mock_audit_logger = MagicMock()
    
    mutator = PromptMutator(
        llm_client=mock_llm_client,
        audit_logger=mock_audit_logger,
        experiment_id=experiment_id
    )
    
    # Mock WebSocket functions
    with patch('api.websocket.send_llm_request', new_callable=AsyncMock), \
         patch('api.websocket.send_llm_error', new_callable=AsyncMock) as mock_error:
        
        feedback = {
            "target_response": "I cannot help",
            "judge_score": 2.0,
            "judge_reasoning": "Strong refusal"
        }
        
        # Should not raise, should fallback
        result = await mutator._mutate_rephrase_semantic(
            prompt="Test prompt",
            feedback=feedback,
            iteration=3
        )
        
        # Verify error event was sent
        assert mock_error.called, "send_llm_error should be called on LLM failure"
        error_call = mock_error.call_args
        assert error_call.kwargs['experiment_id'] == experiment_id
        assert error_call.kwargs['role'] == 'attacker'
        assert 'timeout' in error_call.kwargs['error_message'].lower()
