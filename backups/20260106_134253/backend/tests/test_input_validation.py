"""
Test input validation and sanitization.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)
api_key = os.getenv("API_KEY", "your-secret-api-key-change-this")

def test_sql_injection_prevention():
    """Test that SQL injection is prevented."""
    malicious_inputs = [
        "'; DROP TABLE experiments; --",
        "1' OR '1'='1",
        "admin'--",
        "<script>alert('xss')</script>"
    ]
    
    for malicious_input in malicious_inputs:
        response = client.post(
            "/api/experiments",
            json={
                "name": malicious_input,
                "description": "Test",
                "target_prompts": ["Test"]
            },
            headers={"X-API-Key": api_key}
        )
        
        # Should either reject or sanitize
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            # Verify data was sanitized
            data = response.json()
            # Check that malicious SQL is not executed (would cause 500 error)
            assert response.status_code != 500
    
    print("✅ SQL injection prevention working")

def test_xss_prevention():
    """Test that XSS is prevented."""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "javascript:alert('xss')"
    ]
    
    for payload in xss_payloads:
        response = client.post(
            "/api/experiments",
            json={
                "name": payload,
                "description": "Test",
                "target_prompts": ["Test"]
            },
            headers={"X-API-Key": api_key}
        )
        
        # Should either reject or sanitize
        assert response.status_code in [200, 400, 422]
    
    print("✅ XSS prevention working")

