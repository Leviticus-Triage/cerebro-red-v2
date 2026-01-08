"""
Tests for database operations and CRUD functionality.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import (
    init_db,
    get_session,
    close_db,
    ExperimentRepository,
    AttackIterationRepository,
    VulnerabilityRepository,
    ExperimentDB,
)
from core.models import (
    ExperimentConfig,
    AttackIteration,
    VulnerabilityFinding,
    LLMProvider,
    AttackStrategyType,
    VulnerabilitySeverity,
)


@pytest.mark.asyncio
async def test_database_initialization():
    """Test database initialization."""
    await init_db()
    # If no exception is raised, initialization succeeded


@pytest.mark.asyncio
async def test_experiment_repository_create():
    """Test creating an experiment via repository."""
    async for session in get_session():
        repo = ExperimentRepository(session)
        experiment_config = ExperimentConfig(
            name="Test Experiment",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen3:8b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen3:8b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen3:14b",
            initial_prompts=["Test prompt"],
            strategies=[AttackStrategyType.OBFUSCATION_BASE64],
        )
        db_experiment = await repo.create(experiment_config)
        assert db_experiment.experiment_id == experiment_config.experiment_id
        assert db_experiment.name == "Test Experiment"
        break  # Exit after first iteration


@pytest.mark.asyncio
async def test_experiment_repository_get_by_id():
    """Test retrieving an experiment by ID."""
    async for session in get_session():
        repo = ExperimentRepository(session)
        experiment_config = ExperimentConfig(
            name="Test Get",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen3:8b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen3:8b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen3:14b",
            initial_prompts=["Test"],
            strategies=[AttackStrategyType.OBFUSCATION_BASE64],
        )
        created = await repo.create(experiment_config)
        retrieved = await repo.get_by_id(created.experiment_id)
        assert retrieved is not None
        assert retrieved.experiment_id == created.experiment_id
        break


@pytest.mark.asyncio
async def test_experiment_repository_list_all():
    """Test listing all experiments."""
    async for session in get_session():
        repo = ExperimentRepository(session)
        experiments = await repo.list_all(limit=10)
        assert isinstance(experiments, list)
        break


@pytest.mark.asyncio
async def test_experiment_repository_update_status():
    """Test updating experiment status."""
    async for session in get_session():
        repo = ExperimentRepository(session)
        experiment_config = ExperimentConfig(
            name="Test Update",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen3:8b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen3:8b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen3:14b",
            initial_prompts=["Test"],
            strategies=[AttackStrategyType.OBFUSCATION_BASE64],
        )
        created = await repo.create(experiment_config)
        updated = await repo.update_status(created.experiment_id, "running")
        assert updated is not None
        assert updated.status == "running"
        break


@pytest.mark.asyncio
async def test_attack_iteration_repository_create():
    """Test creating an attack iteration."""
    async for session in get_session():
        exp_repo = ExperimentRepository(session)
        experiment_config = ExperimentConfig(
            name="Test Iteration",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen3:8b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen3:8b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen3:14b",
            initial_prompts=["Test"],
            strategies=[AttackStrategyType.OBFUSCATION_BASE64],
        )
        experiment = await exp_repo.create(experiment_config)
        
        iter_repo = AttackIterationRepository(session)
        iteration = AttackIteration(
            experiment_id=experiment.experiment_id,
            iteration_number=1,
            strategy_used=AttackStrategyType.OBFUSCATION_BASE64,
            original_prompt="Original",
            mutated_prompt="Mutated",
            target_response="Response",
            judge_score=7.5,
            judge_reasoning="Test",
            success=True,
            latency_ms=150,
        )
        db_iteration = await iter_repo.create(iteration)
        assert db_iteration.iteration_id == iteration.iteration_id
        break

