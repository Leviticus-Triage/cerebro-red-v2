"""
Tests for telemetry and audit logging.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from uuid import uuid4

from core.telemetry import AuditLogger, AuditLogEntry, get_audit_logger
from core.models import AttackStrategyType


def test_audit_logger_initialization():
    """Test audit logger initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(Path(tmpdir))
        assert logger.log_path.exists()
        assert logger.retention_days == 90


def test_audit_log_entry_creation():
    """Test creating an audit log entry."""
    entry = AuditLogEntry(
        event_type="attack_attempt",
        experiment_id=uuid4(),
        iteration_number=1,
        model_attacker="qwen3:8b",
        model_target="qwen3:8b",
        prompt_hash="test_hash",
        latency_ms=150,
    )
    assert entry.event_type == "attack_attempt"
    assert entry.latency_ms == 150


def test_audit_logger_log_attack_attempt():
    """Test logging an attack attempt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(Path(tmpdir))
        experiment_id = uuid4()
        
        logger.log_attack_attempt(
            experiment_id=experiment_id,
            iteration=1,
            prompt="Test prompt",
            strategy=AttackStrategyType.OBFUSCATION_BASE64,
            model_attacker="qwen3:8b",
            model_target="qwen3:8b",
            latency_ms=150,
        )
        
        # Verify log file was created
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        assert len(log_files) > 0


def test_audit_logger_thread_safety():
    """Test thread-safe logging with concurrent writes."""
    import threading
    
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(Path(tmpdir))
        experiment_id = uuid4()
        
        def log_attack(i):
            logger.log_attack_attempt(
                experiment_id=experiment_id,
                iteration=i,
                prompt=f"Prompt {i}",
                strategy=AttackStrategyType.OBFUSCATION_BASE64,
                model_attacker="qwen3:8b",
                model_target="qwen3:8b",
                latency_ms=100 + i,
            )
        
        # Create multiple threads
        threads = [threading.Thread(target=log_attack, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify all entries were written
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        assert len(log_files) > 0
        
        # Count entries
        total_entries = 0
        for log_file in log_files:
            with open(log_file, "r") as f:
                total_entries += len(f.readlines())
        
        assert total_entries == 10


def test_audit_logger_get_stats():
    """Test getting statistics from logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(Path(tmpdir))
        experiment_id = uuid4()
        
        # Log some events
        logger.log_attack_attempt(
            experiment_id=experiment_id,
            iteration=1,
            prompt="Test",
            strategy=AttackStrategyType.OBFUSCATION_BASE64,
            model_attacker="qwen3:8b",
            model_target="qwen3:8b",
            latency_ms=150,
        )
        
        stats = logger.get_stats(experiment_id=experiment_id)
        assert stats["total_events"] > 0
        assert stats["attack_attempts"] > 0

