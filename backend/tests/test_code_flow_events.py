"""
Tests for code-flow event tracking (verbosity level 3).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from api.websocket import send_strategy_selection, send_mutation_start, send_judge_end, send_decision_point


@pytest.mark.asyncio
async def test_code_flow_events_sent_at_verbosity_3():
    """Test that code-flow events are sent when verbosity=3."""
    experiment_id = uuid4()
    
    with patch('api.websocket.manager.broadcast') as mock_broadcast:
        await send_strategy_selection(
            experiment_id=experiment_id,
            iteration=1,
            strategy="roleplay_injection",
            reasoning="Initial strategy",
            previous_score=None,
            threshold=7.0
        )
        
        # Verify message format
        assert mock_broadcast.called
        call_args = mock_broadcast.call_args
        assert call_args[0][0] == experiment_id  # First positional arg is experiment_id
        message = call_args[0][1]  # Second positional arg is message dict
        assert message['type'] == 'code_flow'
        assert message['event_type'] == 'strategy_selection'
        assert message['strategy'] == 'roleplay_injection'
        # Verify min_verbosity=3
        assert call_args[1]['min_verbosity'] == 3


@pytest.mark.asyncio
async def test_code_flow_websocket_message_format():
    """Test that code-flow WebSocket messages have correct format."""
    experiment_id = uuid4()
    
    with patch('api.websocket.manager.broadcast') as mock_broadcast:
        await send_mutation_start(
            experiment_id=experiment_id,
            iteration=2,
            strategy="obfuscation_base64",
            original_prompt="Test prompt"
        )
        
        # Verify message format
        assert mock_broadcast.called
        message = mock_broadcast.call_args[0][1]  # Second positional arg is message dict
        assert message['type'] == 'code_flow'
        assert message['event_type'] == 'mutation_start'
        assert message['strategy'] == 'obfuscation_base64'
        assert message['iteration'] == 2
        assert 'timestamp' in message


@pytest.mark.asyncio
async def test_judge_end_event_includes_all_scores():
    """Test that judge_end event includes all score breakdowns."""
    experiment_id = uuid4()
    
    with patch('api.websocket.manager.broadcast') as mock_broadcast:
        await send_judge_end(
            experiment_id=experiment_id,
            iteration=3,
            overall_score=7.5,
            all_scores={
                "jailbreak_success": 8.0,
                "harmful_content": 7.0,
                "hallucination": 6.0,
                "bias": 5.0,
                "logical_consistency": 6.5,
                "sycophancy": 7.5,
                "policy_violation": 8.5
            },
            reasoning="Test reasoning",
            latency_ms=150
        )
        
        # Verify message format
        assert mock_broadcast.called
        message = mock_broadcast.call_args[0][1]  # Second positional arg is message dict
        assert message['type'] == 'code_flow'
        assert message['event_type'] == 'judge_end'
        assert message['overall_score'] == 7.5
        assert len(message['all_scores']) == 7
        assert message['all_scores']['jailbreak_success'] == 8.0


@pytest.mark.asyncio
async def test_decision_point_event_format():
    """Test that decision_point events have correct format."""
    experiment_id = uuid4()
    
    with patch('api.websocket.manager.broadcast') as mock_broadcast:
        await send_decision_point(
            experiment_id=experiment_id,
            iteration=4,
            decision_type="threshold_check",
            condition="score (7.5) >= threshold (7.0)",
            decision_result=True,  # Changed from 'result' to 'decision_result'
            description="✅ SUCCESS - Vulnerability found!"
        )
        
        # Verify message format
        assert mock_broadcast.called
        message = mock_broadcast.call_args[0][1]  # Second positional arg is message dict
        assert message['type'] == 'code_flow'
        assert message['event_type'] == 'decision_point'
        assert message['decision_type'] == 'threshold_check'
        assert message['decision_result'] is True  # Changed from 'result' to 'decision_result'
        assert '✅ SUCCESS' in message['description']
