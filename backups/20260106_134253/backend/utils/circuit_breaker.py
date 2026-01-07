"""
backend/utils/circuit_breaker.py
=================================

Circuit breaker pattern implementation for LLM provider resilience.

Implements a three-state circuit breaker (CLOSED, OPEN, HALF_OPEN) to prevent
cascading failures when LLM providers are unavailable or experiencing issues.
"""

import asyncio
import time
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, field
from threading import Lock


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"  # Circuit is open, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    total_requests: int = 0
    total_failures: int = 0
    opened_at: Optional[float] = None


class CircuitBreaker:
    """
    Circuit breaker for protecting LLM provider calls.
    
    Implements the circuit breaker pattern with three states:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Circuit is open, requests are immediately rejected
    - HALF_OPEN: Testing if service has recovered (allows limited requests)
    
    Attributes:
        failure_threshold: Number of failures before opening circuit (default: 5)
        timeout: Time in seconds before attempting half-open (default: 60)
        success_threshold: Number of successes in half-open to close circuit (default: 2)
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 2
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening
            timeout: Seconds to wait before attempting half-open
            success_threshold: Successes needed in half-open to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._half_open_successes = 0
        self._last_failure_time: Optional[float] = None
        self._lock = Lock()
        self._stats = CircuitBreakerStats()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit breaker state."""
        # Check if we should transition to half-open when state is accessed
        # This ensures state transitions happen even when state is checked directly
        if self._state == CircuitState.OPEN:
            self._transition_to_half_open()
        return self._state
    
    @property
    def stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        with self._lock:
            stats = CircuitBreakerStats(
                state=self._state,
                failures=self._failures,
                successes=self._stats.successes,
                last_failure_time=self._last_failure_time,
                last_success_time=self._stats.last_success_time,
                total_requests=self._stats.total_requests,
                total_failures=self._stats.total_failures,
                opened_at=self._stats.opened_at
            )
        return stats
    
    def _should_attempt_half_open(self) -> bool:
        """Check if circuit should transition to half-open."""
        if self._state != CircuitState.OPEN:
            return False
        
        if self._last_failure_time is None:
            return False
        
        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.timeout
    
    def _transition_to_half_open(self):
        """Transition circuit to half-open state."""
        with self._lock:
            if self._state == CircuitState.OPEN and self._should_attempt_half_open():
                self._state = CircuitState.HALF_OPEN
                self._half_open_successes = 0
    
    def record_success(self):
        """Record a successful request."""
        with self._lock:
            self._stats.total_requests += 1
            self._stats.successes += 1
            self._stats.last_success_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.success_threshold:
                    # Close circuit after success threshold
                    self._state = CircuitState.CLOSED
                    self._failures = 0
                    self._half_open_successes = 0
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failures = 0
    
    def record_failure(self):
        """Record a failed request."""
        with self._lock:
            self._stats.total_requests += 1
            self._stats.total_failures += 1
            self._failures += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens circuit
                self._state = CircuitState.OPEN
                self._half_open_successes = 0
                self._stats.opened_at = time.time()
            elif self._state == CircuitState.CLOSED:
                if self._failures >= self.failure_threshold:
                    # Open circuit after failure threshold
                    self._state = CircuitState.OPEN
                    self._stats.opened_at = time.time()
    
    def call(self, func, *args, **kwargs):
        """
        Execute a function call through the circuit breaker.
        
        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of function call
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        # Check if we should transition to half-open
        if self._state == CircuitState.OPEN:
            self._transition_to_half_open()
        
        # Reject if still open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise
    
    async def call_async(self, func, *args, **kwargs):
        """
        Execute an async function call through the circuit breaker.
        
        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of async function call
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        # Check if we should transition to half-open
        if self._state == CircuitState.OPEN:
            self._transition_to_half_open()
        
        # Reject if still open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        # Execute async function
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failures = 0
            self._half_open_successes = 0
            self._last_failure_time = None
            self._stats.opened_at = None


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global circuit breakers per provider
_circuit_breakers: Dict[str, CircuitBreaker] = {}
_breakers_lock = Lock()


def get_circuit_breaker(provider: str) -> CircuitBreaker:
    """
    Get or create circuit breaker for a provider.
    
    Args:
        provider: LLM provider name (e.g., "ollama", "openai", "azure")
        
    Returns:
        CircuitBreaker instance for the provider
    """
    with _breakers_lock:
        if provider not in _circuit_breakers:
            _circuit_breakers[provider] = CircuitBreaker(
                failure_threshold=5,
                timeout=60.0,
                success_threshold=2
            )
        return _circuit_breakers[provider]


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """Get all circuit breakers."""
    with _breakers_lock:
        return _circuit_breakers.copy()


def reset_circuit_breaker(provider: str):
    """Reset circuit breaker for a provider."""
    with _breakers_lock:
        if provider in _circuit_breakers:
            _circuit_breakers[provider].reset()

