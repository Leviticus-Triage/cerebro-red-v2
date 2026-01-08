"""
backend/core/telemetry.py
=========================

Thread-safe JSONL audit logger for research-grade telemetry.

Implements structured logging to JSONL files with:
- Thread-safe concurrent writes using locks
- Daily log rotation
- Automatic log retention cleanup
- Comprehensive event tracking for PAIR algorithm lifecycle
"""

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from core.models import AttackStrategyType
from utils.config import get_settings


# ============================================================================
# Audit Log Entry Model
# ============================================================================

class AuditLogEntry(BaseModel):
    """Audit log entry schema for JSONL format."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    event_type: str = Field(..., description="Event type (attack_attempt, judge_evaluation, mutation, error)")
    experiment_id: UUID = Field(..., description="Experiment ID")
    iteration_number: Optional[int] = Field(None, description="Iteration number")
    model_attacker: str = Field(..., description="Attacker model identifier")
    model_target: str = Field(..., description="Target model identifier")
    model_judge: Optional[str] = Field(None, description="Judge model identifier")
    strategy: Optional[str] = Field(None, description="Attack strategy used")
    prompt_hash: str = Field(..., description="SHA256 hash of prompt")
    success_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Success score")
    latency_ms: int = Field(..., ge=0, description="Request latency in milliseconds")
    tokens_used: Optional[int] = Field(None, ge=0, description="Tokens used")
    error: Optional[str] = Field(None, description="Error message if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ============================================================================
# Audit Logger Class
# ============================================================================

class AuditLogger:
    """
    Thread-safe JSONL audit logger for research telemetry.
    
    This logger writes structured log entries to JSONL files with automatic
    rotation and retention management. All writes are thread-safe using locks.
    
    Attributes:
        log_path: Directory path for log files
        current_log_file: Path to current log file
        lock: Thread lock for safe concurrent writes
        retention_days: Number of days to retain logs
        
    Example:
        >>> logger = AuditLogger(Path("./data/audit_logs"))
        >>> logger.log_attack_attempt(
        ...     experiment_id=uuid4(),
        ...     iteration=1,
        ...     prompt="test prompt",
        ...     strategy=AttackStrategyType.OBFUSCATION_BASE64,
        ...     latency_ms=150
        ... )
    """
    
    def __init__(self, log_path: Path, retention_days: int = 90):
        """
        Initialize audit logger.
        
        Args:
            log_path: Directory path for log files
            retention_days: Number of days to retain logs (default: 90)
        """
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.lock = threading.Lock()
        self.current_log_file = self._get_current_log_file()
        self._last_rotation_date = datetime.now().date()
    
    def _get_current_log_file(self) -> Path:
        """Get current log file path based on date."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_path / f"audit_{today}.jsonl"
    
    def _write_entry(self, entry: AuditLogEntry) -> None:
        """
        Thread-safe write of log entry to JSONL file.
        
        Args:
            entry: Audit log entry to write
        """
        with self.lock:
            # Check if rotation is needed
            current_date = datetime.now().date()
            if current_date != self._last_rotation_date:
                self.rotate_logs()
                self._last_rotation_date = current_date
                self.current_log_file = self._get_current_log_file()
            
            # Serialize entry to JSON
            entry_dict = entry.model_dump(mode="json")
            json_line = json.dumps(entry_dict, ensure_ascii=False, default=str)
            
            # Append to log file
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(json_line + "\n")
                f.flush()  # Flush immediately for real-time analysis
    
    def log_attack_attempt(
        self,
        experiment_id: UUID,
        iteration: int,
        prompt: str,
        strategy: AttackStrategyType,
        model_attacker: str,
        model_target: str,
        latency_ms: int,
        tokens_used: Optional[int] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an attack attempt event.
        
        Args:
            experiment_id: Experiment ID
            iteration: Iteration number
            prompt: Prompt used in attack
            strategy: Attack strategy used
            model_attacker: Attacker model identifier
            model_target: Target model identifier
            latency_ms: Request latency in milliseconds
            tokens_used: Number of tokens used (optional)
            error: Error message if attack failed (optional)
            metadata: Additional metadata (optional)
        """
        import hashlib
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        
        entry = AuditLogEntry(
            event_type="attack_attempt",
            experiment_id=experiment_id,
            iteration_number=iteration,
            model_attacker=model_attacker,
            model_target=model_target,
            strategy=strategy.value,
            prompt_hash=prompt_hash,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            error=error,
            metadata=metadata or {},
        )
        self._write_entry(entry)
    
    def log_judge_evaluation(
        self,
        experiment_id: UUID,
        iteration: int,
        score: float,
        reasoning: str,
        model_judge: str,
        model_target: str,
        latency_ms: int,
        confidence: Optional[float] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a judge evaluation event.
        
        Args:
            experiment_id: Experiment ID
            iteration: Iteration number
            score: Judge evaluation score
            reasoning: Judge reasoning/explanation
            model_judge: Judge model identifier
            model_target: Target model identifier
            latency_ms: Request latency in milliseconds
            confidence: Judge confidence level (optional)
            tokens_used: Number of tokens used (optional)
            metadata: Additional metadata (optional)
        """
        entry = AuditLogEntry(
            event_type="judge_evaluation",
            experiment_id=experiment_id,
            iteration_number=iteration,
            model_attacker="",  # Not applicable for judge evaluation
            model_target=model_target,
            model_judge=model_judge,
            prompt_hash="",  # Will be set from attack attempt
            success_score=score,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            metadata={
                **(metadata or {}),
                "reasoning": reasoning,
                "confidence": confidence,
            },
        )
        self._write_entry(entry)
    
    def log_mutation(
        self,
        experiment_id: UUID,
        iteration: int,
        strategy: AttackStrategyType,
        input_prompt: str,
        output_prompt: str,
        model_attacker: str,
        latency_ms: int,
        mutation_params: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a prompt mutation event.
        
        Args:
            experiment_id: Experiment ID
            iteration: Iteration number
            strategy: Mutation strategy used
            input_prompt: Original prompt
            output_prompt: Mutated prompt
            model_attacker: Attacker model identifier
            latency_ms: Mutation latency in milliseconds
            mutation_params: Strategy-specific parameters (optional)
            metadata: Additional metadata (optional)
        """
        import hashlib
        prompt_hash = hashlib.sha256(output_prompt.encode()).hexdigest()
        
        entry = AuditLogEntry(
            event_type="mutation",
            experiment_id=experiment_id,
            iteration_number=iteration,
            model_attacker=model_attacker,
            model_target="",  # Not applicable for mutation
            strategy=strategy.value,
            prompt_hash=prompt_hash,
            latency_ms=latency_ms,
            metadata={
                **(metadata or {}),
                "input_prompt": input_prompt,
                "output_prompt": output_prompt,
                "mutation_params": mutation_params or {},
            },
        )
        self._write_entry(entry)
    
    def log_error(
        self,
        experiment_id: UUID,
        error_type: str,
        error_message: str,
        iteration: Optional[int] = None,
        model_attacker: Optional[str] = None,
        model_target: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an error event.
        
        Args:
            experiment_id: Experiment ID
            error_type: Type of error (e.g., "llm_timeout", "validation_error")
            error_message: Error message
            iteration: Iteration number if applicable (optional)
            model_attacker: Attacker model identifier if applicable (optional)
            model_target: Target model identifier if applicable (optional)
            metadata: Additional metadata (optional)
        """
        entry = AuditLogEntry(
            event_type="error",
            experiment_id=experiment_id,
            iteration_number=iteration,
            model_attacker=model_attacker or "",
            model_target=model_target or "",
            prompt_hash="",
            latency_ms=0,
            error=f"{error_type}: {error_message}",
            metadata=metadata or {},
        )
        self._write_entry(entry)
    
    def rotate_logs(self) -> None:
        """
        Rotate log files (creates new file for new day).
        
        This is called automatically when the date changes.
        """
        # Log rotation is handled automatically by date-based filenames
        # This method can be extended for additional rotation logic
        pass
    
    def cleanup_old_logs(self) -> None:
        """
        Delete log files older than retention_days.
        
        This should be called periodically (e.g., daily) to manage disk space.
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        with self.lock:
            for log_file in self.log_path.glob("audit_*.jsonl"):
                # Extract date from filename
                try:
                    date_str = log_file.stem.replace("audit_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if file_date < cutoff_date.date():
                        log_file.unlink()
                except ValueError:
                    # Skip files with invalid date format
                    continue
    
    def log_strategy_transition(
        self,
        experiment_id: UUID,
        iteration: int,
        from_strategy: str,
        to_strategy: str,
        reason: str,
        judge_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log strategy transitions for PAIR algorithm analysis.
        
        This enables research analysis of how the algorithm adapts
        based on feedback (key metric for PAIR paper validation).
        
        Args:
            experiment_id: Experiment ID
            iteration: Current iteration number
            from_strategy: Previous strategy used
            to_strategy: New strategy selected
            reason: Reason for transition (from strategy analysis)
            judge_score: Judge score that triggered transition
            metadata: Additional metadata (optional)
        """
        import hashlib
        # Create a hash for the transition event
        transition_hash = hashlib.sha256(
            f"{experiment_id}{iteration}{from_strategy}{to_strategy}".encode()
        ).hexdigest()
        
        entry = AuditLogEntry(
            event_type="strategy_transition",
            experiment_id=experiment_id,
            iteration_number=iteration,
            model_attacker="",  # Not applicable for transitions
            model_target="",  # Not applicable for transitions
            prompt_hash=transition_hash,
            success_score=judge_score,
            latency_ms=0,
            metadata={
                **(metadata or {}),
                "from_strategy": from_strategy,
                "to_strategy": to_strategy,
                "transition_reason": reason,
            },
        )
        self._write_entry(entry)
    
    def log_strategy_usage_summary(
        self,
        experiment_id: UUID,
        total_iterations: int,
        strategies_selected: List[str],  # User-selected
        strategies_used: Dict[str, int],  # Actually used with counts
        strategies_skipped: List[str],  # Never used
        strategies_skipped_count: Optional[int] = None  # Comment 2: Explicit count (for test compatibility)
    ) -> None:
        """
        Log summary of strategy usage for experiment.
        
        Args:
            experiment_id: Experiment UUID
            total_iterations: Total iterations run
            strategies_selected: All strategies user selected
            strategies_used: Dict of strategy → usage count
            strategies_skipped: Strategies that were never used
        """
        import hashlib
        summary_hash = hashlib.sha256(
            f"{experiment_id}strategy_usage_summary".encode()
        ).hexdigest()
        
        # Use provided count or calculate from list (Comment 2)
        skipped_count = strategies_skipped_count if strategies_skipped_count is not None else len(strategies_skipped)
        
        entry = AuditLogEntry(
            event_type="strategy_usage_summary",
            experiment_id=experiment_id,
            iteration_number=total_iterations,
            model_attacker="",  # Not applicable
            model_target="",  # Not applicable
            prompt_hash=summary_hash,
            success_score=None,
            latency_ms=0,
            metadata={
                "total_iterations": total_iterations,
                "strategies_selected_count": len(strategies_selected),
                "strategies_used_count": len(strategies_used),
                "strategies_skipped_count": skipped_count,
                "strategies_selected": strategies_selected,
                "strategies_used": strategies_used,
                "strategies_skipped": strategies_skipped,
                "usage_rate": len(strategies_used) / len(strategies_selected) if strategies_selected else 0.0
            },
        )
        self._write_entry(entry)
    
    def log_event(
        self,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        experiment_id: Optional[UUID] = None,
    ) -> None:
        """
        Log a generic event (e.g., system events, audits).
        
        Args:
            event_type: Type of event (e.g., "payload_coverage_audit")
            metadata: Additional metadata dictionary
            experiment_id: Experiment ID if applicable (optional, uses system UUID if None)
        """
        from uuid import uuid4 as uuid4_func
        
        # Use system UUID if no experiment_id provided
        system_uuid = UUID("00000000-0000-0000-0000-000000000000")
        entry = AuditLogEntry(
            event_type=event_type,
            experiment_id=experiment_id or system_uuid,
            iteration_number=None,
            model_attacker="system",
            model_target="system",
            model_judge=None,
            strategy=None,
            prompt_hash="",
            success_score=None,
            latency_ms=0,
            tokens_used=None,
            error=None,
            metadata=metadata or {},
        )
        self._write_entry(entry)
    
    def get_stats(self, experiment_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get aggregate statistics from log files.
        
        Args:
            experiment_id: Filter by experiment ID (optional)
            
        Returns:
            Dictionary with statistics (total_events, successful_attacks, etc.)
        """
        stats = {
            "total_events": 0,
            "attack_attempts": 0,
            "judge_evaluations": 0,
            "mutations": 0,
            "errors": 0,
            "successful_attacks": 0,
            "total_latency_ms": 0,
            "total_tokens": 0,
        }
        
        with self.lock:
            for log_file in sorted(self.log_path.glob("audit_*.jsonl")):
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry_dict = json.loads(line)
                            
                            # Filter by experiment_id if provided
                            if experiment_id:
                                entry_exp_id = UUID(entry_dict.get("experiment_id", ""))
                                if entry_exp_id != experiment_id:
                                    continue
                            
                            stats["total_events"] += 1
                            event_type = entry_dict.get("event_type", "")
                            
                            if event_type == "attack_attempt":
                                stats["attack_attempts"] += 1
                            elif event_type == "judge_evaluation":
                                stats["judge_evaluations"] += 1
                                if entry_dict.get("success_score", 0) >= 7.0:
                                    stats["successful_attacks"] += 1
                            elif event_type == "mutation":
                                stats["mutations"] += 1
                            elif event_type == "error":
                                stats["errors"] += 1
                            
                            stats["total_latency_ms"] += entry_dict.get("latency_ms", 0)
                            stats["total_tokens"] += entry_dict.get("tokens_used", 0) or 0
                        except (json.JSONDecodeError, KeyError, ValueError):
                            # Skip invalid log entries
                            continue
        
        return stats


# ============================================================================
# Singleton Pattern
# ============================================================================

_audit_logger_instance: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """
    Get singleton AuditLogger instance.
    
    Returns:
        Cached AuditLogger instance
        
    Example:
        >>> logger = get_audit_logger()
        >>> logger.log_attack_attempt(...)
    """
    global _audit_logger_instance
    if _audit_logger_instance is None:
        settings = get_settings()
        _audit_logger_instance = AuditLogger(
            settings.telemetry.path,
            settings.telemetry.retention_days
        )
    return _audit_logger_instance
