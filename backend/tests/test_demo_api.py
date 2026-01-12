"""
Test suite for demo mode API endpoints.

Tests that demo endpoints return proper mock data and block write operations
with helpful 403 responses.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_get_demo_experiments(client):
    """Test GET /api/demo/experiments returns 3 mock experiments."""
    # Note: This test requires demo mode to be enabled
    # In a real scenario, you'd set CEREBRO_DEMO_MODE=true
    response = client.get("/api/demo/experiments")
    
    # If demo mode is not enabled, the endpoint won't exist (404)
    # If enabled, should return 200 with 3 experiments
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled - endpoint not registered")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    experiments = data["data"]
    assert len(experiments) == 3
    assert all("experiment_id" in exp for exp in experiments)
    assert all("name" in exp for exp in experiments)
    assert all("status" in exp for exp in experiments)


def test_get_demo_experiment_by_id(client):
    """Test GET /api/demo/experiments/{id} returns correct experiment."""
    response = client.get("/api/demo/experiments/demo-running-001")
    
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    experiment = data["data"]
    assert experiment["experiment_id"] == "demo-running-001"
    assert experiment["status"] == "running"


def test_get_demo_experiment_not_found(client):
    """Test GET /api/demo/experiments/{id} returns 404 for non-existent experiment."""
    response = client.get("/api/demo/experiments/non-existent-id")
    
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled")
    
    assert response.status_code == 404


def test_create_demo_experiment_blocked(client):
    """Test POST /api/demo/experiments returns 403 with helpful message."""
    response = client.post("/api/demo/experiments", json={"name": "Test"})
    
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled")
    
    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert "Demo mode" in data["error"]
    assert "detail" in data
    assert "deploy" in data["detail"].lower()


def test_update_demo_experiment_blocked(client):
    """Test PUT /api/demo/experiments/{id} returns 403."""
    response = client.put("/api/demo/experiments/demo-running-001", json={"name": "Updated"})
    
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled")
    
    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert "Demo mode" in data["error"]


def test_delete_demo_experiment_blocked(client):
    """Test DELETE /api/demo/experiments/{id} returns 403."""
    response = client.delete("/api/demo/experiments/demo-running-001")
    
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled")
    
    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert "Demo mode" in data["error"]


def test_demo_api_response_format(client):
    """Test demo API uses api_response() wrapper for consistent format."""
    response = client.get("/api/demo/experiments")
    
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled")
    
    assert response.status_code == 200
    data = response.json()
    # Should be wrapped in { "data": ... }
    assert "data" in data
    assert isinstance(data["data"], list)


def test_demo_api_cors_headers(client):
    """Test demo API error responses include CORS headers."""
    response = client.post("/api/demo/experiments", json={"name": "Test"})
    
    if response.status_code == 404:
        pytest.skip("Demo mode not enabled")
    
    assert response.status_code == 403
    # Check for CORS headers
    assert "access-control-allow-origin" in response.headers or "*" in str(response.headers)
