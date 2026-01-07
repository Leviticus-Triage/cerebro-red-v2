"""
backend/api/websocket.py
=========================

WebSocket endpoints for real-time progress streaming in CEREBRO-RED v2 API.
"""

from typing import Dict, Set, Optional, Any, List
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

router = APIRouter()


# ============================================================================
# Connection Manager
# ============================================================================

class ConnectionManager:
    """
    Manages WebSocket connections for real-time progress updates.
    
    Tracks active connections per experiment and provides broadcast functionality
    with verbosity-based filtering.
    """
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        # Track verbosity level per connection
        self.connection_verbosity: Dict[WebSocket, int] = {}
    
    async def connect(self, experiment_id: UUID, websocket: WebSocket, verbosity: Optional[int] = None) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            experiment_id: Experiment UUID
            websocket: WebSocket connection
            verbosity: Initial verbosity level (0-3, default: from settings)
        """
        # Use configured default if not provided
        if verbosity is None:
            from utils.config import get_settings
            settings = get_settings()
            verbosity = max(0, min(3, settings.app.verbosity))  # Clamp to 0-3
        await websocket.accept()
        
        if experiment_id not in self.active_connections:
            self.active_connections[experiment_id] = set()
        
        self.active_connections[experiment_id].add(websocket)
        # Store verbosity level
        self.connection_verbosity[websocket] = verbosity
    
    def disconnect(self, experiment_id: UUID, websocket: WebSocket) -> None:
        """
        Remove WebSocket connection.
        
        Args:
            experiment_id: Experiment UUID
            websocket: WebSocket connection
        """
        if experiment_id in self.active_connections:
            self.active_connections[experiment_id].discard(websocket)
            # Clean up verbosity tracking
            self.connection_verbosity.pop(websocket, None)
            
            # Clean up empty sets
            if not self.active_connections[experiment_id]:
                del self.active_connections[experiment_id]
    
    def set_verbosity(self, websocket: WebSocket, verbosity: int) -> None:
        """Update verbosity level for a connection."""
        # Clamp verbosity to valid range (0-3) instead of raising
        clamped_verbosity = max(0, min(3, verbosity))
        self.connection_verbosity[websocket] = clamped_verbosity
    
    def get_verbosity(self, websocket: WebSocket) -> int:
        """Get verbosity level for a connection (default: from settings)."""
        from utils.config import get_settings
        settings = get_settings()
        default_verbosity = max(0, min(3, settings.app.verbosity))  # Clamp to 0-3
        return self.connection_verbosity.get(websocket, default_verbosity)
    
    async def broadcast(self, experiment_id: UUID, message: dict, min_verbosity: int = 0) -> None:
        """
        Broadcast message to connections with sufficient verbosity level.
        
        Args:
            experiment_id: Experiment UUID
            message: Message dict to send (will be JSON-serialized)
            min_verbosity: Minimum verbosity level required to receive this message
                          0 = errors only
                          1 = + warnings, events
                          2 = + LLM details
                          3 = + code flow
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # DEBUG: Log broadcast attempt
        logger.info(f"[WS-BROADCAST] Attempting broadcast for exp {experiment_id}, type={message.get('type')}, min_verbosity={min_verbosity}")
        
        if experiment_id not in self.active_connections:
            logger.warning(f"[WS-BROADCAST] No active connections for exp {experiment_id}")
            return
        
        connection_count = len(self.active_connections[experiment_id])
        logger.info(f"[WS-BROADCAST] Found {connection_count} active connections")
        
        # Send to all connections (remove dead connections)
        dead_connections = set()
        sent_count = 0
        filtered_count = 0
        
        for connection in self.active_connections[experiment_id]:
            try:
                # Check verbosity level before sending
                conn_verbosity = self.get_verbosity(connection)
                
                # DEBUG: Log verbosity check
                logger.debug(f"[WS-BROADCAST] Connection verbosity={conn_verbosity}, required={min_verbosity}")
                
                if conn_verbosity >= min_verbosity:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_json(message)
                        sent_count += 1
                        logger.debug(f"[WS-BROADCAST] ✅ Sent message type={message.get('type')} to connection")
                    else:
                        dead_connections.add(connection)
                        logger.warning(f"[WS-BROADCAST] Connection not in CONNECTED state")
                else:
                    filtered_count += 1
                    logger.debug(f"[WS-BROADCAST] ❌ Filtered message (verbosity {conn_verbosity} < {min_verbosity})")
            except Exception as e:
                logger.error(f"[WS-BROADCAST] Error sending message: {e}")
                dead_connections.add(connection)
        
        logger.info(f"[WS-BROADCAST] Summary: sent={sent_count}, filtered={filtered_count}, dead={len(dead_connections)}")
        
        # Remove dead connections
        for connection in dead_connections:
            self.disconnect(experiment_id, connection)


# Global connection manager instance
manager = ConnectionManager()


# ============================================================================
# Endpoints
# ============================================================================

@router.websocket("/scan/{experiment_id}")
async def websocket_scan_progress(
    websocket: WebSocket,
    experiment_id: UUID
):
    """
    WebSocket endpoint for real-time scan progress updates.
    
    Connects to experiment and receives live updates:
    - Progress updates (iteration, progress_percent)
    - Iteration complete events
    - Vulnerability found events
    - Experiment complete events
    - Error events
    
    Message Types:
    - progress: Current iteration and progress
    - iteration_complete: Iteration finished
    - vulnerability_found: Vulnerability discovered
    - experiment_complete: Experiment finished
    - error: Error occurred
    
    Authentication:
    - No API key required for WebSocket connections (simplified for development/testing)
    """
    # WebSocket connections are allowed without API key validation for easier development/testing
    # API key validation removed per user request to simplify access
    
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[WS-ENDPOINT] ========== NEW CONNECTION ==========")
    logger.info(f"[WS-ENDPOINT] Experiment ID: {experiment_id}")
    logger.info(f"[WS-ENDPOINT] Query params: {websocket.query_params}")
    
    # Get configured default verbosity from settings
    from utils.config import get_settings
    settings = get_settings()
    default_verbosity = max(0, min(3, settings.app.verbosity))  # Clamp to 0-3
    
    # Get initial verbosity from query param, with error handling
    initial_verbosity = default_verbosity
    verbosity_error_message = None
    verbosity_param = websocket.query_params.get("verbosity")
    if verbosity_param:
        try:
            parsed_verbosity = int(verbosity_param)
            # Clamp to valid range
            if 0 <= parsed_verbosity <= 3:
                initial_verbosity = parsed_verbosity
            else:
                # Out of range - use default and send error after connection
                initial_verbosity = default_verbosity
                verbosity_error_message = f"Invalid verbosity value {parsed_verbosity}. Must be 0-3. Using default: {default_verbosity}."
        except ValueError:
            # Invalid format - use default and send error after connection
            initial_verbosity = default_verbosity
            verbosity_error_message = f"Invalid verbosity format '{verbosity_param}'. Must be integer 0-3. Using default: {default_verbosity}."
    
    logger.info(f"[WS-ENDPOINT] Initial verbosity: {initial_verbosity}")
    
    await manager.connect(experiment_id, websocket, verbosity=initial_verbosity)
    logger.info(f"[WS-ENDPOINT] ✅ Connection registered with verbosity={initial_verbosity}")
    
    # Send error message if verbosity was invalid (after connection is established)
    if verbosity_error_message:
        try:
            await websocket.send_json({
                "type": "error",
                "error_message": verbosity_error_message
            })
        except Exception:
            pass  # Ignore errors sending error message
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "experiment_id": str(experiment_id),
            "message": "Connected to experiment progress stream",
            "verbosity": initial_verbosity  # Inform client of current verbosity
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Receive any message (ping/pong for keepalive, verbosity control)
            try:
                data = await websocket.receive_text()
                logger.debug(f"[WS-ENDPOINT] Received message: {data}")
                
                # Handle verbosity control messages
                if data.startswith("set_verbosity:"):
                    try:
                        new_verbosity = int(data.split(":")[1])
                        logger.info(f"[WS-ENDPOINT] Verbosity change request: {new_verbosity}")
                        
                        manager.set_verbosity(websocket, new_verbosity)
                        logger.info(f"[WS-ENDPOINT] ✅ Verbosity updated to {new_verbosity}")
                        
                        await websocket.send_json({
                            "type": "verbosity_updated",
                            "verbosity": new_verbosity
                        })
                    except (ValueError, IndexError) as e:
                        logger.error(f"[WS-ENDPOINT] Invalid verbosity format: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "error_message": "Invalid verbosity format. Use: set_verbosity:0-3"
                        })
                elif data == "ping":
                    await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                logger.info(f"[WS-ENDPOINT] Client disconnected for exp {experiment_id}")
                break
            
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(experiment_id, websocket)


# ============================================================================
# Helper Functions for Orchestrator Integration
# ============================================================================

async def send_progress_update(
    experiment_id: UUID,
    iteration: int,
    total_iterations: int,
    progress_percent: float,
    current_strategy: str,
    elapsed_time_seconds: float
) -> None:
    """
    Send progress update via WebSocket.
    
    This function should be called by the Orchestrator during experiment execution.
    
    Args:
        experiment_id: Experiment UUID
        iteration: Current iteration number
        total_iterations: Total iterations
        progress_percent: Progress percentage (0-100)
        current_strategy: Current attack strategy
        elapsed_time_seconds: Elapsed time in seconds
    """
    await manager.broadcast(experiment_id, {
        "type": "progress",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "total_iterations": total_iterations,
        "progress_percent": progress_percent,
        "current_strategy": current_strategy,
        "elapsed_time_seconds": elapsed_time_seconds
    }, min_verbosity=1)  # Level 1: Events


async def send_iteration_complete(
    experiment_id: UUID,
    iteration: int,
    success: bool,
    judge_score: float,
    strategy_used: str,
    latency_breakdown: Optional[Dict[str, int]] = None,
    token_breakdown: Optional[Dict[str, int]] = None
) -> None:
    """
    Send iteration complete event via WebSocket with latency/token breakdowns.
    
    Args:
        experiment_id: Experiment UUID
        iteration: Iteration number
        success: Whether attack was successful
        judge_score: Judge evaluation score
        strategy_used: Attack strategy used
        latency_breakdown: Per-component latency breakdown (mutation_ms, target_ms, judge_ms, total_ms)
        token_breakdown: Per-agent token breakdown (attacker, target, judge, total)
    """
    message = {
        "type": "iteration_complete",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "success": success,
        "judge_score": judge_score,
        "strategy_used": strategy_used
    }
    if latency_breakdown:
        message["latency_breakdown"] = latency_breakdown
    if token_breakdown:
        message["token_breakdown"] = token_breakdown
    
    await manager.broadcast(experiment_id, message, min_verbosity=1)  # Level 1: Events


async def send_vulnerability_found(
    experiment_id: UUID,
    vulnerability_id: UUID,
    severity: str,
    iteration: int
) -> None:
    """
    Send vulnerability found event via WebSocket.
    
    Args:
        experiment_id: Experiment UUID
        vulnerability_id: Vulnerability UUID
        severity: Vulnerability severity
        iteration: Iteration where vulnerability was found
    """
    await manager.broadcast(experiment_id, {
        "type": "vulnerability_found",
        "experiment_id": str(experiment_id),
        "vulnerability_id": str(vulnerability_id),
        "severity": severity,
        "iteration": iteration
    }, min_verbosity=0)  # Level 0: Critical (always show)


async def send_experiment_complete(
    experiment_id: UUID,
    status: str,
    total_iterations: int,
    vulnerabilities_found: int,
    success_rate: float
) -> None:
    """
    Send experiment complete event via WebSocket.
    
    Args:
        experiment_id: Experiment UUID
        status: Final experiment status
        total_iterations: Total iterations executed
        vulnerabilities_found: Number of vulnerabilities found
        success_rate: Success rate (0-1)
    """
    await manager.broadcast(experiment_id, {
        "type": "experiment_complete",
        "experiment_id": str(experiment_id),
        "status": status,
        "total_iterations": total_iterations,
        "vulnerabilities_found": vulnerabilities_found,
        "success_rate": success_rate
    }, min_verbosity=1)  # Level 1: Events


async def send_error(
    experiment_id: UUID,
    error_message: str,
    iteration: Optional[int] = None
) -> None:
    """
    Send error event via WebSocket.
    
    Args:
        experiment_id: Experiment UUID
        error_message: Error message
        iteration: Iteration number if applicable
    """
    await manager.broadcast(experiment_id, {
        "type": "error",
        "experiment_id": str(experiment_id),
        "error_message": error_message,
        "iteration": iteration
    }, min_verbosity=0)  # Level 0: Errors


async def send_failure_analysis(
    experiment_id: UUID,
    failure_analysis: Dict[str, Any]
) -> None:
    """
    Send detailed failure analysis via WebSocket.
    
    Args:
        experiment_id: Experiment UUID
        failure_analysis: Structured failure analysis data
    """
    await manager.broadcast(experiment_id, {
        "type": "failure_analysis",
        "experiment_id": str(experiment_id),
        **failure_analysis  # Spread all analysis fields
    }, min_verbosity=0)  # Level 0: Always show (critical info)


# ============================================================================
# Live Monitoring Events (for Frontend Dashboard)
# ============================================================================

async def send_llm_request(
    experiment_id: UUID,
    role: str,
    provider: str,
    model: str,
    prompt: str,
    iteration: Optional[int] = None
) -> None:
    """
    Send LLM request event for live monitoring.
    
    Args:
        experiment_id: Experiment UUID
        role: LLM role (attacker, target, judge)
        provider: LLM provider (ollama, openai, etc.)
        model: Model name
        prompt: Request prompt (full content, truncation handled in UI)
        iteration: Current iteration number
    """
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)
    
    # DEBUG: Log before broadcast
    logger.info(f"[WS-SEND] send_llm_request called for exp {experiment_id}, role={role}, verbosity_required=2")
    
    message = {
        "type": "llm_request",
        "experiment_id": str(experiment_id),
        "role": role,
        "provider": provider,
        "model": model,
        "prompt": prompt,  # Send full prompt, truncation handled in UI
        "iteration": iteration,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # DEBUG: Log message content
    logger.info(f"[WS-SEND] Message: type={message['type']}, role={role}, prompt_len={len(prompt)}")
    
    await manager.broadcast(experiment_id, message, min_verbosity=2)  # Level 2: LLM Details
    
    # DEBUG: Log after broadcast
    logger.info(f"[WS-SEND] Broadcast completed for {experiment_id}")


async def send_llm_response(
    experiment_id: UUID,
    role: str,
    provider: str,
    model: str,
    response: str,
    latency_ms: float,
    tokens: Optional[int] = None,
    iteration: Optional[int] = None
) -> None:
    """
    Send LLM response event for live monitoring.
    
    Args:
        experiment_id: Experiment UUID
        role: LLM role (attacker, target, judge)
        provider: LLM provider
        model: Model name
        response: Response content (full content, truncation handled in UI)
        latency_ms: Response latency in milliseconds
        tokens: Token count if available
        iteration: Current iteration number
    """
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)
    
    # DEBUG: Log before broadcast
    logger.info(f"[WS-SEND] send_llm_response called for exp {experiment_id}, role={role}, verbosity_required=2")
    
    message = {
        "type": "llm_response",
        "experiment_id": str(experiment_id),
        "role": role,
        "provider": provider,
        "model": model,
        "response": response,  # Send full response, truncation handled in UI
        "latency_ms": latency_ms,
        "tokens": tokens,
        "iteration": iteration,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # DEBUG: Log message content
    logger.info(f"[WS-SEND] Message: type={message['type']}, role={role}, response_len={len(response)}, latency={latency_ms}ms")
    
    await manager.broadcast(experiment_id, message, min_verbosity=2)  # Level 2: LLM Details
    
    # DEBUG: Log after broadcast
    logger.info(f"[WS-SEND] Broadcast completed for {experiment_id}")


async def send_llm_error(
    experiment_id: UUID,
    role: str,
    provider: str,
    model: str,
    error_message: str,
    iteration: Optional[int] = None
) -> None:
    """
    Send LLM error event for live monitoring.
    """
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "llm_error",
        "experiment_id": str(experiment_id),
        "role": role,
        "provider": provider,
        "model": model,
        "error_message": error_message,
        "iteration": iteration,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=0)  # Level 0: Errors


async def send_judge_evaluation(
    experiment_id: UUID,
    iteration: int,
    judge_score: float,
    reasoning: str,
    success: bool,
    sub_scores: Optional[Dict[str, float]] = None,
    confidence: Optional[float] = None,
    latency_ms: Optional[float] = None,
    token_breakdown: Optional[Dict[str, int]] = None  # Comment 3: Add token_breakdown parameter
) -> None:
    """
    Send judge evaluation event with all 7 sub-scores for live monitoring.
    
    Args:
        experiment_id: Experiment UUID
        iteration: Iteration number
        judge_score: Score assigned by judge (0-10)
        reasoning: Judge's reasoning
        success: Whether attack was successful
        sub_scores: All 7 judge criteria scores (jailbreak_success, harmful_content, etc.)
        confidence: Judge confidence level (0-1)
        latency_ms: Judge evaluation latency in milliseconds
        token_breakdown: Token usage breakdown (attacker, target, judge, total) - Comment 3
    """
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)
    
    # DEBUG: Log before broadcast
    logger.info(f"[WS-SEND] send_judge_evaluation called for exp {experiment_id}, iteration={iteration}, score={judge_score}, success={success}")
    
    message = {
        "type": "judge_evaluation",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "judge_score": judge_score,
        "reasoning": reasoning[:500] + "..." if len(reasoning) > 500 else reasoning,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    if sub_scores:
        message["sub_scores"] = sub_scores
    if confidence is not None:
        message["confidence"] = confidence
    if latency_ms is not None:
        message["latency_ms"] = latency_ms
    if token_breakdown:  # Comment 3: Include token_breakdown in message
        message["token_breakdown"] = token_breakdown
    
    # DEBUG: Log message content
    logger.info(f"[WS-SEND] Message: type={message['type']}, score={judge_score}, success={success}, verbosity_required=2")
    
    await manager.broadcast(experiment_id, message, min_verbosity=2)  # Level 2: LLM Details
    
    # DEBUG: Log after broadcast
    logger.info(f"[WS-SEND] Broadcast completed for {experiment_id}")


async def send_attack_mutation(
    experiment_id: UUID,
    iteration: int,
    strategy: str,
    original_prompt: str,
    mutated_prompt: str,
    template_source: Optional[str] = None,
    template_category: Optional[str] = None,
    template_used_preview: Optional[str] = None
) -> None:
    """
    Send attack mutation event for live monitoring.
    
    Args:
        experiment_id: Experiment UUID
        iteration: Iteration number
        strategy: Attack strategy used
        original_prompt: Original prompt
        mutated_prompt: Mutated prompt
        template_source: Source of template used (payloads.json, hardcoded, etc.)
        template_category: Category of template used
        template_used_preview: Preview of template used (first 50 chars)
    """
    from datetime import datetime
    message = {
        "type": "attack_mutation",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "strategy_used": strategy,
        "original_prompt": original_prompt[:300] + "..." if len(original_prompt) > 300 else original_prompt,
        "mutated_prompt": mutated_prompt[:500] + "..." if len(mutated_prompt) > 500 else mutated_prompt,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add template metadata if provided
    if template_source or template_category or template_used_preview:
        message["template_metadata"] = {
            "template_source": template_source,
            "template_category": template_category,
            "template_used_preview": template_used_preview
        }
    
    await manager.broadcast(experiment_id, message, min_verbosity=2)  # Level 2: LLM Details


async def send_target_response(
    experiment_id: UUID,
    iteration: int,
    prompt: str,
    response: str,
    latency_ms: float
) -> None:
    """
    Send target response event for live monitoring.
    
    Args:
        experiment_id: Experiment UUID
        iteration: Iteration number
        prompt: Prompt sent to target
        response: Target's response
        latency_ms: Response latency
    """
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "target_response",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,
        "response": response[:1000] + "..." if len(response) > 1000 else response,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=2)  # Level 2: LLM Details


async def send_iteration_start(
    experiment_id: UUID,
    iteration: int,
    total_iterations: int,
    strategy: str
) -> None:
    """
    Send iteration start event for live monitoring.
    
    Args:
        experiment_id: Experiment UUID
        iteration: Iteration number
        total_iterations: Total iterations
        strategy: Attack strategy being used
    """
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "iteration_start",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "total_iterations": total_iterations,
        "strategy_used": strategy,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=1)  # Level 1: Events


async def send_task_update(
    experiment_id: UUID,
    task_id: str,
    task_name: str,
    status: str,
    queue_position: Optional[int] = None,
    dependencies: Optional[List[str]] = None
) -> None:
    """
    Send task queue update for live monitoring.
    
    Args:
        experiment_id: Experiment UUID
        task_id: Unique task identifier
        task_name: Human-readable task name
        status: Task status (queued, running, completed, failed)
        queue_position: Position in queue if queued
        dependencies: List of task IDs this task depends on (Phase 6)
    """
    from datetime import datetime
    message = {
        "type": f"task_{status}",
        "experiment_id": str(experiment_id),
        "task_id": task_id,
        "task_name": task_name,
        "status": status,
        "queue_position": queue_position,
        "timestamp": datetime.utcnow().isoformat()
    }
    if dependencies:
        message["dependencies"] = dependencies
    
    await manager.broadcast(experiment_id, message, min_verbosity=1)  # Level 1: Events


# ============================================================================
# Code-Flow Events (Verbosity Level 3)
# ============================================================================

async def send_code_flow_event(
    experiment_id: UUID,
    event_type: str,
    function_name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None,
    result: Optional[Any] = None,
    iteration: Optional[int] = None
) -> None:
    """
    Send generic code-flow event for verbosity level 3.
    
    Args:
        experiment_id: Experiment UUID
        event_type: Event type (function_call, decision, loop, etc.)
        function_name: Name of function/step
        description: Human-readable description
        parameters: Function parameters (truncated)
        result: Function result (truncated)
        iteration: Current iteration number
    """
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "code_flow",
        "experiment_id": str(experiment_id),
        "event_type": event_type,
        "function_name": function_name,
        "description": description,
        "parameters": parameters,
        "result": result,
        "iteration": iteration,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=3)  # Level 3: Code Flow


async def send_strategy_selection(
    experiment_id: UUID,
    iteration: int,
    strategy: str,
    reasoning: str,
    previous_score: Optional[float] = None,
    threshold: Optional[float] = None
) -> None:
    """Send strategy selection code-flow event."""
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "code_flow",
        "event_type": "strategy_selection",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "strategy": strategy,
        "reasoning": reasoning,
        "previous_score": previous_score,
        "threshold": threshold,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=3)  # Level 3: Code Flow


async def send_strategy_selection_detailed(
    experiment_id: UUID,
    iteration: int,
    selected_strategy: str,
    reasoning: str,
    available_strategies: List[str],
    preferred_categories: List[str],
    filtered_count: int,
    previous_score: Optional[float] = None,
    threshold: Optional[float] = None
) -> None:
    """
    Send detailed strategy selection event via WebSocket.
    
    Shows which strategies were considered, which were filtered, and why.
    """
    from datetime import datetime
    await manager.broadcast(
        experiment_id,
        {
            "type": "strategy_selection",
            "experiment_id": str(experiment_id),
            "iteration": iteration,
            "strategy": selected_strategy,
            "reasoning": reasoning,
            "available_strategies": available_strategies,
            "preferred_categories": preferred_categories,
            "filtered_count": filtered_count,
            "previous_score": previous_score,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        },
        min_verbosity=2  # Level 2: Detailed events
    )


async def send_mutation_start(
    experiment_id: UUID,
    iteration: int,
    strategy: str,
    original_prompt: str
) -> None:
    """Send mutation start code-flow event."""
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "code_flow",
        "event_type": "mutation_start",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "strategy": strategy,
        "original_prompt": original_prompt[:200] + "..." if len(original_prompt) > 200 else original_prompt,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=3)  # Level 3: Code Flow


async def send_mutation_end(
    experiment_id: UUID,
    iteration: int,
    strategy: str,
    mutated_prompt: str,
    latency_ms: float
) -> None:
    """Send mutation end code-flow event."""
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "code_flow",
        "event_type": "mutation_end",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "strategy": strategy,
        "mutated_prompt": mutated_prompt[:200] + "..." if len(mutated_prompt) > 200 else mutated_prompt,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=3)  # Level 3: Code Flow


async def send_judge_start(
    experiment_id: UUID,
    iteration: int,
    original_prompt: str,
    target_response: str
) -> None:
    """Send judge evaluation start code-flow event."""
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "code_flow",
        "event_type": "judge_start",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "original_prompt": original_prompt[:150] + "..." if len(original_prompt) > 150 else original_prompt,
        "target_response": target_response[:200] + "..." if len(target_response) > 200 else target_response,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=3)  # Level 3: Code Flow


async def send_judge_end(
    experiment_id: UUID,
    iteration: int,
    overall_score: float,
    all_scores: Dict[str, float],
    reasoning: str,
    latency_ms: float
) -> None:
    """Send judge evaluation end code-flow event."""
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "code_flow",
        "event_type": "judge_end",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "overall_score": overall_score,
        "all_scores": all_scores,
        "reasoning": reasoning[:300] + "..." if len(reasoning) > 300 else reasoning,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=3)  # Level 3: Code Flow


async def send_decision_point(
    experiment_id: UUID,
    iteration: int,
    decision_type: str,
    condition: str,
    decision_result: bool,
    description: str
) -> None:
    """Send decision point code-flow event (if/else, loops)."""
    from datetime import datetime
    await manager.broadcast(experiment_id, {
        "type": "code_flow",
        "event_type": "decision_point",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "decision_type": decision_type,
        "condition": condition,
        "decision_result": decision_result,  # Changed from 'result' to 'decision_result'
        "description": description,
        "timestamp": datetime.utcnow().isoformat()
    }, min_verbosity=3)  # Level 3: Code Flow


async def send_strategy_fallback(
    experiment_id: UUID,
    iteration: int,
    intended_strategy: str,
    fallback_strategy: str,
    reason: str
) -> None:
    """
    Send strategy fallback notification via WebSocket.
    
    Args:
        experiment_id: Experiment UUID
        iteration: Iteration number
        intended_strategy: Originally selected strategy
        fallback_strategy: Fallback strategy used
        reason: Reason for fallback (exception message)
    """
    from datetime import datetime
    message = {
        "type": "strategy_fallback",
        "experiment_id": str(experiment_id),
        "iteration": iteration,
        "intended_strategy": intended_strategy,
        "fallback_strategy": fallback_strategy,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast(experiment_id, message, min_verbosity=1)  # Level 1: Important events

