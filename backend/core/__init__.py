"""
backend/core/__init__.py
========================

Core module exports for CEREBRO-RED v2.

Exports all Pydantic models, database components, and telemetry infrastructure.
"""

from .models import (
    ExperimentConfig,
    AttackIteration,
    PromptMutation,
    JudgeScore,
    VulnerabilityFinding,
    ModelConfig,
    AttackStrategyType,
    VulnerabilitySeverity,
    ExperimentStatus,
    LLMProvider,
)
# Defer mutator import to avoid circular dependency with utils.llm_client
# PromptMutator will be imported lazily when needed
from .database import (
    init_db,
    get_session,
    close_db,
    ExperimentRepository,
    AttackIterationRepository,
    VulnerabilityRepository,
    JudgeScoreRepository,
    Base,
    ExperimentDB,
    AttackIterationDB,
    PromptMutationDB,
    JudgeScoreDB,
    VulnerabilityDB,
    ModelConfigDB,
)
from .telemetry import (
    get_audit_logger,
    AuditLogger,
    AuditLogEntry,
)
from .payloads import (
    get_payload_manager,
    PayloadManager,
)
from .scoring import (
    ScoringDefinitions,
    RefusalLevel,
    analyze_response_for_scoring,
)
# Defer judge import to avoid circular dependency with utils.llm_client
# SecurityJudge will be imported lazily when needed
# Use: from core.judge import SecurityJudge, get_security_judge

__all__ = [
    # Pydantic Models
    "ExperimentConfig",
    "AttackIteration",
    "PromptMutation",
    "JudgeScore",
    "VulnerabilityFinding",
    "ModelConfig",
    # Enums
    "AttackStrategyType",
    "VulnerabilitySeverity",
    "ExperimentStatus",
    "LLMProvider",
    # Mutator
    "PromptMutator",
    # Database
    "init_db",
    "get_session",
    "close_db",
    "ExperimentRepository",
    "AttackIterationRepository",
    "VulnerabilityRepository",
    "JudgeScoreRepository",
    "Base",
    "ExperimentDB",
    "AttackIterationDB",
    "PromptMutationDB",
    "JudgeScoreDB",
    "VulnerabilityDB",
    "ModelConfigDB",
    # Telemetry
    "get_audit_logger",
    "AuditLogger",
    "AuditLogEntry",
    # Note: log_strategy_transition is a method of AuditLogger, not exported separately
    # Payloads
    "get_payload_manager",
    "PayloadManager",
    # Scoring
    "ScoringDefinitions",
    "RefusalLevel",
    "analyze_response_for_scoring",
    # Judge (imported lazily to avoid circular dependency)
    # "SecurityJudge",  # Use: from core.judge import SecurityJudge
    # "get_security_judge",  # Use: from core.judge import get_security_judge
]

