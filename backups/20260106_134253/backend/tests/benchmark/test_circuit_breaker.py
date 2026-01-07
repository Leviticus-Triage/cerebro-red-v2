"""
Benchmark tests for circuit breaker.

Tests circuit breaker state transitions, overhead, and behavior
under failure conditions.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch

from utils.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
    get_circuit_breaker,
    reset_circuit_breaker,
)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_circuit_breaker_overhead():
    """
    Benchmark circuit breaker overhead on successful calls.
    
    Measures the performance impact of circuit breaker on normal operations.
    """
    breaker = CircuitBreaker(failure_threshold=5, timeout=60.0, success_threshold=2)
    
    async def successful_call():
        return "success"
    
    # Benchmark with circuit breaker
    start = time.time()
    for _ in range(100):
        result = await breaker.call_async(successful_call)
        assert result == "success"
    elapsed_with_breaker = time.time() - start
    
    # Benchmark without circuit breaker
    start = time.time()
    for _ in range(100):
        result = await successful_call()
        assert result == "success"
    elapsed_without_breaker = time.time() - start
    
    # Overhead should be reasonable (< 50% increase for circuit breaker with state management)
    # Note: Circuit breaker has state tracking overhead which is acceptable for resilience
    overhead_ratio = (elapsed_with_breaker - elapsed_without_breaker) / elapsed_without_breaker if elapsed_without_breaker > 0 else 0
    assert overhead_ratio < 0.5, f"Circuit breaker overhead {overhead_ratio:.2%} exceeds 50% (elapsed_with: {elapsed_with_breaker:.4f}s, elapsed_without: {elapsed_without_breaker:.4f}s)"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions():
    """
    Test circuit breaker state transitions under failure conditions.
    
    Verifies CLOSED -> OPEN -> HALF_OPEN -> CLOSED transitions.
    """
    breaker = CircuitBreaker(failure_threshold=3, timeout=1.0, success_threshold=2)
    
    # Initially CLOSED
    assert breaker.state == CircuitState.CLOSED
    
    async def failing_call():
        raise Exception("Simulated failure")
    
    # Fail 3 times to open circuit
    for i in range(3):
        try:
            await breaker.call_async(failing_call)
        except Exception:
            pass
    
    # Circuit should be OPEN
    assert breaker.state == CircuitState.OPEN
    
    # Attempting call should raise CircuitBreakerOpenError
    with pytest.raises(CircuitBreakerOpenError):
        await breaker.call_async(failing_call)
    
    # Wait for timeout
    await asyncio.sleep(1.1)
    
    # Circuit should transition to HALF_OPEN
    assert breaker.state == CircuitState.HALF_OPEN
    
    # Success in half-open
    async def successful_call():
        return "success"
    
    result = await breaker.call_async(successful_call)
    assert result == "success"
    
    # Second success should close circuit
    result = await breaker.call_async(successful_call)
    assert result == "success"
    assert breaker.state == CircuitState.CLOSED


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_circuit_breaker_retry_behavior():
    """
    Test circuit breaker behavior with retry logic.
    
    Verifies that circuit breaker prevents unnecessary retries when open.
    """
    breaker = CircuitBreaker(failure_threshold=2, timeout=60.0, success_threshold=1)
    
    call_count = 0
    
    async def failing_call():
        nonlocal call_count
        call_count += 1
        raise Exception("Simulated failure")
    
    # Fail twice to open circuit
    for _ in range(2):
        try:
            await breaker.call_async(failing_call)
        except Exception:
            pass
    
    assert breaker.state == CircuitState.OPEN
    assert call_count == 2
    
    # Attempt retry - should be rejected immediately
    with pytest.raises(CircuitBreakerOpenError):
        await breaker.call_async(failing_call)
    
    # Call count should not increase (circuit breaker rejected before call)
    assert call_count == 2


@pytest.mark.benchmark
def test_circuit_breaker_stats():
    """
    Test circuit breaker statistics tracking.
    
    Verifies that stats are correctly maintained.
    """
    breaker = CircuitBreaker()
    
    async def successful_call():
        return "success"
    
    async def failing_call():
        raise Exception("Failure")
    
    # Run some calls
    asyncio.run(breaker.call_async(successful_call))
    asyncio.run(breaker.call_async(successful_call))
    
    try:
        asyncio.run(breaker.call_async(failing_call))
    except Exception:
        pass
    
    stats = breaker.stats
    assert stats.total_requests == 3
    assert stats.total_failures == 1
    assert stats.successes == 2
    assert stats.state == CircuitState.CLOSED

