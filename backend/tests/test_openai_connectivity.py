"""
Test OpenAI connectivity and model availability.
"""
import pytest
import os
from utils.llm_client import get_llm_client
from utils.config import get_settings

@pytest.mark.skipif(
    os.getenv("DEFAULT_LLM_PROVIDER") != "openai" or not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI not configured"
)
@pytest.mark.asyncio
async def test_openai_connection():
    """Test that OpenAI is reachable."""
    settings = get_settings()
    assert settings.llm_provider.provider == "openai"
    assert settings.openai.api_key is not None
    
    llm_client = get_llm_client()
    messages = [{"role": "user", "content": "Test OpenAI connection"}]
    response = await llm_client.complete(messages, role="target")
    
    assert response is not None
    assert response.provider.value == "openai"
    print(f" OpenAI connection successful: {response.model}")

@pytest.mark.skipif(
    os.getenv("DEFAULT_LLM_PROVIDER") != "openai" or not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI not configured"
)
@pytest.mark.asyncio
async def test_openai_all_models():
    """Test all three OpenAI models."""
    llm_client = get_llm_client()
    settings = get_settings()
    
    roles = ["attacker", "target", "judge"]
    for role in roles:
        config = settings.get_llm_config(role)
        print(f"Testing {role}: {config['model_name']}")
        
        messages = [{"role": "user", "content": f"Test {role}"}]
        response = await llm_client.complete(messages, role=role)
        
        assert response is not None
        print(f" {role.capitalize()}: {response.model} (latency: {response.latency_ms}ms)")

@pytest.mark.skipif(
    os.getenv("DEFAULT_LLM_PROVIDER") != "openai" or not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI not configured"
)
@pytest.mark.asyncio
async def test_openai_latency():
    """Measure OpenAI API latency."""
    llm_client = get_llm_client()
    messages = [{"role": "user", "content": "Short test message"}]
    response = await llm_client.complete(messages, role="target")
    
    assert response.latency_ms > 0
    print(f" OpenAI latency: {response.latency_ms}ms")
    print(f" Tokens used: {response.tokens_used}")

