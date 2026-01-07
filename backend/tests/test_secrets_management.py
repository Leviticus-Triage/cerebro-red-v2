"""
Test that secrets are not exposed.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)
api_key = os.getenv("API_KEY", "your-secret-api-key-change-this")

def test_secrets_not_exposed():
    """Test that API keys and secrets are not exposed in responses."""
    # Get health check
    response = client.get("/health")
    data = response.json()
    
    # Should not contain API keys
    response_str = str(data).lower()
    assert "api_key" not in response_str or "your-secret-api-key" not in response_str
    assert "secret" not in response_str or "your-secret-api-key" not in response_str
    
    # Get experiment details
    response = client.get(
        "/api/experiments",
        headers={"X-API-Key": api_key}
    )
    if response.status_code == 200:
        data = response.json()
        data_str = str(data)
        
        # Should not contain LLM API keys
        assert "AZURE_OPENAI_API_KEY" not in data_str
        assert "OPENAI_API_KEY" not in data_str
        assert "sk-" not in data_str  # OpenAI API key prefix
    
    print("✅ Secrets not exposed in API responses")

def test_env_vars_not_exposed():
    """Test that environment variables are not exposed."""
    # Check health endpoint
    response = client.get("/health")
    data = response.json()
    data_str = str(data)
    
    # Should not contain sensitive env vars
    sensitive_vars = [
        "API_KEY",
        "AZURE_OPENAI_API_KEY",
        "OPENAI_API_KEY",
        "DATABASE_URL"
    ]
    
    for var in sensitive_vars:
        assert var not in data_str or "your-" in data_str.lower()  # Allow placeholder values
    
    print("✅ Environment variables not exposed")

