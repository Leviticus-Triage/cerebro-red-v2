"""
backend/tests/test_error_logging.py
====================================

Tests for error logging and traceback functionality.
"""

import pytest
import logging
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_logging_configuration():
    """Test that logging is configured with DEBUG level."""
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG, f"Expected DEBUG (10), got {root_logger.level}"
    
    # Test that handlers have formatters
    assert len(root_logger.handlers) > 0, "No handlers configured"
    for handler in root_logger.handlers:
        assert handler.formatter is not None, "Handler missing formatter"


def test_debug_endpoint_force_error():
    """Test that forced errors produce traceback in logs."""
    # Debug endpoints no longer require API key or debug mode
    response = client.post("/api/debug/force-error?error_type=value")
    
    assert response.status_code == 500
    assert "ValueError" in response.json()["detail"]["error_type"]
    assert "traceback" in response.json()["detail"]
    assert "forced ValueError" in response.json()["detail"]["error_message"]


def test_debug_endpoint_test_logging():
    """Test that all log levels work."""
    response = client.get("/api/debug/test-logging")
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["log_level"] == "DEBUG"
    assert "DEBUG" in data["expected_logs"]
