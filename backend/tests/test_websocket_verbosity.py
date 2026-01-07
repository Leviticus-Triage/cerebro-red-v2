"""
backend/tests/test_websocket_verbosity.py
==========================================

Tests for WebSocket verbosity filtering functionality.

Validates that:
- Events are filtered based on verbosity level
- Control messages update verbosity correctly
- Query parameter verbosity is respected
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi.websockets import WebSocketState

from api.websocket import ConnectionManager


@pytest.mark.asyncio
async def test_verbosity_filtering_level_0():
    """Test that only errors are sent at verbosity level 0."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    # Mock WebSocket with verbosity 0
    ws_mock = AsyncMock()
    ws_mock.client_state = WebSocketState.CONNECTED
    await manager.connect(experiment_id, ws_mock, verbosity=0)
    
    # Send error (min_verbosity=0) → Should be sent
    await manager.broadcast(experiment_id, {"type": "error", "message": "Test error"}, min_verbosity=0)
    assert ws_mock.send_json.called
    ws_mock.send_json.reset_mock()
    
    # Send LLM request (min_verbosity=2) → Should NOT be sent
    await manager.broadcast(experiment_id, {"type": "llm_request", "prompt": "test"}, min_verbosity=2)
    assert not ws_mock.send_json.called


@pytest.mark.asyncio
async def test_verbosity_filtering_level_2():
    """Test that LLM I/O is sent at verbosity level 2."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    # Mock WebSocket with verbosity 2
    ws_mock = AsyncMock()
    ws_mock.client_state = WebSocketState.CONNECTED
    await manager.connect(experiment_id, ws_mock, verbosity=2)
    
    # Send LLM request (min_verbosity=2) → Should be sent
    await manager.broadcast(experiment_id, {"type": "llm_request"}, min_verbosity=2)
    assert ws_mock.send_json.called
    ws_mock.send_json.reset_mock()
    
    # Send code flow (min_verbosity=3) → Should NOT be sent
    await manager.broadcast(experiment_id, {"type": "code_flow"}, min_verbosity=3)
    assert not ws_mock.send_json.called


@pytest.mark.asyncio
async def test_verbosity_filtering_level_3():
    """Test that all events are sent at verbosity level 3."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    # Mock WebSocket with verbosity 3
    ws_mock = AsyncMock()
    ws_mock.client_state = WebSocketState.CONNECTED
    await manager.connect(experiment_id, ws_mock, verbosity=3)
    
    # All events should be sent
    await manager.broadcast(experiment_id, {"type": "error"}, min_verbosity=0)
    assert ws_mock.send_json.called
    ws_mock.send_json.reset_mock()
    
    await manager.broadcast(experiment_id, {"type": "llm_request"}, min_verbosity=2)
    assert ws_mock.send_json.called
    ws_mock.send_json.reset_mock()
    
    await manager.broadcast(experiment_id, {"type": "code_flow"}, min_verbosity=3)
    assert ws_mock.send_json.called


@pytest.mark.asyncio
async def test_verbosity_control_message():
    """Test set_verbosity control message updates verbosity."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    # Connect with verbosity=1
    ws_mock = AsyncMock()
    ws_mock.client_state = WebSocketState.CONNECTED
    await manager.connect(experiment_id, ws_mock, verbosity=1)
    
    # Verify initial verbosity
    assert manager.get_verbosity(ws_mock) == 1
    
    # Update verbosity to 3
    manager.set_verbosity(ws_mock, 3)
    assert manager.get_verbosity(ws_mock) == 3


@pytest.mark.asyncio
async def test_multiple_connections_different_verbosity():
    """Test that different connections receive different events based on verbosity."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    # Connection 1: verbosity 0
    ws1 = AsyncMock()
    ws1.client_state = WebSocketState.CONNECTED
    await manager.connect(experiment_id, ws1, verbosity=0)
    
    # Connection 2: verbosity 2
    ws2 = AsyncMock()
    ws2.client_state = WebSocketState.CONNECTED
    await manager.connect(experiment_id, ws2, verbosity=2)
    
    # Send LLM request (min_verbosity=2)
    await manager.broadcast(experiment_id, {"type": "llm_request"}, min_verbosity=2)
    
    # ws1 should NOT receive (verbosity 0 < 2)
    assert not ws1.send_json.called
    
    # ws2 should receive (verbosity 2 >= 2)
    assert ws2.send_json.called


@pytest.mark.asyncio
async def test_verbosity_default_from_settings():
    """Test that default verbosity comes from settings."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    # Mock settings
    with patch('api.websocket.get_settings') as mock_settings:
        mock_settings.return_value.app.verbosity = 2
        
        ws_mock = AsyncMock()
        ws_mock.client_state = WebSocketState.CONNECTED
        await manager.connect(experiment_id, ws_mock)  # No verbosity specified
        
        # Should use default from settings (2)
        assert manager.get_verbosity(ws_mock) == 2


@pytest.mark.asyncio
async def test_verbosity_clamping():
    """Test that verbosity values are clamped to 0-3 range."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    ws_mock = AsyncMock()
    ws_mock.client_state = WebSocketState.CONNECTED
    
    # Test negative value (should clamp to 0)
    await manager.connect(experiment_id, ws_mock, verbosity=-1)
    assert manager.get_verbosity(ws_mock) >= 0
    
    # Test value > 3 (should clamp to 3)
    manager.set_verbosity(ws_mock, 5)
    assert manager.get_verbosity(ws_mock) <= 3


@pytest.mark.asyncio
async def test_dead_connection_cleanup():
    """Test that dead connections are removed."""
    manager = ConnectionManager()
    experiment_id = uuid4()
    
    ws_mock = AsyncMock()
    ws_mock.client_state = WebSocketState.DISCONNECTED  # Dead connection
    await manager.connect(experiment_id, ws_mock, verbosity=2)
    
    # Broadcast should remove dead connection
    await manager.broadcast(experiment_id, {"type": "test"}, min_verbosity=0)
    
    # Connection should be removed
    assert experiment_id not in manager.active_connections or ws_mock not in manager.active_connections[experiment_id]
