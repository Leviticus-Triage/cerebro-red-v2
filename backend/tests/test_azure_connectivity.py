"""
Test Azure OpenAI connectivity and model availability.
"""
import pytest
import os
from utils.llm_client import get_llm_client
from utils.config import get_settings

@pytest.mark.skipif(
    os.getenv("DEFAULT_LLM_PROVIDER") != "azure",
    reason="Azure OpenAI not configured"
)
@pytest.mark.asyncio
async def test_azure_connection():
    """Test that Azure OpenAI is reachable."""
    settings = get_settings()
    assert settings.llm_provider.provider == "azure"
    assert settings.azure_openai.api_key is not None
    
    llm_client = get_llm_client()
    messages = [{"role": "user", "content": "Test Azure connection"}]
    response = await llm_client.complete(messages, role="target")
    
    assert response is not None
    assert response.provider.value == "azure"
    print(f" Azure OpenAI connection successful: {response.model}")

@pytest.mark.skipif(
    os.getenv("DEFAULT_LLM_PROVIDER") != "azure",
    reason="Azure OpenAI not configured"
)
@pytest.mark.asyncio
async def test_azure_all_models():
    """Test all three Azure models."""
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
    os.getenv("DEFAULT_LLM_PROVIDER") != "azure",
    reason="Azure OpenAI not configured"
)
@pytest.mark.asyncio
async def test_azure_cost_estimation():
    """Estimate Azure OpenAI costs per request."""
    llm_client = get_llm_client()
    messages = [{"role": "user", "content": "Short test message"}]
    response = await llm_client.complete(messages, role="target")
    
    # GPT-3.5-Turbo pricing (approximate)
    input_cost_per_1k = 0.0005  # $0.0005 per 1K input tokens
    output_cost_per_1k = 0.0015  # $0.0015 per 1K output tokens
    
    estimated_cost = (
        (response.tokens_used / 1000) * input_cost_per_1k +
        (response.tokens_used / 1000) * output_cost_per_1k
    )
    
    print(f" Tokens used: {response.tokens_used}")
    print(f" Estimated cost: ${estimated_cost:.6f}")

