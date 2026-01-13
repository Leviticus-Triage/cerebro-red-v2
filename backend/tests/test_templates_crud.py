"""
Tests for experiment template CRUD operations (Phase 6).
"""

import pytest
from uuid import uuid4
from core.models import ExperimentTemplateCreate, ExperimentConfig, LLMProvider, AttackStrategyType, ExperimentTemplateUpdate
from core.database import ExperimentTemplateRepository, AsyncSessionLocal
from tests.test_mutator_all_strategies import ALL_STRATEGIES


@pytest.mark.asyncio
async def test_create_template():
    """Test creating a template."""
    async with AsyncSessionLocal() as session:
        repo = ExperimentTemplateRepository(session)
        
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="Test Experiment",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test prompt"],
            strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
        )
        
        template = ExperimentTemplateCreate(
            name="Test Template",
            description="Test description",
            config=config,
            tags=["test", "jailbreak"],
            is_public=False
        )
        
        db_template = await repo.create(template)
        await session.commit()
        
        assert db_template.name == "Test Template"
        assert db_template.tags == ["test", "jailbreak"]
        assert "qwen2.5:3b" in db_template.config_json


@pytest.mark.asyncio
async def test_list_templates():
    """Test listing templates."""
    async with AsyncSessionLocal() as session:
        repo = ExperimentTemplateRepository(session)
        templates = await repo.list_all(limit=10)
        assert isinstance(templates, list)


@pytest.mark.asyncio
async def test_update_template():
    """Test updating a template."""
    async with AsyncSessionLocal() as session:
        repo = ExperimentTemplateRepository(session)
        
        # Create template first
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="Original Experiment",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test prompt"],
            strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
        )
        template = ExperimentTemplateCreate(name="Original", config=config)
        db_template = await repo.create(template)
        await session.commit()
        
        # Update
        from core.models import ExperimentTemplateUpdate
        update = ExperimentTemplateUpdate(name="Updated Name")
        updated = await repo.update(db_template.template_id, update)
        await session.commit()
        
        assert updated is not None
        assert updated.name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_template():
    """Test deleting a template."""
    async with AsyncSessionLocal() as session:
        repo = ExperimentTemplateRepository(session)
        
        # Create template first
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="To Delete Experiment",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test prompt"],
            strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
        )
        template = ExperimentTemplateCreate(name="To Delete", config=config)
        db_template = await repo.create(template)
        await session.commit()
        
        # Delete
        success = await repo.delete(db_template.template_id)
        await session.commit()
        
        assert success is True
        
        # Verify deleted
        deleted = await repo.get_by_id(db_template.template_id)
        assert deleted is None


@pytest.mark.asyncio
async def test_increment_usage():
    """Test incrementing usage count."""
    async with AsyncSessionLocal() as session:
        repo = ExperimentTemplateRepository(session)
        
        # Create template first
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="Usage Test Experiment",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test prompt"],
            strategies=[AttackStrategyType.ROLEPLAY_INJECTION],
        )
        template = ExperimentTemplateCreate(name="Usage Test", config=config)
        db_template = await repo.create(template)
        await session.commit()
        
        # Increment usage
        initial_count = db_template.usage_count
        await repo.increment_usage(db_template.template_id)
        await session.commit()
        
        # Verify increment
        updated = await repo.get_by_id(db_template.template_id)
        assert updated is not None
        assert updated.usage_count == initial_count + 1


@pytest.mark.asyncio
async def test_template_with_all_44_strategies():
    """
    Phase 6: Test template with all 44 strategies.
    
    Verifies that templates can save and load all 44 attack strategies correctly.
    """
    async with AsyncSessionLocal() as session:
        repo = ExperimentTemplateRepository(session)
        
        # Create config with all 44 strategies
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="All Strategies Template",
            description="Template with all 44 attack strategies",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test"],
            strategies=list(ALL_STRATEGIES),  # All 44
            max_iterations=50,
            max_concurrent_attacks=5,
            success_threshold=7.0,
            timeout_seconds=3600
        )
        
        template = ExperimentTemplateCreate(
            name="All 44 Strategies",
            description="Template with all attack strategies for comprehensive testing",
            config=config,
            tags=["comprehensive", "all-strategies", "phase-6"],
            is_public=False
        )
        
        # Save template
        db_template = await repo.create(template)
        await session.commit()
        
        assert db_template.template_id is not None
        assert db_template.name == "All 44 Strategies"
        
        # Load template
        loaded = await repo.get_by_id(db_template.template_id)
        assert loaded is not None
        
        # Parse config
        import json
        loaded_config_dict = json.loads(loaded.config_json)
        loaded_config = ExperimentConfig(**loaded_config_dict)
        
        # Assert all 44 strategies preserved
        assert len(loaded_config.strategies) == 44, \
            f"Expected 44 strategies, got {len(loaded_config.strategies)}"
        assert set(loaded_config.strategies) == set(ALL_STRATEGIES), \
            f"Strategy mismatch: {set(ALL_STRATEGIES) - set(loaded_config.strategies)}"
        
        # Verify other config fields
        assert loaded_config.name == "All Strategies Template"
        assert loaded_config.max_iterations == 50
        assert loaded_config.target_model_name == "qwen2.5:3b"
        
        print(f" Template with all 44 strategies saved and loaded successfully")


@pytest.mark.asyncio
async def test_template_multi_strategy_selection():
    """
    Phase 6: Test template with multi-strategy selection (10+ strategies).
    
    Validates that templates work correctly with a subset of strategies.
    """
    async with AsyncSessionLocal() as session:
        repo = ExperimentTemplateRepository(session)
        
        # Select 10 diverse strategies
        selected_strategies = [
            AttackStrategyType.OBFUSCATION_BASE64,
            AttackStrategyType.JAILBREAK_DAN,
            AttackStrategyType.ROLEPLAY_INJECTION,
            AttackStrategyType.CONTEXT_FLOODING,
            AttackStrategyType.SYCOPHANCY,
            AttackStrategyType.RAG_POISONING,
            AttackStrategyType.BIAS_PROBE,
            AttackStrategyType.DIRECT_INJECTION,
            AttackStrategyType.TRANSLATION_ATTACK,
            AttackStrategyType.ADVERSARIAL_SUFFIX
        ]
        
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="Multi-Strategy Test",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test"],
            strategies=selected_strategies
        )
        
        template = ExperimentTemplateCreate(
            name="Multi-Strategy Template",
            description="Template with 10 diverse strategies",
            config=config,
            tags=["multi-strategy", "diverse"]
        )
        
        # Save and load
        db_template = await repo.create(template)
        await session.commit()
        
        loaded = await repo.get_by_id(db_template.template_id)
        
        import json
        loaded_config = ExperimentConfig(**json.loads(loaded.config_json))
        
        # Verify all 10 strategies preserved
        assert len(loaded_config.strategies) == 10
        assert set(loaded_config.strategies) == set(selected_strategies)
        
        print(f" Template with 10 strategies saved and loaded successfully")
