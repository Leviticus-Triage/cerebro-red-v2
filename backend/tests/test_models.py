"""
Tests for Pydantic models validation and serialization.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from core.models import (
    ExperimentConfig,
    AttackIteration,
    PromptMutation,
    JudgeScore,
    VulnerabilityFinding,
    AttackStrategyType,
    VulnerabilitySeverity,
    ExperimentStatus,
    LLMProvider,
)


class TestExperimentConfig:
    """Test ExperimentConfig model validation."""
    
    def test_valid_experiment_config(self):
        """Test creating a valid experiment configuration."""
        config = ExperimentConfig(
            name="Test Experiment",
            description="A test experiment",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen3:8b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen3:8b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen3:14b",
            initial_prompts=["Test prompt"],
            strategies=[AttackStrategyType.OBFUSCATION_BASE64],
        )
        assert config.name == "Test Experiment"
        assert config.max_iterations == 20  # Default value
        assert len(config.strategies) == 1
    
    def test_experiment_config_empty_prompts_validation(self):
        """Test that empty prompts are rejected."""
        with pytest.raises(ValueError):
            ExperimentConfig(
                name="Test",
                target_model_provider=LLMProvider.OLLAMA,
                target_model_name="qwen3:8b",
                attacker_model_provider=LLMProvider.OLLAMA,
                attacker_model_name="qwen3:8b",
                judge_model_provider=LLMProvider.OLLAMA,
                judge_model_name="qwen3:14b",
                initial_prompts=[""],  # Empty prompt
                strategies=[AttackStrategyType.OBFUSCATION_BASE64],
            )
    
    def test_experiment_config_max_iterations_constraint(self):
        """Test max_iterations constraint validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            ExperimentConfig(
                name="Test",
                target_model_provider=LLMProvider.OLLAMA,
                target_model_name="qwen3:8b",
                attacker_model_provider=LLMProvider.OLLAMA,
                attacker_model_name="qwen3:8b",
                judge_model_provider=LLMProvider.OLLAMA,
                judge_model_name="qwen3:14b",
                initial_prompts=["Test"],
                strategies=[AttackStrategyType.OBFUSCATION_BASE64],
                max_iterations=200,  # Exceeds max of 100
            )


class TestAttackIteration:
    """Test AttackIteration model validation."""
    
    def test_valid_attack_iteration(self):
        """Test creating a valid attack iteration."""
        iteration = AttackIteration(
            experiment_id=uuid4(),
            iteration_number=1,
            strategy_used=AttackStrategyType.OBFUSCATION_BASE64,
            original_prompt="Original",
            mutated_prompt="Mutated",
            target_response="Response",
            judge_score=7.5,
            judge_reasoning="Test reasoning",
            success=True,
            latency_ms=150,
        )
        assert iteration.iteration_number == 1
        assert iteration.success is True
        assert iteration.judge_score == 7.5


class TestEnums:
    """Test enum values."""
    
    def test_attack_strategy_types(self):
        """Test AttackStrategyType enum values."""
        assert AttackStrategyType.OBFUSCATION_BASE64.value == "obfuscation_base64"
        assert AttackStrategyType.CONTEXT_FLOODING.value == "context_flooding"
    
    def test_vulnerability_severity(self):
        """Test VulnerabilitySeverity enum values."""
        assert VulnerabilitySeverity.LOW.value == "low"
        assert VulnerabilitySeverity.CRITICAL.value == "critical"
    
    def test_experiment_status(self):
        """Test ExperimentStatus enum values."""
        assert ExperimentStatus.PENDING.value == "pending"
        assert ExperimentStatus.COMPLETED.value == "completed"
    
    def test_llm_provider(self):
        """Test LLMProvider enum values."""
        assert LLMProvider.OLLAMA.value == "ollama"
        assert LLMProvider.AZURE.value == "azure"
        assert LLMProvider.OPENAI.value == "openai"

