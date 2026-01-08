"""
Tests for Task Queue Implementation (Phase 6)
"""
import pytest
from uuid import uuid4
from core.orchestrator import RedTeamOrchestrator
from core.models import ExperimentConfig, LLMProvider, AttackStrategyType
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def orchestrator():
    """Create orchestrator instance with mocked dependencies."""
    mutator = MagicMock()
    judge = MagicMock()
    target_llm_client = MagicMock()
    audit_logger = MagicMock()
    experiment_repo = MagicMock()
    iteration_repo = MagicMock()
    vulnerability_repo = MagicMock()
    
    return RedTeamOrchestrator(
        mutator=mutator,
        judge=judge,
        target_llm_client=target_llm_client,
        audit_logger=audit_logger,
        experiment_repo=experiment_repo,
        iteration_repo=iteration_repo,
        vulnerability_repo=vulnerability_repo
    )


@pytest.mark.asyncio
async def test_task_queue_initialization(orchestrator):
    """Test task queue is initialized for experiment."""
    experiment_id = uuid4()
    orchestrator._init_task_queue(experiment_id)
    
    assert experiment_id in orchestrator._task_queues
    assert orchestrator._task_queues[experiment_id] == []
    assert orchestrator._task_counter[experiment_id] == 0


@pytest.mark.asyncio
async def test_queue_task_creates_task(orchestrator):
    """Test queuing a task creates proper task structure."""
    experiment_id = uuid4()
    orchestrator._init_task_queue(experiment_id)
    
    with patch('api.websocket.send_task_update', new_callable=AsyncMock):
        task_id = await orchestrator._queue_task(
            experiment_id=experiment_id,
            task_name="Test Task",
            iteration=1,
            task_type="mutate"
        )
        
        assert task_id.startswith("task-")
        assert len(orchestrator._task_queues[experiment_id]) == 1
        
        task = orchestrator._task_queues[experiment_id][0]
        assert task["name"] == "Test Task"
        assert task["status"] == "queued"
        assert task["iteration"] == 1
        assert task["task_type"] == "mutate"


@pytest.mark.asyncio
async def test_task_lifecycle_transitions(orchestrator):
    """Test task transitions through queued → running → completed."""
    experiment_id = uuid4()
    orchestrator._init_task_queue(experiment_id)
    
    with patch('api.websocket.send_task_update', new_callable=AsyncMock):
        task_id = await orchestrator._queue_task(
            experiment_id=experiment_id,
            task_name="Lifecycle Test",
            iteration=1,
            task_type="target"
        )
        
        # Check queued
        task = orchestrator._task_queues[experiment_id][0]
        assert task["status"] == "queued"
        
        # Start task
        await orchestrator._start_task(experiment_id, task_id)
        assert task["status"] == "running"
        assert "started_at" in task
        
        # Complete task
        await orchestrator._complete_task(experiment_id, task_id, success=True)
        assert task["status"] == "completed"
        assert "completed_at" in task


@pytest.mark.asyncio
async def test_task_dependencies_tracked(orchestrator):
    """Test task dependencies are properly tracked."""
    experiment_id = uuid4()
    orchestrator._init_task_queue(experiment_id)
    
    with patch('api.websocket.send_task_update', new_callable=AsyncMock):
        task1_id = await orchestrator._queue_task(
            experiment_id=experiment_id,
            task_name="Task 1",
            iteration=1,
            task_type="mutate"
        )
        
        task2_id = await orchestrator._queue_task(
            experiment_id=experiment_id,
            task_name="Task 2",
            iteration=1,
            task_type="target",
            dependencies=[task1_id]
        )
        
        task2 = orchestrator._task_queues[experiment_id][1]
        assert task2["dependencies"] == [task1_id]


@pytest.mark.asyncio
async def test_task_queue_cleanup(orchestrator):
    """Test task queue is cleaned up after experiment."""
    experiment_id = uuid4()
    orchestrator._init_task_queue(experiment_id)
    
    with patch('api.websocket.send_task_update', new_callable=AsyncMock):
        await orchestrator._queue_task(
            experiment_id=experiment_id,
            task_name="Test",
            iteration=1,
            task_type="judge"
        )
        
        orchestrator._cleanup_task_queue(experiment_id)
        
        assert experiment_id not in orchestrator._task_queues
        assert experiment_id not in orchestrator._task_counter
