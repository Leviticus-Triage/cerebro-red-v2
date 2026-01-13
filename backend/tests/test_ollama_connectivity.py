"""
Test Ollama connectivity and model availability.
"""
import pytest
import asyncio
from utils.llm_client import get_llm_client
from utils.config import get_settings

@pytest.mark.asyncio
async def test_ollama_connection():
    """Test that Ollama is reachable and responds."""
    settings = get_settings()
    assert settings.llm_provider.provider == "ollama"
    
    llm_client = get_llm_client()
    
    # Simple completion test
    messages = [{"role": "user", "content": "Say 'test successful'"}]
    response = await llm_client.complete(messages, role="target")
    
    assert response is not None
    assert response.content is not None
    assert len(response.content) > 0
    assert response.provider.value == "ollama"
    print(f" Ollama connection successful: {response.model}")

@pytest.mark.asyncio
async def test_ollama_all_roles():
    """Test that all three roles (attacker, target, judge) work."""
    llm_client = get_llm_client()
    
    roles = ["attacker", "target", "judge"]
    for role in roles:
        messages = [{"role": "user", "content": f"Test for {role} role"}]
        response = await llm_client.complete(messages, role=role)
        assert response is not None
        print(f" {role.capitalize()} role working: {response.model}")

@pytest.mark.asyncio
async def test_ollama_latency():
    """Measure Ollama response latency."""
    llm_client = get_llm_client()
    messages = [{"role": "user", "content": "Quick test"}]
    
    response = await llm_client.complete(messages, role="target")
    
    assert response.latency_ms > 0
    print(f" Ollama latency: {response.latency_ms}ms")
    
    # Warn if latency is too high
    if response.latency_ms > 10000:  # 10 seconds
        print(f"️  Warning: High latency detected ({response.latency_ms}ms)")

