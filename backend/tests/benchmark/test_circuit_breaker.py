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
    ErrorType,
    classify_error,
    calculate_backoff_with_jitter,
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
    
    # Benchmark with circuit breaker (use more iterations for accurate measurement)
    iterations = 1000
    start = time.time()
    for _ in range(iterations):
        result = await breaker.call_async(successful_call)
        assert result == "success"
    elapsed_with_breaker = time.time() - start
    
    # Benchmark without circuit breaker
    start = time.time()
    for _ in range(iterations):
        result = await successful_call()
        assert result == "success"
    elapsed_without_breaker = time.time() - start
    
    # Overhead should be reasonable (< 100% increase for circuit breaker with state management)
    # Note: Circuit breaker has state tracking overhead which is acceptable for resilience
    overhead_ratio = (elapsed_with_breaker - elapsed_without_breaker) / elapsed_without_breaker if elapsed_without_breaker > 0 else 0
    
    # Allow up to 100% overhead (2x slower) for circuit breaker with full state management
    assert overhead_ratio < 1.0, f"Circuit breaker overhead {overhead_ratio:.2%} exceeds 100% (elapsed_with: {elapsed_with_breaker:.4f}s, elapsed_without: {elapsed_without_breaker:.4f}s)"


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
            # Manually record failure (caller responsibility)
            breaker.record_failure(ErrorType.TRANSIENT)
    
    # Circuit should be OPEN
    assert breaker.state == CircuitState.OPEN
    
    # Attempting call should raise CircuitBreakerOpenError
    with pytest.raises(CircuitBreakerOpenError):
        await breaker.call_async(failing_call)
    
    # Wait for timeout
    await asyncio.sleep(1.1)
    
    # Access state property to trigger transition check
    current_state = breaker.state  # Triggers _transition_to_half_open()
    
    # Circuit should transition to HALF_OPEN
    assert current_state == CircuitState.HALF_OPEN
    
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
            # Manually record failure (caller responsibility)
            breaker.record_failure(ErrorType.TRANSIENT)
    
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
        # Manually record failure (caller responsibility)
        breaker.record_failure(ErrorType.TRANSIENT)
    
    stats = breaker.stats
    assert stats.total_requests == 3
    assert stats.total_failures == 1
    assert stats.successes == 2
    assert stats.state == CircuitState.CLOSED


@pytest.mark.benchmark
def test_error_classification():
    """Test error classification for transient vs permanent errors."""
    import litellm
    
    # Transient errors (use proper LiteLLM exception constructors)
    rate_limit_error = litellm.RateLimitError(
        message="Rate limit",
        llm_provider="ollama",
        model="test-model"
    )
    assert classify_error(rate_limit_error) == ErrorType.TRANSIENT
    
    timeout_error = litellm.Timeout(
        message="Timeout",
        model="test-model",
        llm_provider="ollama"
    )
    assert classify_error(timeout_error) == ErrorType.TRANSIENT
    
    assert classify_error(ConnectionError("Connection failed")) == ErrorType.TRANSIENT
    assert classify_error(TimeoutError("Timeout")) == ErrorType.TRANSIENT
    
    # Permanent errors
    auth_error = litellm.AuthenticationError(
        message="Auth failed",
        llm_provider="ollama",
        model="test-model"
    )
    assert classify_error(auth_error) == ErrorType.PERMANENT
    
    invalid_error = litellm.InvalidRequestError(
        message="Invalid",
        llm_provider="ollama",
        model="test-model"
    )
    assert classify_error(invalid_error) == ErrorType.PERMANENT
    
    assert classify_error(ValueError("Value error")) == ErrorType.PERMANENT
    assert classify_error(TypeError("Type error")) == ErrorType.PERMANENT
    
    # Unknown errors (treated as transient)
    assert classify_error(Exception("Unknown")) == ErrorType.UNKNOWN


@pytest.mark.benchmark
def test_jitter_backoff():
    """Test jitter backoff calculation produces varied delays."""
    delays = []
    
    # Run 10 times to verify jitter randomization
    for _ in range(10):
        delay = calculate_backoff_with_jitter(
            base_delay=1.0,
            attempt=2,  # 1.0 * 2^2 = 4.0s base
            multiplier=2.0,
            max_delay=60.0,
            jitter_enabled=True,
            max_jitter_ms=1000
        )
        delays.append(delay)
    
    # All delays should be around 4.0s ± 0.8s (20% of 4.0s)
    for delay in delays:
        assert 3.2 <= delay <= 4.8, f"Delay {delay} outside expected range"
    
    # Delays should vary (not all identical)
    unique_delays = len(set(delays))
    assert unique_delays > 5, f"Only {unique_delays} unique delays, jitter may not be working"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_circuit_breaker_with_error_types():
    """Test that only transient errors count toward circuit opening."""
    breaker = CircuitBreaker(failure_threshold=3, timeout=1.0, success_threshold=2, log_transitions=False)
    
    async def transient_error():
        import litellm
        raise litellm.RateLimitError(
            message="Rate limit",
            llm_provider="ollama",
            model="test-model"
        )
    
    async def permanent_error():
        import litellm
        raise litellm.AuthenticationError(
            message="Auth failed",
            llm_provider="ollama",
            model="test-model"
        )
    
    # 5 permanent errors should NOT open circuit
    for _ in range(5):
        try:
            await breaker.call_async(permanent_error)
        except Exception as e:
            # Manually record failure with error classification
            error_type = classify_error(e)
            breaker.record_failure(error_type)
    
    assert breaker.state == CircuitState.CLOSED, "Circuit should stay CLOSED for permanent errors"
    
    # 3 transient errors SHOULD open circuit
    for _ in range(3):
        try:
            await breaker.call_async(transient_error)
        except Exception as e:
            # Manually record failure with error classification
            error_type = classify_error(e)
            breaker.record_failure(error_type)
    
    assert breaker.state == CircuitState.OPEN, "Circuit should OPEN for transient errors"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_half_open_call_limit():
    """Test that half-open state respects max_calls limit."""
    breaker = CircuitBreaker(
        failure_threshold=2,
        timeout=0.5,
        success_threshold=3,
        half_open_max_calls=2,  # Only allow 2 calls in half-open
        log_transitions=False
    )
    
    async def failing_call():
        raise Exception("Fail")
    
    # Open circuit
    for _ in range(2):
        try:
            await breaker.call_async(failing_call)
        except Exception:
            # Manually record failure (caller responsibility)
            breaker.record_failure(ErrorType.TRANSIENT)
    
    assert breaker.state == CircuitState.OPEN
    
    # Wait for timeout
    await asyncio.sleep(0.6)
    
    # Trigger transition to half-open
    current_state = breaker.state
    assert current_state == CircuitState.HALF_OPEN
    
    async def successful_call():
        return "success"
    
    # First 2 calls should succeed
    await breaker.call_async(successful_call)
    await breaker.call_async(successful_call)
    
    # Third call should be rejected (exceeds half_open_max_calls)
    with pytest.raises(CircuitBreakerOpenError, match="Half-open call limit reached"):
        await breaker.call_async(successful_call)

