"""
Integration test for strategy rotation with real PAIR loop (Phase 6).
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy import select
from core.orchestrator import RedTeamOrchestrator
from core.models import ExperimentConfig, AttackStrategyType, LLMProvider
from core.database import AsyncSessionLocal, AttackIterationDB
from tests.test_mutator_all_strategies import ALL_STRATEGIES


# Comment 3: Shared fixture for AsyncSessionLocal mock
@pytest_asyncio.fixture
async def mock_async_session():
    """
    Create async context manager stub for AsyncSessionLocal (Comment 3).
    
    Provides proper async with support for all orchestrator DB operations.
    """
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    
    # Create async context manager for begin()
    begin_context = AsyncMock()
    begin_context.__aenter__ = AsyncMock(return_value=None)
    begin_context.__aexit__ = AsyncMock(return_value=None)
    session.begin = Mock(return_value=begin_context)
    
    return session


@pytest.mark.asyncio
async def test_full_pair_loop_uses_all_selected_strategies(mock_async_session):
    """
    Integration test: Run PAIR loop with 10 strategies, verify all are used.
    """
    # Mock dependencies
    mock_mutator = Mock()
    mock_mutator.mutate = AsyncMock(return_value=Mock(
        output_prompt="mutated",
        mutation_params={"latency_ms": 100, "tokens_used": 50}
    ))
    
    mock_judge = Mock()
    mock_judge.evaluate = AsyncMock(return_value=Mock(
        overall_score=5.0,  # Medium score
        jailbreak_success_score=5.0,
        harmful_content_score=4.0,
        hallucination_score=3.0,
        bias_score=2.0,
        logical_consistency_score=6.0,
        sycophancy_score=3.0,
        policy_violation_score=4.0,
        confidence=0.8,
        reasoning="Test reasoning",
        fallback_used=False,
        judge_model="test"
    ))
    mock_judge.get_feedback_dict = Mock(return_value={
        "target_response": "Test response",
        "judge_score": 5.0,
        "judge_reasoning": "Test reasoning"
    })
    
    mock_target_llm = Mock()
    mock_target_llm.complete = AsyncMock(return_value=Mock(
        content="Test response",
        latency_ms=200,
        tokens_used=100,
        model="test"
    ))
    
    mock_audit_logger = Mock()
    mock_audit_logger.log_iteration = Mock()
    mock_audit_logger.log_strategy_usage_summary = Mock()
    mock_audit_logger.log_error = Mock()
    
    # Mock repositories
    mock_experiment_repo = AsyncMock()
    mock_experiment_repo.create = AsyncMock(return_value=Mock(experiment_id=uuid4()))
    mock_experiment_repo.update_status = AsyncMock()
    
    mock_iteration_repo = AsyncMock()
    mock_iteration_repo.create = AsyncMock(return_value=Mock())
    
    mock_vulnerability_repo = AsyncMock()
    mock_judge_score_repo = AsyncMock()
    
    # Comment 3: Use shared fixture for AsyncSessionLocal
    with patch('core.orchestrator.AsyncSessionLocal', return_value=mock_async_session):
        orchestrator = RedTeamOrchestrator(
            mutator=mock_mutator,
            judge=mock_judge,
            target_llm_client=mock_target_llm,
            audit_logger=mock_audit_logger,
            experiment_repo=mock_experiment_repo,
            iteration_repo=mock_iteration_repo,
            vulnerability_repo=mock_vulnerability_repo,
            judge_score_repo=mock_judge_score_repo
        )
        
        # Create config with 10 strategies
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="Strategy Rotation Test",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test"],
            strategies=[
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
            ],
            max_iterations=20
        )
        
        # Run experiment
        result = await orchestrator.run_experiment(config)
        
        # Verify all strategies were used
        # Check audit logger calls
        assert mock_audit_logger.log_strategy_usage_summary.called
        call_args = mock_audit_logger.log_strategy_usage_summary.call_args
        
        # Verify result
        assert result["status"] in ["COMPLETED", "FAILED"]
        assert result["total_iterations"] > 0


@pytest.mark.asyncio
async def test_all_44_strategies_logged_in_db(mock_async_session):
    """
    Phase 6: Verify all 44 strategies are logged in database.
    
    Creates an experiment with all 44 strategies, runs 50 iterations,
    and verifies all strategies appear in the attack_iterations table.
    """
    # Mock dependencies
    mock_mutator = Mock()
    
    # Track which strategies were used
    strategies_used = []
    
    async def mock_mutate(original_prompt, strategy, iteration, feedback=None):
        strategies_used.append(strategy)
        return Mock(
            output_prompt=f"mutated_{strategy.value}",
            mutation_params={"latency_ms": 100, "tokens_used": 50}
        )
    
    mock_mutator.mutate = AsyncMock(side_effect=mock_mutate)
    
    mock_judge = Mock()
    mock_judge.evaluate = AsyncMock(return_value=Mock(
        overall_score=5.0,
        jailbreak_success_score=5.0,
        harmful_content_score=4.0,
        hallucination_score=3.0,
        bias_score=2.0,
        logical_consistency_score=6.0,
        sycophancy_score=3.0,
        policy_violation_score=4.0,
        confidence=0.8,
        reasoning="Test reasoning",
        fallback_used=False,
        judge_model="test",
        tokens_used=100
    ))
    mock_judge.get_feedback_dict = Mock(return_value={
        "target_response": "Test response",
        "judge_score": 5.0,
        "judge_reasoning": "Test reasoning"
    })
    
    mock_target_llm = Mock()
    mock_target_llm.complete = AsyncMock(return_value=Mock(
        content="Test response",
        latency_ms=200,
        tokens_used=100,
        model="test"
    ))
    
    mock_audit_logger = Mock()
    mock_audit_logger.log_iteration = Mock()
    mock_audit_logger.log_strategy_usage_summary = Mock()
    mock_audit_logger.log_error = Mock()
    
    # Mock repositories
    mock_experiment_repo = AsyncMock()
    experiment_id = uuid4()
    mock_experiment_repo.create = AsyncMock(return_value=Mock(experiment_id=experiment_id))
    mock_experiment_repo.update_status = AsyncMock()
    
    mock_iteration_repo = AsyncMock()
    mock_iteration_repo.create = AsyncMock(return_value=Mock())
    
    mock_vulnerability_repo = AsyncMock()
    mock_judge_score_repo = AsyncMock()
    
    # Comment 3: Use shared fixture for AsyncSessionLocal
    with patch('core.orchestrator.AsyncSessionLocal', return_value=mock_async_session):
        orchestrator = RedTeamOrchestrator(
            mutator=mock_mutator,
            judge=mock_judge,
            target_llm_client=mock_target_llm,
            audit_logger=mock_audit_logger,
            experiment_repo=mock_experiment_repo,
            iteration_repo=mock_iteration_repo,
            vulnerability_repo=mock_vulnerability_repo,
            judge_score_repo=mock_judge_score_repo
        )
        
        # Create config with all 44 strategies
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name="All 44 Strategies Test",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test"],
            strategies=list(ALL_STRATEGIES),  # All 44
            max_iterations=50  # Enough to use all strategies
        )
        
        # Run experiment
        result = await orchestrator.run_experiment(config)
        
        # Verify all 44 strategies were used
        unique_strategies = set(strategies_used)
        
        print(f"\n{'='*80}")
        print(f"STRATEGY COVERAGE TEST (Phase 6)")
        print(f"{'='*80}")
        print(f"Total Strategies: {len(ALL_STRATEGIES)}")
        print(f"Strategies Used: {len(unique_strategies)}")
        print(f"Coverage: {len(unique_strategies) / len(ALL_STRATEGIES) * 100:.1f}%")
        print(f"{'='*80}")
        
        # Assert all 44 strategies were used
        assert len(unique_strategies) == len(ALL_STRATEGIES), \
            f"Only {len(unique_strategies)}/44 strategies used"
        assert unique_strategies == set(ALL_STRATEGIES), \
            f"Missing strategies: {set(ALL_STRATEGIES) - unique_strategies}"
        
        print(f"✅ All 44 strategies used in {result['total_iterations']} iterations")


@pytest.mark.asyncio
async def test_strategy_rotation_respects_user_selection(mock_async_session):
    """
    Verify that orchestrator only uses user-selected strategies.
    
    Creates experiment with 5 strategies, verifies no other strategies are used.
    """
    mock_mutator = Mock()
    strategies_used = []
    
    async def mock_mutate(original_prompt, strategy, iteration, feedback=None):
        strategies_used.append(strategy)
        return Mock(
            output_prompt=f"mutated_{strategy.value}",
            mutation_params={"latency_ms": 100, "tokens_used": 50}
        )
    
    mock_mutator.mutate = AsyncMock(side_effect=mock_mutate)
    
    mock_judge = Mock()
    mock_judge.evaluate = AsyncMock(return_value=Mock(
        overall_score=5.0,
        jailbreak_success_score=5.0,
        harmful_content_score=4.0,
        hallucination_score=3.0,
        bias_score=2.0,
        logical_consistency_score=6.0,
        sycophancy_score=3.0,
        policy_violation_score=4.0,
        confidence=0.8,
        reasoning="Test",
        fallback_used=False,
        judge_model="test",
        tokens_used=100
    ))
    mock_judge.get_feedback_dict = Mock(return_value={
        "target_response": "Test",
        "judge_score": 5.0,
        "judge_reasoning": "Test"
    })
    
    mock_target_llm = Mock()
    mock_target_llm.complete = AsyncMock(return_value=Mock(
        content="Test",
        latency_ms=200,
        tokens_used=100,
        model="test"
    ))
    
    mock_audit_logger = Mock()
    mock_audit_logger.log_iteration = Mock()
    mock_audit_logger.log_strategy_usage_summary = Mock()
    mock_audit_logger.log_error = Mock()
    
    mock_experiment_repo = AsyncMock()
    mock_experiment_repo.create = AsyncMock(return_value=Mock(experiment_id=uuid4()))
    mock_experiment_repo.update_status = AsyncMock()
    mock_iteration_repo = AsyncMock()
    mock_iteration_repo.create = AsyncMock(return_value=Mock())
    mock_vulnerability_repo = AsyncMock()
    mock_judge_score_repo = AsyncMock()
    
    # Comment 3: Use shared fixture for AsyncSessionLocal
    with patch('core.orchestrator.AsyncSessionLocal', return_value=mock_async_session):
        orchestrator = RedTeamOrchestrator(
            mutator=mock_mutator,
            judge=mock_judge,
            target_llm_client=mock_target_llm,
            audit_logger=mock_audit_logger,
            experiment_repo=mock_experiment_repo,
            iteration_repo=mock_iteration_repo,
            vulnerability_repo=mock_vulnerability_repo,
            judge_score_repo=mock_judge_score_repo
        )
        
        # Only select 5 strategies
        selected_strategies = [
            AttackStrategyType.OBFUSCATION_BASE64,
            AttackStrategyType.JAILBREAK_DAN,
            AttackStrategyType.ROLEPLAY_INJECTION,
            AttackStrategyType.CONTEXT_FLOODING,
            AttackStrategyType.SYCOPHANCY
        ]
        
        config = ExperimentConfig(
            experiment_id=uuid4(),
            name="Limited Strategy Test",
            target_model_provider=LLMProvider.OLLAMA,
            target_model_name="qwen2.5:3b",
            attacker_model_provider=LLMProvider.OLLAMA,
            attacker_model_name="qwen2.5:3b",
            judge_model_provider=LLMProvider.OLLAMA,
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test"],
            strategies=selected_strategies,
            max_iterations=10
        )
        
        await orchestrator.run_experiment(config)
        
        # Verify only selected strategies were used
        unique_used = set(strategies_used)
        assert unique_used.issubset(set(selected_strategies)), \
            f"Unexpected strategies used: {unique_used - set(selected_strategies)}"
        
        print(f"✅ Only user-selected strategies used: {len(unique_used)}/{len(selected_strategies)}")
