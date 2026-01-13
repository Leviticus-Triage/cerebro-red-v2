"""
Compare performance across all three providers.
"""
import pytest
import asyncio
from utils.llm_client import LLMClient, get_llm_client
from utils.config import get_settings

@pytest.mark.asyncio
async def test_provider_latency_comparison():
    """Compare latency across Ollama, Azure, OpenAI."""
    providers = ["ollama", "azure", "openai"]
    results = {}
    
    for provider in providers:
        try:
            # Get settings and check if provider is configured
            settings = get_settings()
            
            # Skip if provider is not configured
            if provider == "azure" and not settings.azure_openai.api_key:
                results[provider] = {"error": "Azure OpenAI not configured"}
                print(f"⏭  {provider}: Skipped (not configured)")
                continue
            if provider == "openai" and not settings.openai.api_key:
                results[provider] = {"error": "OpenAI not configured"}
                print(f"⏭  {provider}: Skipped (not configured)")
                continue
            
            # Temporarily set provider (for testing only)
            original_provider = settings.llm_provider.provider
            settings.llm_provider.provider = provider
            
            llm_client = get_llm_client()
            messages = [{"role": "user", "content": "Quick test"}]
            
            response = await llm_client.complete(messages, role="target")
            results[provider] = {
                "latency_ms": response.latency_ms,
                "model": response.model,
                "tokens": response.tokens_used
            }
            print(f" {provider}: {response.latency_ms}ms ({response.model})")
            
            # Restore original provider
            settings.llm_provider.provider = original_provider
        except Exception as e:
            results[provider] = {"error": str(e)}
            print(f" {provider}: {str(e)}")
    
    # Print comparison table
    print("\n Provider Comparison:")
    print(f"{'Provider':<15} {'Latency':<15} {'Model':<30}")
    print("-" * 60)
    for provider, data in results.items():
        if "error" not in data:
            print(f"{provider:<15} {data['latency_ms']:<15} {data['model']:<30}")

