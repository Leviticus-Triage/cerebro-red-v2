"""
Tests for configuration management.
"""

import pytest
import os
from pathlib import Path

from utils.config import (
    get_settings,
    Settings,
    AppSettings,
    DatabaseSettings,
    LLMProviderSettings,
)


def test_get_settings_singleton():
    """Test that get_settings returns a singleton."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_app_settings_defaults():
    """Test AppSettings default values."""
    settings = AppSettings()
    assert settings.env == "development"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8889
    assert settings.debug is True


def test_database_settings_defaults():
    """Test DatabaseSettings default values."""
    settings = DatabaseSettings()
    assert "sqlite" in settings.url.lower()
    assert settings.echo is False


def test_get_llm_config_ollama():
    """Test getting LLM config for Ollama provider."""
    settings = get_settings()
    # Temporarily set provider to ollama
    original_provider = settings.llm_provider.provider
    settings.llm_provider.provider = "ollama"
    
    try:
        config = settings.get_llm_config("attacker")
        assert config["provider"] == "ollama"
        assert "model_name" in config
        assert "api_base" in config
    finally:
        settings.llm_provider.provider = original_provider


def test_validate_provider_config_ollama():
    """Test provider config validation for Ollama (no credentials required)."""
    settings = get_settings()
    original_provider = settings.llm_provider.provider
    settings.llm_provider.provider = "ollama"
    
    try:
        # Should not raise for Ollama
        settings.validate_provider_config()
    finally:
        settings.llm_provider.provider = original_provider


def test_validate_provider_config_azure_missing_key():
    """Test provider config validation fails for Azure without API key."""
    settings = get_settings()
    original_provider = settings.llm_provider.provider
    original_key = settings.azure_openai.api_key
    
    settings.llm_provider.provider = "azure"
    settings.azure_openai.api_key = None
    
    try:
        with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY"):
            settings.validate_provider_config()
    finally:
        settings.llm_provider.provider = original_provider
        settings.azure_openai.api_key = original_key

