"""
CORS and Authentication tests for CEREBRO-RED v2.

Tests:
1. OPTIONS preflight requests
2. CORS headers for all origins
3. API key authentication (enabled/disabled)
4. Unauthorized requests (401)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.mark.cors
def test_cors_preflight_request(client):
    """
    Test OPTIONS preflight request for CORS.
    
    Browser sends OPTIONS before actual request to check CORS policy.
    """
    response = client.options(
        "/api/experiments",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-api-key"
        }
    )
    
    # Should return 200 OK with CORS headers
    assert response.status_code == 200
    
    # Check CORS headers
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers
    
    # Verify allowed methods include POST
    allowed_methods = response.headers["access-control-allow-methods"]
    assert "POST" in allowed_methods
    
    print(f" CORS Preflight: {allowed_methods}")


@pytest.mark.cors
def test_cors_headers_on_actual_request(client):
    """
    Test that CORS headers are present on actual requests.
    """
    # Disable API key for this test
    with patch.dict(os.environ, {"API_KEY_ENABLED": "false"}):
        response = client.get(
            "/api/experiments",
            headers={"Origin": "http://localhost:5173"}
        )
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
        
        origin = response.headers["access-control-allow-origin"]
        assert origin in ["http://localhost:5173", "*"]
        
        print(f" CORS Headers present: Origin={origin}")


@pytest.mark.cors
def test_cors_multiple_origins(client):
    """
    Test CORS with multiple allowed origins.
    """
    test_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://cerebro-red.example.com"
    ]
    
    with patch.dict(os.environ, {"API_KEY_ENABLED": "false"}):
        for origin in test_origins:
            response = client.options(
                "/api/experiments",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET"
                }
            )
            
            # Should allow configured origins
            if origin in ["http://localhost:5173", "http://localhost:3000"]:
                assert response.status_code == 200
                print(f" Origin allowed: {origin}")
            else:
                # May or may not be allowed depending on config
                print(f"️  Origin {origin}: {response.status_code}")


@pytest.mark.auth
def test_api_key_disabled(client):
    """
    Test that API key is not required when disabled.
    """
    with patch.dict(os.environ, {"API_KEY_ENABLED": "false"}):
        # Should work without API key
        response = client.get("/api/experiments")
        
        # Should not return 401
        assert response.status_code != 401
        print(f" API Key disabled: {response.status_code}")


@pytest.mark.auth
def test_api_key_enabled_missing(client):
    """
    Test that API key is required when enabled.
    """
    with patch.dict(os.environ, {"API_KEY_ENABLED": "true", "API_KEY": "test-secret-key"}):
        # Request without API key
        response = client.get("/api/experiments")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        data = response.json()
        # Backend returns "error" or "detail" field
        error_msg = data.get("error") or data.get("detail", "")
        assert "API key" in error_msg or "API key" in str(data)
        
        print(" API Key required when enabled")


@pytest.mark.auth
def test_api_key_enabled_invalid(client):
    """
    Test that invalid API key is rejected.
    """
    with patch.dict(os.environ, {"API_KEY_ENABLED": "true", "API_KEY": "test-secret-key"}):
        # Request with invalid API key
        response = client.get(
            "/api/experiments",
            headers={"X-API-Key": "wrong-key"}
        )
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        
        data = response.json()
        # Backend returns "error" or "detail" field
        error_msg = data.get("error") or data.get("detail", "")
        assert "Invalid API key" in error_msg or "Invalid" in error_msg
        
        print(" Invalid API Key rejected")


@pytest.mark.auth
def test_api_key_enabled_valid(client):
    """
    Test that valid API key is accepted.
    """
    from utils.config import get_settings
    
    with patch.dict(os.environ, {"API_KEY_ENABLED": "true", "API_KEY": "test-secret-key"}):
        # Clear settings cache to force reload
        get_settings.cache_clear()
        
        # Request with valid API key
        response = client.get(
            "/api/experiments",
            headers={"X-API-Key": "test-secret-key"}
        )
        
        # Should not return 401
        assert response.status_code != 401, f"Expected non-401 status, got {response.status_code}: {response.text}"
        print(f" Valid API Key accepted: {response.status_code}")
        
        # Restore cache
        get_settings.cache_clear()


@pytest.mark.cors
@pytest.mark.auth
def test_cors_with_api_key(client):
    """
    Test CORS with API key authentication.
    """
    with patch.dict(os.environ, {"API_KEY_ENABLED": "true", "API_KEY": "test-secret-key"}):
        # Preflight request
        response = client.options(
            "/api/experiments",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "x-api-key,content-type"
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-headers" in response.headers
        
        # Actual request with API key
        response = client.post(
            "/api/experiments",
            json={
                "experiment_id": "test-id",
                "name": "CORS Test",
                "target_model_provider": "ollama",
                "target_model_name": "qwen2.5:3b",
                "attacker_model_provider": "ollama",
                "attacker_model_name": "qwen2.5:3b",
                "judge_model_provider": "ollama",
                "judge_model_name": "qwen2.5:7b",
                "initial_prompts": ["test"],
                "strategies": ["roleplay_injection"]
            },
            headers={
                "Origin": "http://localhost:5173",
                "X-API-Key": "test-secret-key"
            }
        )
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
        print(" CORS works with API Key authentication")


@pytest.mark.cors
def test_cors_credentials(client):
    """
    Test CORS with credentials (cookies, auth headers).
    """
    with patch.dict(os.environ, {"API_KEY_ENABLED": "false"}):
        response = client.get(
            "/api/experiments",
            headers={
                "Origin": "http://localhost:5173",
                "Cookie": "session=test"
            }
        )
        
        # Check if credentials are allowed
        if "access-control-allow-credentials" in response.headers:
            credentials = response.headers["access-control-allow-credentials"]
            print(f" CORS Credentials: {credentials}")
        else:
            print("️  CORS Credentials header not present")

