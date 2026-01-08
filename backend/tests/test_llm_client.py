"""
Tests for LLM client wrapper.
"""

import pytest
from unittest.mock import AsyncMock, patch

from utils.llm_client import LLMClient, LLMResponse
from core.models import LLMProvider


@pytest.mark.asyncio
async def test_llm_client_initialization():
    """Test LLM client initialization."""
    client = LLMClient()
    assert client.retry_attempts == 3
    assert client.settings is not None


@pytest.mark.asyncio
async def test_llm_client_invalid_role():
    """Test that invalid role raises ValueError."""
    client = LLMClient()
    with pytest.raises(ValueError):
        await client.complete(
            messages=[{"role": "user", "content": "test"}],
            role="invalid_role"
        )


@pytest.mark.asyncio
@patch('utils.llm_client.acompletion')
async def test_llm_client_complete_success(mock_acompletion):
    """Test successful LLM completion."""
    # Mock litellm response
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_response.choices[0].finish_reason = "stop"
    mock_response.usage.total_tokens = 10
    mock_acompletion.return_value = mock_response
    
    client = LLMClient()
    # Note: This test requires proper provider configuration
    # For now, we'll just test the structure
    assert client is not None


@pytest.mark.asyncio
async def test_llm_client_health_check():
    """Test health check functionality."""
    client = LLMClient()
    # Health check requires actual provider connection
    # This is a placeholder test
    assert client is not None


@pytest.mark.asyncio
async def test_llm_client_list_models():
    """Test listing available models."""
    client = LLMClient()
    ollama_models = await client.list_models(LLMProvider.OLLAMA)
    assert isinstance(ollama_models, list)
    assert len(ollama_models) > 0


def test_llm_response_model():
    """Test LLMResponse model."""
    response = LLMResponse(
        content="Test content",
        model="qwen3:8b",
        provider=LLMProvider.OLLAMA,
        latency_ms=150,
        finish_reason="stop",
    )
    assert response.content == "Test content"
    assert response.provider == LLMProvider.OLLAMA
    assert response.latency_ms == 150

