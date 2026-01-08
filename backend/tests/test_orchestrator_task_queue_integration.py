"""
Integration tests for Task Queue WebSocket events
"""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_task_events_emitted_via_websocket():
    """Test that task lifecycle events are emitted via WebSocket."""
    from core.orchestrator import RedTeamOrchestrator
    from unittest.mock import MagicMock
    
    # Create orchestrator with mocked dependencies
    orchestrator = RedTeamOrchestrator(
        mutator=MagicMock(),
        judge=MagicMock(),
        target_llm_client=MagicMock(),
        audit_logger=MagicMock(),
        experiment_repo=MagicMock(),
        iteration_repo=MagicMock(),
        vulnerability_repo=MagicMock()
    )
    
    experiment_id = uuid4()
    orchestrator._init_task_queue(experiment_id)
    
    with patch('api.websocket.send_task_update', new_callable=AsyncMock) as mock_send:
        # Queue task
        task_id = await orchestrator._queue_task(
            experiment_id=experiment_id,
            task_name="WS Test Task",
            iteration=1,
            task_type="mutate"
        )
        
        # Verify queued event
        assert mock_send.call_count == 1
        call_args = mock_send.call_args[1]
        assert call_args["status"] == "queued"
        assert call_args["task_name"] == "WS Test Task"
        
        # Start task
        await orchestrator._start_task(experiment_id, task_id)
        assert mock_send.call_count == 2
        call_args = mock_send.call_args[1]
        assert call_args["status"] == "running"
        
        # Complete task
        await orchestrator._complete_task(experiment_id, task_id, success=True)
        assert mock_send.call_count == 3
        call_args = mock_send.call_args[1]
        assert call_args["status"] == "completed"


@pytest.mark.asyncio
async def test_task_dependencies_sent_in_websocket():
    """Test that task dependencies are included in WebSocket events."""
    from core.orchestrator import RedTeamOrchestrator
    from unittest.mock import MagicMock
    
    orchestrator = RedTeamOrchestrator(
        mutator=MagicMock(),
        judge=MagicMock(),
        target_llm_client=MagicMock(),
        audit_logger=MagicMock(),
        experiment_repo=MagicMock(),
        iteration_repo=MagicMock(),
        vulnerability_repo=MagicMock()
    )
    
    experiment_id = uuid4()
    orchestrator._init_task_queue(experiment_id)
    
    with patch('api.websocket.send_task_update', new_callable=AsyncMock) as mock_send:
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
        
        # Verify dependencies were sent in WebSocket event
        calls = mock_send.call_args_list
        # Second call should be for task2 with dependencies
        task2_call = calls[1]
        assert task2_call[1]["dependencies"] == [task1_id]
