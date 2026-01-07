"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, AsyncSessionLocal


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    
    Uses in-memory SQLite for fast tests.
    """
    # Create in-memory database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Create and yield session
    async with async_session() as session:
        yield session
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for tests."""
    from unittest.mock import AsyncMock, MagicMock
    
    client = MagicMock()
    client.complete = AsyncMock(return_value=MagicMock(
        content="Mocked LLM response",
        model="mock-model",
        tokens_used=100,
        latency_ms=50
    ))
    
    return client


def _create_mock_benchmark_fixture():
    """
    Factory function to create mock benchmark fixture.
    
    This fixture is only registered when pytest-benchmark plugin is not loaded.
    """
    class MockBenchmark:
        """Mock benchmark object that does nothing."""
        def __call__(self, func, *args, **kwargs):
            """Execute function without benchmarking."""
            # Check if function is async and schedule it as a task
            if asyncio.iscoroutinefunction(func):
                return asyncio.create_task(func(*args, **kwargs))
            # For sync functions, call and return directly
            return func(*args, **kwargs)
        
        def pedantic(self, func, *args, **kwargs):
            """Mock pedantic mode - just execute the function."""
            return self(func, *args, **kwargs)
    
    return MockBenchmark()


def pytest_configure(config):
    """
    Pytest configuration hook to conditionally register mock benchmark fixture.
    
    Only registers the mock fixture if pytest-benchmark plugin is not loaded.
    This ensures the real plugin fixture is used when enabled.
    """
    # Only register mock fixture if benchmark plugin is not active
    if not config.pluginmanager.hasplugin('benchmark'):
        # Create and register the mock benchmark fixture
        @pytest.fixture(name='benchmark')
        def benchmark_fixture():
            """
            Mock benchmark fixture for when pytest-benchmark plugin is disabled.
            
            This fixture is used when running tests with `-p no:benchmark` (default).
            It provides a no-op implementation that allows benchmark tests to run
            without the actual benchmarking overhead.
            
            To run real benchmarks, use: pytest -m benchmark -p benchmark
            """
            return _create_mock_benchmark_fixture()
        
        # Add to the conftest module's namespace so pytest can discover it
        import sys
        module = sys.modules[__name__]
        setattr(module, 'benchmark', benchmark_fixture)

