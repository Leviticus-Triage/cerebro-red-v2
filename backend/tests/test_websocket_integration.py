"""
Integration tests for WebSocket verbosity control.

Tests verify that WebSocket endpoint correctly handles verbosity control messages.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.mark.asyncio
async def test_websocket_verbosity_control():
    """Test WebSocket verbosity control via control messages."""
    client = TestClient(app)
    experiment_id = "test-experiment-id"
    
    with client.websocket_connect(f"/ws/scan/{experiment_id}?verbosity=1") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert data["verbosity"] == 1
        
        # Change verbosity to 3
        websocket.send_text("set_verbosity:3")
        
        # Receive confirmation
        data = websocket.receive_json()
        assert data["type"] == "verbosity_updated"
        assert data["verbosity"] == 3
        
        # Try invalid verbosity
        websocket.send_text("set_verbosity:5")
        
        # Receive error
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "Invalid verbosity" in data["error_message"]
