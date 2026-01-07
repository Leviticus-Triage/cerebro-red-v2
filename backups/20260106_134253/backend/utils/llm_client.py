"""
backend/utils/llm_client.py
============================

LLM client wrapper using litellm for multi-provider support.

Provides unified interface for Ollama, Azure OpenAI, and OpenAI with:
- Automatic provider routing based on role (attacker/target/judge)
- Exponential backoff retry logic
- Comprehensive error handling
- Latency and token usage tracking
"""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

import litellm
from litellm import acompletion
from pydantic import BaseModel, Field

from core.models import LLMProvider
from utils.config import get_settings
from utils.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenError
from utils.verbose_logging import verbose_logger


# ============================================================================
# Response Models
# ============================================================================

class LLMResponse(BaseModel):
    """Structured response from LLM API."""
    
    content: str = Field(..., description="Generated content")
    model: str = Field(..., description="Model identifier used")
    provider: LLMProvider = Field(..., description="LLM provider")
    tokens_used: Optional[int] = Field(None, ge=0, description="Tokens used")
    latency_ms: int = Field(..., ge=0, description="Request latency in milliseconds")
    finish_reason: str = Field(..., description="Finish reason (stop, length, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ============================================================================
# LLM Client Class
# ============================================================================

class LLMClient:
    """
    Unified LLM client for multi-provider support.
    
    This client abstracts over litellm to provide a consistent interface
    for calling LLMs from different providers (Ollama, Azure OpenAI, OpenAI).
    It handles provider-specific configuration, error handling, and retries.
    
    Attributes:
        settings: Application settings instance
        retry_attempts: Number of retry attempts (default: 3)
        
    Example:
        >>> client = LLMClient()
        >>> response = await client.complete(
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     role="attacker"
        ... )
    """
    
    def __init__(self, retry_attempts: int = 3):
        """
        Initialize LLM client.
        
        Args:
            retry_attempts: Number of retry attempts for failed requests (default: 3)
        """
        self.settings = get_settings()
        self.retry_attempts = retry_attempts
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        role: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Complete a chat conversation with LLM.
        
        Args:
            messages: List of message dicts with "role" and "content" keys
            role: One of "attacker", "target", or "judge"
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens to generate (optional)
            **kwargs: Additional parameters passed to litellm
            
        Returns:
            LLMResponse with generated content and metadata
            
        Raises:
            ValueError: If role is invalid or provider config is incomplete
            litellm.exceptions.RateLimitError: If rate limit exceeded after retries
            litellm.exceptions.Timeout: If request times out after retries
            litellm.exceptions.AuthenticationError: If authentication fails
        """
        if role not in ["attacker", "target", "judge"]:
            raise ValueError(f"Invalid role: {role}. Must be 'attacker', 'target', or 'judge'")
        
        # Get provider configuration
        config = self.settings.get_llm_config(role)
        provider = LLMProvider(config["provider"])
        model_name = config["model_name"]
        
        # Get circuit breaker for provider
        circuit_breaker = get_circuit_breaker(provider.value)
        
        # Build litellm model string
        if provider == LLMProvider.OLLAMA:
            model_string = f"ollama/{model_name}"
            api_base = config.get("api_base")
        elif provider == LLMProvider.AZURE:
            model_string = f"azure/{model_name}"
            # Set Azure environment variables
            if "api_key" in config:
                os.environ["AZURE_API_KEY"] = config["api_key"]
            if "api_base" in config:
                os.environ["AZURE_API_BASE"] = config["api_base"]
            if "api_version" in config:
                os.environ["AZURE_API_VERSION"] = config["api_version"]
        elif provider == LLMProvider.OPENAI:
            model_string = f"openai/{model_name}"
            # Set OpenAI environment variable
            if "api_key" in config:
                os.environ["OPENAI_API_KEY"] = config["api_key"]
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Prepare request parameters
        request_params = {
            "model": model_string,
            "messages": messages,
            "temperature": temperature,
            **kwargs,
        }
        
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        if provider == LLMProvider.OLLAMA and "api_base" in config:
            request_params["api_base"] = config["api_base"]
        
        # Execute request with circuit breaker and retry logic
        start_time = time.time()
        last_error = None
        
        # Log LLM request
        prompt_preview = messages[-1]["content"] if messages else ""
        verbose_logger.llm_request(
            provider=provider.value,
            model=model_name,
            role=role,
            prompt=prompt_preview,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Wrap the actual API call in circuit breaker
        async def _call_llm():
            return await acompletion(**request_params)
        
        for attempt in range(self.retry_attempts):
            try:
                # Call through circuit breaker
                response = await circuit_breaker.call_async(_call_llm)
                
                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Extract response data
                choice = response.choices[0]
                content = choice.message.content or ""
                finish_reason = choice.finish_reason or "unknown"
                
                # Extract token usage
                tokens_used = None
                if hasattr(response, "usage"):
                    tokens_used = response.usage.total_tokens
                
                # Log successful response
                verbose_logger.llm_response(
                    provider=provider.value,
                    model=model_name,
                    role=role,
                    response=content,
                    latency_ms=latency_ms,
                    tokens=tokens_used,
                    attempt=attempt + 1,
                    finish_reason=finish_reason
                )
                
                return LLMResponse(
                    content=content,
                    model=model_name,
                    provider=provider,
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    finish_reason=finish_reason,
                    metadata={
                        "model_string": model_string,
                        "attempt": attempt + 1,
                    },
                )
            
            except CircuitBreakerOpenError as e:
                # Circuit breaker is open, don't retry
                verbose_logger.llm_error(
                    provider=provider.value,
                    model=model_name,
                    role=role,
                    error=f"Circuit breaker OPEN: {str(e)}",
                    attempt=attempt + 1
                )
                raise RuntimeError(f"Circuit breaker is OPEN for {provider.value}: {str(e)}") from e
            except litellm.RateLimitError as e:
                last_error = e
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff for rate limits
                    delay = (2 ** attempt) * self.settings.pair_algorithm.backoff_base_delay
                    delay = min(delay, self.settings.pair_algorithm.backoff_max_delay)
                    await asyncio.sleep(delay)
                else:
                    raise
            
            except litellm.Timeout as e:
                last_error = e
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff for timeouts
                    delay = (2 ** attempt) * self.settings.pair_algorithm.backoff_base_delay
                    delay = min(delay, self.settings.pair_algorithm.backoff_max_delay)
                    await asyncio.sleep(delay)
                else:
                    raise
            
            except litellm.AuthenticationError as e:
                # Don't retry authentication errors
                raise ValueError(f"Authentication failed for {provider.value}: {str(e)}") from e
            
            except litellm.APIError as e:
                last_error = e
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff for API errors
                    delay = (2 ** attempt) * self.settings.pair_algorithm.backoff_base_delay
                    delay = min(delay, self.settings.pair_algorithm.backoff_max_delay)
                    await asyncio.sleep(delay)
                else:
                    raise
            
            except Exception as e:
                # Unexpected errors
                raise RuntimeError(f"Unexpected error calling LLM: {str(e)}") from e
        
        # If we get here, all retries failed
        raise RuntimeError(f"Failed after {self.retry_attempts} attempts: {str(last_error)}")
    
    async def health_check(self, provider: LLMProvider) -> bool:
        """
        Test connection to a specific provider.
        
        Args:
            provider: Provider to test
            
        Returns:
            True if provider is accessible, False otherwise
            
        Note:
            This method does not mutate global settings. It constructs
            a local request using the specified provider without affecting
            the default provider configuration.
        """
        try:
            # Get provider-specific configuration without mutating settings
            if provider == LLMProvider.OLLAMA:
                model_name = self.settings.ollama.model_target
                model_string = f"ollama/{model_name}"
                api_base = self.settings.ollama.base_url
            elif provider == LLMProvider.AZURE:
                model_name = self.settings.azure_openai.model_target
                model_string = f"azure/{model_name}"
                # Set Azure environment variables temporarily (only for this request)
                import os
                original_azure_key = os.environ.get("AZURE_API_KEY")
                original_azure_base = os.environ.get("AZURE_API_BASE")
                original_azure_version = os.environ.get("AZURE_API_VERSION")
                try:
                    if self.settings.azure_openai.api_key:
                        os.environ["AZURE_API_KEY"] = self.settings.azure_openai.api_key
                    if self.settings.azure_openai.endpoint:
                        os.environ["AZURE_API_BASE"] = self.settings.azure_openai.endpoint
                    if self.settings.azure_openai.api_version:
                        os.environ["AZURE_API_VERSION"] = self.settings.azure_openai.api_version
                    api_base = None
                except Exception:
                    # Restore on error
                    if original_azure_key:
                        os.environ["AZURE_API_KEY"] = original_azure_key
                    elif "AZURE_API_KEY" in os.environ:
                        del os.environ["AZURE_API_KEY"]
                    if original_azure_base:
                        os.environ["AZURE_API_BASE"] = original_azure_base
                    elif "AZURE_API_BASE" in os.environ:
                        del os.environ["AZURE_API_BASE"]
                    if original_azure_version:
                        os.environ["AZURE_API_VERSION"] = original_azure_version
                    elif "AZURE_API_VERSION" in os.environ:
                        del os.environ["AZURE_API_VERSION"]
                    raise
            elif provider == LLMProvider.OPENAI:
                model_name = self.settings.openai.model_target
                model_string = f"openai/{model_name}"
                # Set OpenAI environment variable temporarily
                import os
                original_openai_key = os.environ.get("OPENAI_API_KEY")
                try:
                    if self.settings.openai.api_key:
                        os.environ["OPENAI_API_KEY"] = self.settings.openai.api_key
                    api_base = None
                except Exception:
                    # Restore on error
                    if original_openai_key:
                        os.environ["OPENAI_API_KEY"] = original_openai_key
                    elif "OPENAI_API_KEY" in os.environ:
                        del os.environ["OPENAI_API_KEY"]
                    raise
            else:
                return False
            
            # Build request parameters without mutating settings
            request_params = {
                "model": model_string,
                "messages": [{"role": "user", "content": "test"}],
                "temperature": 0.7,
                "max_tokens": 5,
            }
            
            if api_base:
                request_params["api_base"] = api_base
            
            # Execute request directly via litellm
            response = await acompletion(**request_params)
            
            # Restore environment variables if they were modified
            if provider == LLMProvider.AZURE:
                import os
                if original_azure_key:
                    os.environ["AZURE_API_KEY"] = original_azure_key
                elif "AZURE_API_KEY" in os.environ:
                    del os.environ["AZURE_API_KEY"]
                if original_azure_base:
                    os.environ["AZURE_API_BASE"] = original_azure_base
                elif "AZURE_API_BASE" in os.environ:
                    del os.environ["AZURE_API_BASE"]
                if original_azure_version:
                    os.environ["AZURE_API_VERSION"] = original_azure_version
                elif "AZURE_API_VERSION" in os.environ:
                    del os.environ["AZURE_API_VERSION"]
            elif provider == LLMProvider.OPENAI:
                import os
                if original_openai_key:
                    os.environ["OPENAI_API_KEY"] = original_openai_key
                elif "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]
            
            return response.choices[0].message.content is not None
        
        except Exception:
            return False
    
    async def list_models(self, provider: LLMProvider) -> List[str]:
        """
        Get list of available models for a provider.
        
        Args:
            provider: Provider to query
            
        Returns:
            List of model names
            
        Note:
            This is a placeholder implementation. Actual implementation
            would query provider-specific APIs.
        """
        if provider == LLMProvider.OLLAMA:
            # Would use Ollama API to list models
            return ["qwen3:8b", "qwen3:14b", "llama2:7b"]
        elif provider == LLMProvider.AZURE:
            # Would use Azure OpenAI API to list models
            return ["gpt-4", "gpt-35-turbo"]
        elif provider == LLMProvider.OPENAI:
            # Would use OpenAI API to list models
            return ["gpt-4-turbo-preview", "gpt-3.5-turbo"]
        else:
            return []
    
    def get_provider_config(self, provider: LLMProvider) -> Dict[str, Any]:
        """
        Get provider-specific configuration.
        
        Args:
            provider: Provider to get config for
            
        Returns:
            Dictionary with provider configuration
        """
        if provider == LLMProvider.OLLAMA:
            return {
                "base_url": self.settings.ollama.base_url,
                "models": {
                    "attacker": self.settings.ollama.model_attacker,
                    "target": self.settings.ollama.model_target,
                    "judge": self.settings.ollama.model_judge,
                },
                "timeout": self.settings.ollama.timeout,
            }
        elif provider == LLMProvider.AZURE:
            return {
                "endpoint": self.settings.azure_openai.endpoint,
                "api_version": self.settings.azure_openai.api_version,
                "models": {
                    "attacker": self.settings.azure_openai.model_attacker,
                    "target": self.settings.azure_openai.model_target,
                    "judge": self.settings.azure_openai.model_judge,
                },
            }
        elif provider == LLMProvider.OPENAI:
            return {
                "models": {
                    "attacker": self.settings.openai.model_attacker,
                    "target": self.settings.openai.model_target,
                    "judge": self.settings.openai.model_judge,
                },
                "timeout": self.settings.openai.timeout,
            }
        else:
            return {}


# ============================================================================
# Singleton Pattern
# ============================================================================

_llm_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get singleton LLMClient instance.
    
    Returns:
        Cached LLMClient instance
        
    Example:
        >>> client = get_llm_client()
        >>> response = await client.complete(...)
    """
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient()
    return _llm_client_instance
