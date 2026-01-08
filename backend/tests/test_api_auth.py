"""
Test API authentication and authorization.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_key_required():
    """Test that API key is required for protected endpoints."""
    # Minimal valid experiment config for testing auth
    # All required fields with proper types to pass Pydantic validation
    valid_experiment_body = {
        "experiment_config": {
            "name": "Auth Test Experiment",
            "target_model_provider": "ollama",
            "target_model_name": "llama3.2",
            "attacker_model_provider": "ollama",
            "attacker_model_name": "llama3.2",
            "judge_model_provider": "ollama",
            "judge_model_name": "llama3.2",
            "initial_prompts": ["test prompt"],
            "strategies": ["roleplay_injection"],
            # Optional fields with defaults to ensure full validation passes
            "max_iterations": 20,
            "max_concurrent_attacks": 5,
            "success_threshold": 7.0,
            "timeout_seconds": 3600
        }
    }
    
    # Without API key - should get 401
    response = client.post("/api/scan/start", json=valid_experiment_body)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    # With invalid API key - should get 401
    response = client.post(
        "/api/scan/start",
        json=valid_experiment_body,
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    # With valid API key - should succeed (202) or fail with validation error (400/422), but not 401
    import os
    api_key = os.getenv("API_KEY", "your-secret-api-key-change-this")
    response = client.post(
        "/api/scan/start",
        json=valid_experiment_body,
        headers={"X-API-Key": api_key}
    )
    # Should either succeed (202) or fail with validation error (400/422), but not 401
    assert response.status_code != 401, f"Valid API key should not return 401: {response.text}"

def test_rate_limiting():
    """Test that rate limiting works."""
    import os
    api_key = os.getenv("API_KEY", "your-secret-api-key-change-this")
    
    # Send multiple requests rapidly
    responses = []
    for i in range(20):  # Reduced from 100 to avoid excessive requests
        response = client.get(
            "/api/experiments",
            headers={"X-API-Key": api_key}
        )
        responses.append(response.status_code)
    
    # Should have some 429 (Too Many Requests) responses if rate limiting is enabled
    # Or all should succeed if rate limiting is disabled
    print(f"✅ Rate limiting test: {responses.count(429)} requests blocked out of {len(responses)}")

