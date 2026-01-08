"""
Benchmark tests for database indexes.

Tests query performance with and without indexes to measure
the impact of the new performance indexes.
"""

import pytest
import asyncio
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta

from core.database import AsyncSessionLocal, ExperimentDB, AttackIterationDB
from core.models import ExperimentStatus


@pytest.mark.benchmark
@pytest.mark.asyncio(loop_scope="function")
async def test_experiments_status_created_at_index():
    """
    Benchmark query using experiments(status, created_at) composite index.
    
    Tests filtering by status and sorting by created_at.
    """
    async with AsyncSessionLocal() as session:
        # Create test data
        experiments = []
        for i in range(100):
            exp = ExperimentDB(
                name=f"Test Experiment {i}",
                target_model_provider="ollama",
                target_model_name="qwen2.5:3b",
                attacker_model_provider="ollama",
                attacker_model_name="qwen2.5:3b",
                judge_model_provider="ollama",
                judge_model_name="qwen2.5:7b",
                initial_prompts=["test"],
                strategies=["roleplay_injection"],
                status="completed" if i % 2 == 0 else "running",
                created_at=datetime.utcnow() - timedelta(days=i),
            )
            experiments.append(exp)
        
        session.add_all(experiments)
        await session.commit()
        
        # Benchmark query using index
        async def query_with_index():
            result = await session.execute(
                select(ExperimentDB)
                .where(ExperimentDB.status == "completed")
                .order_by(ExperimentDB.created_at.desc())
                .limit(10)
            )
            return result.scalars().all()
        
        # Run benchmark
        start = time.time()
        results = await query_with_index()
        elapsed = time.time() - start
        
        assert len(results) == 10
        assert all(exp.status == "completed" for exp in results)
        
        # Benchmark should complete in reasonable time (< 100ms for 100 records)
        assert elapsed < 0.1, f"Query took {elapsed:.3f}s, expected < 0.1s"
        
        # Cleanup
        for exp in experiments:
            await session.delete(exp)
        await session.commit()


@pytest.mark.benchmark
@pytest.mark.asyncio(loop_scope="function")
async def test_attack_iterations_experiment_timestamp_index():
    """
    Benchmark query using attack_iterations(experiment_id, timestamp) composite index.
    
    Tests filtering by experiment_id and sorting by timestamp.
    """
    async with AsyncSessionLocal() as session:
        # Create test experiment
        exp = ExperimentDB(
            name="Index Test Experiment",
            target_model_provider="ollama",
            target_model_name="qwen2.5:3b",
            attacker_model_provider="ollama",
            attacker_model_name="qwen2.5:3b",
            judge_model_provider="ollama",
            judge_model_name="qwen2.5:7b",
            initial_prompts=["test"],
            strategies=["roleplay_injection"],
        )
        session.add(exp)
        await session.flush()
        
        # Create test iterations
        iterations = []
        for i in range(50):
            iteration = AttackIterationDB(
                experiment_id=exp.experiment_id,
                iteration_number=i,
                strategy_used="roleplay_injection",
                original_prompt="test",
                mutated_prompt="test",
                target_response="test",
                judge_score=7.0,
                judge_reasoning="test",
                success=True,
                latency_ms=100,
                timestamp=datetime.utcnow() - timedelta(minutes=i),
            )
            iterations.append(iteration)
        
        session.add_all(iterations)
        await session.commit()
        
        # Benchmark query using index
        async def query_with_index():
            result = await session.execute(
                select(AttackIterationDB)
                .where(AttackIterationDB.experiment_id == exp.experiment_id)
                .order_by(AttackIterationDB.timestamp.desc())
                .limit(10)
            )
            return result.scalars().all()
        
        # Run benchmark
        start = time.time()
        results = await query_with_index()
        elapsed = time.time() - start
        
        assert len(results) == 10
        assert all(it.experiment_id == exp.experiment_id for it in results)
        
        # Benchmark should complete in reasonable time (< 50ms for 50 records)
        assert elapsed < 0.05, f"Query took {elapsed:.3f}s, expected < 0.05s"
        
        # Cleanup
        for it in iterations:
            await session.delete(it)
        await session.delete(exp)
        await session.commit()

