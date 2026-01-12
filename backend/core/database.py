# Copyright 2024-2026 Cerebro-Red v2 Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
backend/core/database.py
========================

SQLAlchemy ORM models and database configuration for CEREBRO-RED v2.

Implements async SQLAlchemy with SQLite backend, providing:
- ORM models for experiments, iterations, mutations, scores, vulnerabilities
- Repository pattern for CRUD operations
- Async session management with dependency injection
- Database initialization and migration support
"""

from datetime import datetime
from typing import AsyncGenerator, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, JSON, Index,
    ForeignKey, UniqueConstraint, text
)
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.types import Uuid as SQLiteUUID
from sqlalchemy.pool import NullPool, StaticPool

from utils.config import get_settings


# ============================================================================
# Database Setup
# ============================================================================

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Create async engine and session factory
_settings = get_settings()

# Get database URL
database_url = _settings.database.url

# Configure engine based on database type
if database_url.startswith("sqlite"):
    # SQLite: Use StaticPool for single connection (most reliable for SQLite)
    # This ensures all operations use the same connection
    _engine = create_async_engine(
        database_url,
        echo=_settings.database.echo,
        future=True,
        connect_args={
            "check_same_thread": False,
            "timeout": 60.0,
        },
        poolclass=StaticPool,  # Single shared connection for SQLite
    )
else:
    # PostgreSQL/MySQL: Use normal pooling
    _engine = create_async_engine(
        database_url,
        echo=_settings.database.echo,
        future=True,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
    )

AsyncSessionLocal = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# ============================================================================
# ORM Models
# ============================================================================

class ExperimentDB(Base):
    """Experiment table."""
    
    __tablename__ = "experiments"
    
    experiment_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_model_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    target_model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    attacker_model_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    attacker_model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    judge_model_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    judge_model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    initial_prompts: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    strategies: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    max_concurrent_attacks: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    success_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=7.0)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=3600)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    experiment_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    
    # Relationships
    iterations: Mapped[List["AttackIterationDB"]] = relationship(
        "AttackIterationDB", back_populates="experiment", cascade="all, delete-orphan"
    )
    vulnerabilities: Mapped[List["VulnerabilityDB"]] = relationship(
        "VulnerabilityDB", back_populates="experiment", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_experiments_created_at", "created_at"),
    )


class AttackIterationDB(Base):
    """Attack iteration table."""
    
    __tablename__ = "attack_iterations"
    
    iteration_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, primary_key=True, default=uuid4
    )
    experiment_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("experiments.experiment_id", ondelete="CASCADE"), nullable=False
    )
    iteration_number: Mapped[int] = mapped_column(Integer, nullable=False)
    strategy_used: Mapped[str] = mapped_column(String(50), nullable=False)
    # NEW: Originally intended strategy (before fallbacks)
    intended_strategy: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,  # Nullable for backward compatibility
        comment="Originally selected strategy before any fallbacks"
    )
    # NEW: Whether a fallback occurred
    strategy_fallback_occurred: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False,
        comment="True if executed_strategy differs from intended_strategy"
    )
    # NEW: Reason for fallback (if any)
    fallback_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Exception message or reason for strategy fallback"
    )
    original_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    mutated_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    target_response: Mapped[str] = mapped_column(Text, nullable=False)
    judge_score: Mapped[float] = mapped_column(Float, nullable=False)
    judge_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    attacker_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    experiment: Mapped["ExperimentDB"] = relationship("ExperimentDB", back_populates="iterations")
    mutations: Mapped[List["PromptMutationDB"]] = relationship(
        "PromptMutationDB", back_populates="iteration", cascade="all, delete-orphan"
    )
    judge_scores: Mapped[List["JudgeScoreDB"]] = relationship(
        "JudgeScoreDB", back_populates="iteration", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_attack_iterations_experiment_number", "experiment_id", "iteration_number"),
    )


class PromptMutationDB(Base):
    """Prompt mutation table."""
    
    __tablename__ = "prompt_mutations"
    
    mutation_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, primary_key=True, default=uuid4
    )
    iteration_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("attack_iterations.iteration_id", ondelete="CASCADE"), nullable=False
    )
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    output_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    mutation_params: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA256
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    iteration: Mapped["AttackIterationDB"] = relationship(
        "AttackIterationDB", back_populates="mutations"
    )
    
    __table_args__ = (
        Index("idx_prompt_mutations_hash", "prompt_hash"),
    )


class JudgeScoreDB(Base):
    """Judge score table."""
    
    __tablename__ = "judge_scores"
    
    score_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, primary_key=True, default=uuid4
    )
    iteration_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("attack_iterations.iteration_id", ondelete="CASCADE"), nullable=False
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    jailbreak_success_score: Mapped[float] = mapped_column(Float, nullable=False)
    harmful_content_score: Mapped[float] = mapped_column(Float, nullable=False)
    hallucination_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bias_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    logical_consistency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sycophancy_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    policy_violation_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    fallback_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    judge_model: Mapped[str] = mapped_column(String(200), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    iteration: Mapped["AttackIterationDB"] = relationship(
        "AttackIterationDB", back_populates="judge_scores"
    )
    
    __table_args__ = (
        Index("idx_judge_scores_overall", "overall_score"),
    )


class VulnerabilityDB(Base):
    """Vulnerability finding table."""
    
    __tablename__ = "vulnerabilities"
    
    vulnerability_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, primary_key=True, default=uuid4
    )
    experiment_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("experiments.experiment_id", ondelete="CASCADE"), nullable=False
    )
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    successful_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    target_response: Mapped[str] = mapped_column(Text, nullable=False)
    attack_strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    iteration_number: Mapped[int] = mapped_column(Integer, nullable=False)
    judge_score: Mapped[float] = mapped_column(Float, nullable=False)
    reproducible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cve_references: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    mitigation_suggestions: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    experiment_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    
    # Relationships
    experiment: Mapped["ExperimentDB"] = relationship(
        "ExperimentDB", back_populates="vulnerabilities"
    )
    
    __table_args__ = (
        Index("idx_vulnerabilities_severity", "severity"),
        Index("idx_vulnerabilities_discovered_at", "discovered_at"),
    )


class ModelConfigDB(Base):
    """Model configuration table."""
    
    __tablename__ = "model_configs"
    
    config_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, primary_key=True, default=uuid4
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    api_base: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key_env_var: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    additional_params: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    __table_args__ = (
        UniqueConstraint("provider", "model_name", name="uq_model_config_provider_model"),
    )


class ExperimentTemplateDB(Base):
    """Experiment template table for saving/loading configurations."""
    
    __tablename__ = "experiment_templates"
    
    template_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of ExperimentConfig
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    __table_args__ = (
        Index("idx_templates_created_at", "created_at"),
        Index("idx_templates_name", "name"),
        Index("idx_templates_is_public", "is_public"),
    )


# ============================================================================
# Database Initialization
# ============================================================================

async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This function should be called on application startup to ensure
    all tables exist before processing requests.
    
    For SQLite, enables WAL mode for better concurrency.
    """
    async with _engine.begin() as conn:
        # Enable WAL mode for SQLite (better concurrency, allows readers during writes)
        if _settings.database.url.startswith("sqlite"):
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))
            await conn.execute(text("PRAGMA busy_timeout=30000"))  # 30 second timeout
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    
    This function should be called on application shutdown to properly
    clean up database connections.
    """
    await _engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for FastAPI routes.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        >>> @app.get("/experiments")
        >>> async def list_experiments(session: AsyncSession = Depends(get_session)):
        >>>     ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# Repository Pattern for CRUD Operations
# ============================================================================

class ExperimentRepository:
    """Repository for experiment CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, experiment: "ExperimentConfig") -> ExperimentDB:
        """Create a new experiment with transaction logging."""
        import logging
        from datetime import datetime
        
        logger = logging.getLogger(__name__)
        logger.debug(f"Creating experiment: {experiment.name}")
        
        try:
            # Ensure created_at is set
            created_at = experiment.created_at if hasattr(experiment, 'created_at') and experiment.created_at else datetime.utcnow()
            
            db_experiment = ExperimentDB(
                experiment_id=experiment.experiment_id,
                name=experiment.name,
                description=experiment.description,
                target_model_provider=experiment.target_model_provider.value,
                target_model_name=experiment.target_model_name,
                attacker_model_provider=experiment.attacker_model_provider.value,
                attacker_model_name=experiment.attacker_model_name,
                judge_model_provider=experiment.judge_model_provider.value,
                judge_model_name=experiment.judge_model_name,
                initial_prompts=experiment.initial_prompts,
                strategies=[s.value for s in experiment.strategies],
                max_iterations=experiment.max_iterations,
                max_concurrent_attacks=experiment.max_concurrent_attacks,
                success_threshold=experiment.success_threshold,
                timeout_seconds=experiment.timeout_seconds,
                status="pending",
                created_at=created_at,
                experiment_metadata=experiment.metadata or {},
            )
            self.session.add(db_experiment)
            await self.session.flush()  # Flush to catch DB errors before commit
            
            logger.debug(f"Experiment flushed to DB: {db_experiment.experiment_id}")
            
            return db_experiment
            
        except Exception as e:
            logger.error(f"Database error creating experiment: {type(e).__name__} - {str(e)}")
            raise
    
    async def get_by_id(self, experiment_id: UUID) -> Optional[ExperimentDB]:
        """Get experiment by ID."""
        return await self.session.get(ExperimentDB, experiment_id)
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[ExperimentDB]:
        """List all experiments with pagination."""
        from sqlalchemy import select
        stmt = select(ExperimentDB).limit(limit).offset(offset).order_by(ExperimentDB.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_status(self, experiment_id: UUID, status: str) -> Optional[ExperimentDB]:
        """Update experiment status."""
        experiment = await self.get_by_id(experiment_id)
        if experiment:
            experiment.status = status
            await self.session.flush()
        return experiment
    
    async def delete(self, experiment_id: UUID) -> bool:
        """Delete an experiment."""
        experiment = await self.get_by_id(experiment_id)
        if experiment:
            await self.session.delete(experiment)
            await self.session.flush()
            return True
        return False


class AttackIterationRepository:
    """Repository for attack iteration CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, iteration: "AttackIteration") -> AttackIterationDB:
        """Create a new attack iteration."""
        
        # Convert enums to strings with validation
        strategy_used_str = iteration.strategy_used.value if hasattr(iteration.strategy_used, 'value') else str(iteration.strategy_used)
        
        # NEW: Handle intended_strategy (may be None for old data)
        intended_strategy_str = None
        if iteration.intended_strategy:
            intended_strategy_str = iteration.intended_strategy.value if hasattr(iteration.intended_strategy, 'value') else str(iteration.intended_strategy)
        
        # NEW: Log if strategies differ (data integrity check)
        if intended_strategy_str and intended_strategy_str != strategy_used_str:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Strategy mismatch detected: intended={intended_strategy_str}, "
                f"executed={strategy_used_str}, fallback={iteration.strategy_fallback_occurred}"
            )
        
        db_iteration = AttackIterationDB(
            iteration_id=iteration.iteration_id,
            experiment_id=iteration.experiment_id,
            iteration_number=iteration.iteration_number,
            strategy_used=strategy_used_str,
            intended_strategy=intended_strategy_str,  # NEW
            strategy_fallback_occurred=iteration.strategy_fallback_occurred,  # NEW
            fallback_reason=iteration.fallback_reason,  # NEW
            original_prompt=iteration.original_prompt,
            mutated_prompt=iteration.mutated_prompt,
            target_response=iteration.target_response,
            judge_score=iteration.judge_score,
            judge_reasoning=iteration.judge_reasoning,
            success=iteration.success,
            latency_ms=iteration.latency_ms,
            timestamp=iteration.timestamp,
            attacker_feedback=iteration.attacker_feedback,
        )
        self.session.add(db_iteration)
        await self.session.flush()
        return db_iteration
    
    async def get_by_experiment(
        self, experiment_id: UUID, limit: int = 100
    ) -> List[AttackIterationDB]:
        """Get all iterations for an experiment."""
        from sqlalchemy import select
        stmt = (
            select(AttackIterationDB)
            .where(AttackIterationDB.experiment_id == experiment_id)
            .order_by(AttackIterationDB.iteration_number)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_successful_attacks(
        self, experiment_id: UUID
    ) -> List[AttackIterationDB]:
        """Get all successful attacks for an experiment."""
        from sqlalchemy import select
        stmt = (
            select(AttackIterationDB)
            .where(
                AttackIterationDB.experiment_id == experiment_id,
                AttackIterationDB.success == True
            )
            .order_by(AttackIterationDB.iteration_number)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class VulnerabilityRepository:
    """Repository for vulnerability CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, vulnerability: "VulnerabilityFinding") -> VulnerabilityDB:
        """Create a new vulnerability finding."""
        db_vulnerability = VulnerabilityDB(
            vulnerability_id=vulnerability.vulnerability_id,
            experiment_id=vulnerability.experiment_id,
            severity=vulnerability.severity.value,
            title=vulnerability.title,
            description=vulnerability.description,
            successful_prompt=vulnerability.successful_prompt,
            target_response=vulnerability.target_response,
            attack_strategy=vulnerability.attack_strategy.value,
            iteration_number=vulnerability.iteration_number,
            judge_score=vulnerability.judge_score,
            reproducible=vulnerability.reproducible,
            cve_references=vulnerability.cve_references,
            mitigation_suggestions=vulnerability.mitigation_suggestions,
            discovered_at=vulnerability.discovered_at,
            experiment_metadata=vulnerability.metadata,
        )
        self.session.add(db_vulnerability)
        await self.session.flush()
        return db_vulnerability
    
    async def get_by_severity(
        self, severity: str, limit: int = 100
    ) -> List[VulnerabilityDB]:
        """Get vulnerabilities by severity level."""
        from sqlalchemy import select
        stmt = (
            select(VulnerabilityDB)
            .where(VulnerabilityDB.severity == severity)
            .order_by(VulnerabilityDB.discovered_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_experiment(
        self, experiment_id: UUID
    ) -> List[VulnerabilityDB]:
        """Get all vulnerabilities for an experiment."""
        from sqlalchemy import select
        stmt = (
            select(VulnerabilityDB)
            .where(VulnerabilityDB.experiment_id == experiment_id)
            .order_by(VulnerabilityDB.discovered_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class JudgeScoreRepository:
    """Repository for judge score CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, judge_score) -> JudgeScoreDB:
        """
        Create a new judge score record.
        
        Args:
            judge_score: JudgeScore Pydantic model instance
            
        Returns:
            Created JudgeScoreDB instance
        """
        db_score = JudgeScoreDB(
            score_id=judge_score.score_id,
            iteration_id=judge_score.iteration_id,
            overall_score=judge_score.overall_score,
            jailbreak_success_score=judge_score.jailbreak_success_score,
            harmful_content_score=judge_score.harmful_content_score,
            hallucination_score=judge_score.hallucination_score,
            bias_score=judge_score.bias_score,
            logical_consistency_score=judge_score.logical_consistency_score,
            sycophancy_score=judge_score.sycophancy_score,
            policy_violation_score=judge_score.policy_violation_score,
            confidence=judge_score.confidence,
            reasoning=judge_score.reasoning,
            fallback_used=judge_score.fallback_used,
            judge_model=judge_score.judge_model,
            timestamp=judge_score.timestamp,
        )
        self.session.add(db_score)
        await self.session.flush()
        return db_score
    
    async def get_by_iteration(
        self, iteration_id: UUID
    ) -> Optional[JudgeScoreDB]:
        """Get judge score for a specific iteration."""
        from sqlalchemy import select
        stmt = (
            select(JudgeScoreDB)
            .where(JudgeScoreDB.iteration_id == iteration_id)
            .order_by(JudgeScoreDB.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_experiment(
        self, experiment_id: UUID, limit: int = 100
    ) -> List[JudgeScoreDB]:
        """Get all judge scores for an experiment (via iterations)."""
        from sqlalchemy import select
        from sqlalchemy.orm import aliased
        
        # Join with attack_iterations to filter by experiment_id
        stmt = (
            select(JudgeScoreDB)
            .join(AttackIterationDB, JudgeScoreDB.iteration_id == AttackIterationDB.iteration_id)
            .where(AttackIterationDB.experiment_id == experiment_id)
            .order_by(JudgeScoreDB.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ExperimentTemplateRepository:
    """Repository for experiment template CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, template: "ExperimentTemplateCreate") -> ExperimentTemplateDB:
        """Create a new experiment template."""
        from core.models import ExperimentConfig
        import json
        
        # Serialize ExperimentConfig to JSON string
        config_json = template.config.model_dump_json()
        
        db_template = ExperimentTemplateDB(
            template_id=uuid4(),
            name=template.name,
            description=template.description,
            config_json=config_json,
            tags=template.tags,
            is_public=template.is_public,
            created_by=template.created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            usage_count=0,
        )
        self.session.add(db_template)
        await self.session.flush()
        return db_template
    
    async def get_by_id(self, template_id: UUID) -> Optional[ExperimentTemplateDB]:
        """Get template by ID."""
        return await self.session.get(ExperimentTemplateDB, template_id)
    
    async def list_all(
        self, 
        limit: int = 100, 
        offset: int = 0,
        is_public: Optional[bool] = None,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> tuple[List[ExperimentTemplateDB], int]:
        """
        List templates with optional filters.
        
        Returns:
            Tuple of (filtered_templates, total_count)
            where total_count is the count AFTER tag filtering.
        """
        from sqlalchemy import select, and_
        
        conditions = []
        if is_public is not None:
            conditions.append(ExperimentTemplateDB.is_public == is_public)
        if created_by is not None:
            conditions.append(ExperimentTemplateDB.created_by == created_by)
        
        # Load all candidates first (without limit/offset)
        stmt = (
            select(ExperimentTemplateDB)
            .where(and_(*conditions) if conditions else True)
            .order_by(ExperimentTemplateDB.created_at.desc())
        )
        result = await self.session.execute(stmt)
        all_templates = list(result.scalars().all())
        
        # Apply tag filtering in Python (SQLite JSON limitations)
        if tags:
            all_templates = [t for t in all_templates if any(tag in t.tags for tag in tags)]
        
        # Calculate total count AFTER tag filtering
        total_count = len(all_templates)
        
        # Apply pagination AFTER filtering
        paginated_templates = all_templates[offset:offset + limit]
        
        return paginated_templates, total_count
    
    async def update(
        self, 
        template_id: UUID, 
        update_data: "ExperimentTemplateUpdate"
    ) -> Optional[ExperimentTemplateDB]:
        """Update template."""
        template = await self.get_by_id(template_id)
        if not template:
            return None
        
        # Update fields if provided
        if update_data.name is not None:
            template.name = update_data.name
        if update_data.description is not None:
            template.description = update_data.description
        if update_data.config is not None:
            template.config_json = update_data.config.model_dump_json()
        if update_data.tags is not None:
            template.tags = update_data.tags
        if update_data.is_public is not None:
            template.is_public = update_data.is_public
        
        template.updated_at = datetime.utcnow()
        await self.session.flush()
        return template
    
    async def delete(self, template_id: UUID) -> bool:
        """Delete template."""
        template = await self.get_by_id(template_id)
        if template:
            await self.session.delete(template)
            await self.session.flush()
            return True
        return False
    
    async def increment_usage(self, template_id: UUID) -> None:
        """Increment usage count when template is used."""
        template = await self.get_by_id(template_id)
        if template:
            template.usage_count += 1
            await self.session.flush()
