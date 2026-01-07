"""
backend/utils/config.py
=======================

Configuration management for CEREBRO-RED v2 using Pydantic Settings.

Loads all configuration from environment variables with type-safe validation
and provides singleton access pattern for application-wide settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application-level settings (host, port, debug, logging, verbosity)."""
    
    model_config = SettingsConfigDict(env_prefix="CEREBRO_", case_sensitive=False)
    
    env: str = Field(default="development", description="Environment (development/production)")
    host: str = Field(default="0.0.0.0", description="Host to bind server")
    port: int = Field(default=9000, ge=1, le=65535, description="Port to bind server")
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Verbosity Levels (used for WebSocket event filtering):
    # 0 = Minimal (nur Errors, Vulnerabilities)
    # 1 = Normal (+ Warnings, Events, Progress, Iteration Complete)
    # 2 = Verbose (+ LLM Requests/Responses, Judge Evaluations, Attack Mutations)
    # 3 = Debug (+ Full Code Flow: strategy_select, mutate_start/end, judge_start/end - Phase 4)
    verbosity: int = Field(default=2, ge=0, le=3, description="Verbosity level (0-3)")
    
    # Live Stream Settings
    stream_llm_output: bool = Field(default=True, description="Stream LLM outputs to logs")
    stream_code_flow: bool = Field(default=True, description="Log code flow events")


class DatabaseSettings(BaseSettings):
    """Database connection settings."""
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False)
    
    url: str = Field(
        default="sqlite+aiosqlite:///./data/experiments/cerebro.db",
        description="Database connection URL"
    )
    echo: bool = Field(default=False, description="Echo SQL queries")


class TelemetrySettings(BaseSettings):
    """Telemetry and audit logging settings."""
    
    model_config = SettingsConfigDict(env_prefix="AUDIT_LOG_", case_sensitive=False)
    
    path: Path = Field(
        default=Path("./data/audit_logs"),
        description="Path to audit log directory"
    )
    rotation: str = Field(default="daily", description="Log rotation schedule")
    retention_days: int = Field(default=90, ge=1, description="Log retention in days")


class LLMProviderSettings(BaseSettings):
    """LLM provider selection settings."""
    
    model_config = SettingsConfigDict(env_prefix="DEFAULT_LLM_", case_sensitive=False)
    
    provider: Literal["ollama", "azure", "openai"] = Field(
        default="ollama",
        description="Default LLM provider"
    )


class OllamaSettings(BaseSettings):
    """Ollama provider configuration."""
    
    model_config = SettingsConfigDict(env_prefix="OLLAMA_", case_sensitive=False)
    
    base_url: str = Field(
        default="http://host.docker.internal:11434",
        description="Ollama API base URL"
    )
    model_attacker: str = Field(default="qwen3:8b", description="Attacker model name")
    model_target: str = Field(default="qwen3:8b", description="Target model name")
    model_judge: str = Field(default="qwen3:14b", description="Judge model name")
    timeout: int = Field(default=300, ge=1, description="Request timeout in seconds")


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI provider configuration."""
    
    model_config = SettingsConfigDict(env_prefix="AZURE_OPENAI_", case_sensitive=False)
    
    api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint URL")
    api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )
    model_attacker: str = Field(default="gpt-4", description="Attacker model name")
    model_target: str = Field(default="gpt-35-turbo", description="Target model name")
    model_judge: str = Field(default="gpt-4", description="Judge model name")


class OpenAISettings(BaseSettings):
    """OpenAI provider configuration."""
    
    model_config = SettingsConfigDict(env_prefix="OPENAI_", case_sensitive=False)
    
    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model_attacker: str = Field(
        default="gpt-4-turbo-preview",
        description="Attacker model name"
    )
    model_target: str = Field(default="gpt-3.5-turbo", description="Target model name")
    model_judge: str = Field(
        default="gpt-4-turbo-preview",
        description="Judge model name"
    )
    timeout: int = Field(default=300, ge=1, description="Request timeout in seconds")


class PAIRAlgorithmSettings(BaseSettings):
    """PAIR algorithm configuration parameters."""
    
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)
    
    max_iterations: int = Field(default=20, ge=1, le=100, description="Maximum iterations")
    max_concurrent_attacks: int = Field(
        default=5, ge=1, le=20, description="Maximum concurrent attacks"
    )
    backoff_base_delay: float = Field(
        default=1.0, ge=0.1, description="Exponential backoff base delay"
    )
    backoff_max_delay: float = Field(
        default=60.0, ge=1.0, description="Exponential backoff maximum delay"
    )
    backoff_multiplier: float = Field(
        default=2.0, ge=1.1, description="Exponential backoff multiplier"
    )


class CircuitBreakerSettings(BaseSettings):
    """Circuit breaker configuration for LLM resilience."""
    
    model_config = SettingsConfigDict(env_prefix="CIRCUIT_BREAKER_", case_sensitive=False)
    
    failure_threshold: int = Field(
        default=10, ge=1, description="Number of failures before circuit opens"
    )
    success_threshold: int = Field(
        default=3, ge=1, description="Number of successes in HALF_OPEN before circuit closes"
    )
    timeout: float = Field(
        default=60.0, ge=1.0, description="Seconds before transitioning to HALF_OPEN"
    )
    half_open_max_calls: int = Field(
        default=5, ge=1, description="Maximum requests allowed in HALF_OPEN state"
    )
    jitter_enabled: bool = Field(
        default=True, description="Enable randomized backoff jitter"
    )
    max_jitter_ms: int = Field(
        default=1000, ge=0, description="Maximum jitter in milliseconds"
    )
    log_state_transitions: bool = Field(
        default=True, description="Log all circuit breaker state transitions"
    )


class JudgeSettings(BaseSettings):
    """Judge evaluation settings."""
    
    model_config = SettingsConfigDict(env_prefix="JUDGE_", case_sensitive=False)
    
    success_threshold: float = Field(
        default=7.0, ge=0.0, le=10.0, description="Success threshold score"
    )
    confidence_threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence threshold"
    )


class SecuritySettings(BaseSettings):
    """Security and API settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env that don't belong to SecuritySettings
    )
    
    api_key_enabled: bool = Field(
        default=True,
        description="Enable API key authentication",
        json_schema_extra={"env": "API_KEY_ENABLED"}
    )
    api_key: str = Field(
        default="your-secret-api-key-change-this",
        description="API key for authentication"
    )
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="CORS allowed origins (comma-separated)"
    )
    cors_allow_credentials: bool = Field(
        default=True, description="Allow CORS credentials"
    )
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(
        default=60, ge=1, description="Rate limit requests per minute"
    )


class TemplateUpdateSettings(BaseSettings):
    """Template update settings."""
    
    model_config = SettingsConfigDict(env_prefix="TEMPLATE_UPDATE_", case_sensitive=False)
    
    auto_update: bool = Field(
        default=False,
        description="Enable automatic daily template updates (runs at 2 AM UTC)"
    )
    update_interval_hours: int = Field(
        default=24,
        ge=1,
        description="Hours between automatic updates (default: 24 = daily)"
    )


class ExperimentSettings(BaseSettings):
    """Experiment and research settings."""
    
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)
    
    default_experiment_timeout: int = Field(
        default=3600, ge=1, description="Default experiment timeout in seconds"
    )
    default_batch_size: int = Field(
        default=10, ge=1, description="Default batch size"
    )
    enable_mutation_history: bool = Field(
        default=True, description="Enable mutation history tracking"
    )
    enable_detailed_telemetry: bool = Field(
        default=True, description="Enable detailed telemetry"
    )
    vulnerability_severity_levels: str = Field(
        default="low,medium,high,critical",
        description="Vulnerability severity levels (comma-separated)"
    )
    auto_export_results: bool = Field(
        default=True, description="Auto-export results"
    )
    export_format: str = Field(
        default="json,csv,pdf",
        description="Export formats (comma-separated)"
    )


class Settings(BaseSettings):
    """Root settings class combining all configuration groups."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    telemetry: TelemetrySettings = Field(default_factory=TelemetrySettings)
    llm_provider: LLMProviderSettings = Field(default_factory=LLMProviderSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    azure_openai: AzureOpenAISettings = Field(default_factory=AzureOpenAISettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    pair_algorithm: PAIRAlgorithmSettings = Field(default_factory=PAIRAlgorithmSettings)
    circuit_breaker: CircuitBreakerSettings = Field(default_factory=CircuitBreakerSettings)
    judge: JudgeSettings = Field(default_factory=JudgeSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    experiment: ExperimentSettings = Field(default_factory=ExperimentSettings)
    template_update: TemplateUpdateSettings = Field(default_factory=TemplateUpdateSettings)
    
    def get_llm_config(self, role: str) -> Dict[str, Any]:
        """
        Get LLM configuration for a specific role (attacker, target, judge).
        
        Args:
            role: One of "attacker", "target", or "judge"
            
        Returns:
            Dictionary with model_name, provider, and provider-specific config
            
        Raises:
            ValueError: If role is invalid or provider configuration is incomplete
        """
        if role not in ["attacker", "target", "judge"]:
            raise ValueError(f"Invalid role: {role}. Must be 'attacker', 'target', or 'judge'")
        
        provider = self.llm_provider.provider
        
        if provider == "ollama":
            model_name = getattr(self.ollama, f"model_{role}")
            return {
                "model_name": model_name,
                "provider": "ollama",
                "api_base": self.ollama.base_url,
                "timeout": self.ollama.timeout,
            }
        elif provider == "azure":
            if not self.azure_openai.api_key or not self.azure_openai.endpoint:
                raise ValueError("Azure OpenAI requires api_key and endpoint")
            model_name = getattr(self.azure_openai, f"model_{role}")
            return {
                "model_name": model_name,
                "provider": "azure",
                "api_key": self.azure_openai.api_key,
                "api_base": self.azure_openai.endpoint,
                "api_version": self.azure_openai.api_version,
            }
        elif provider == "openai":
            if not self.openai.api_key:
                raise ValueError("OpenAI requires api_key")
            model_name = getattr(self.openai, f"model_{role}")
            return {
                "model_name": model_name,
                "provider": "openai",
                "api_key": self.openai.api_key,
                "timeout": self.openai.timeout,
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def validate_provider_config(self) -> None:
        """
        Validate that the selected provider has all required credentials.
        
        Raises:
            ValueError: If provider configuration is incomplete
        """
        provider = self.llm_provider.provider
        
        if provider == "azure":
            if not self.azure_openai.api_key:
                raise ValueError("Azure OpenAI requires AZURE_OPENAI_API_KEY")
            if not self.azure_openai.endpoint:
                raise ValueError("Azure OpenAI requires AZURE_OPENAI_ENDPOINT")
        elif provider == "openai":
            if not self.openai.api_key:
                raise ValueError("OpenAI requires OPENAI_API_KEY")
        # Ollama doesn't require API key, so no validation needed


@lru_cache()
def get_settings() -> Settings:
    """
    Get singleton Settings instance.
    
    Returns:
        Cached Settings instance loaded from environment variables
        
    Example:
        >>> settings = get_settings()
        >>> config = settings.get_llm_config("attacker")
    """
    settings = Settings()
    settings.validate_provider_config()
    return settings
