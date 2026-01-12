"""
Integration tests for demo mode configuration and routing.

Tests that demo mode is properly enabled/disabled via environment variables
and that demo router is conditionally registered.
"""

import pytest
import os
from unittest.mock import patch
from main import app
from utils.config import get_settings


def test_demo_mode_config_field_exists():
    """Test that demo_mode field exists in AppSettings."""
    settings = get_settings()
    assert hasattr(settings.app, "demo_mode")
    assert isinstance(settings.app.demo_mode, bool)


@patch.dict(os.environ, {"CEREBRO_DEMO_MODE": "true"})
def test_demo_mode_enabled_via_env():
    """Test that CEREBRO_DEMO_MODE=true enables demo mode."""
    # Clear cache to reload settings
    from utils.config import get_settings
    get_settings.cache_clear()
    
    settings = get_settings()
    assert settings.app.demo_mode is True
    
    # Restore
    get_settings.cache_clear()


@patch.dict(os.environ, {"CEREBRO_DEMO_MODE": "false"})
def test_demo_mode_disabled_via_env():
    """Test that CEREBRO_DEMO_MODE=false disables demo mode."""
    from utils.config import get_settings
    get_settings.cache_clear()
    
    settings = get_settings()
    assert settings.app.demo_mode is False
    
    # Restore
    get_settings.cache_clear()


def test_health_check_returns_demo_mode():
    """Test health check endpoint returns demo_mode status."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "demo_mode" in data
    assert isinstance(data["demo_mode"], bool)


def test_demo_endpoints_require_no_auth():
    """Test demo endpoints don't require API key authentication."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Try to access demo endpoint without API key
    response = client.get("/api/demo/experiments")
    
    # Should either work (if demo mode enabled) or 404 (if not)
    # But should NOT be 401 Unauthorized
    assert response.status_code != 401
