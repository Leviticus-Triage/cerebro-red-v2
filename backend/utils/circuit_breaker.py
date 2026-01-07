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

from utils.verbose_logging import verbose_logger


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"  # Circuit is open, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class ErrorType(Enum):
    """Error classification for circuit breaker logic."""
    TRANSIENT = "transient"  # Retry-able errors (RateLimit, Timeout, Network)
    PERMANENT = "permanent"  # Non-retry-able errors (Auth, InvalidRequest)
    UNKNOWN = "unknown"  # Unclassified errors (treat as transient for safety)


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
    transient_failures: int = 0
    permanent_failures: int = 0
    error_type_distribution: Dict[str, int] = field(default_factory=dict)
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
        failure_threshold: int = 10,
        timeout: float = 60.0,
        success_threshold: int = 3,
        half_open_max_calls: int = 5,
        log_transitions: bool = True
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening (default: 10)
            timeout: Seconds to wait before attempting half-open (default: 60)
            success_threshold: Successes needed in half-open to close circuit (default: 3)
            half_open_max_calls: Maximum requests allowed in HALF_OPEN state (default: 5)
            log_transitions: Enable state transition logging (default: True)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.half_open_max_calls = half_open_max_calls
        self.log_transitions = log_transitions
        
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._half_open_successes = 0
        self._half_open_call_count = 0
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
                old_state = self._state
                self._state = CircuitState.HALF_OPEN
                self._half_open_successes = 0
                self._half_open_call_count = 0
                
                # Log transition
                elapsed = time.time() - self._last_failure_time if self._last_failure_time else 0
                self._log_state_transition(
                    old_state,
                    CircuitState.HALF_OPEN,
                    f"Timeout elapsed ({elapsed:.1f}s)"
                )
    
    def _log_state_transition(self, from_state: CircuitState, to_state: CircuitState, reason: str):
        """Log circuit breaker state transition."""
        if not self.log_transitions:
            return
        
        emoji_map = {
            CircuitState.CLOSED: "🟢",
            CircuitState.OPEN: "🔴",
            CircuitState.HALF_OPEN: "🟡"
        }
        
        verbose_logger.log(
            "WARNING" if to_state == CircuitState.OPEN else "INFO",
            f"{emoji_map[from_state]} → {emoji_map[to_state]} Circuit Breaker: {from_state.value.upper()} → {to_state.value.upper()} ({reason})",
            component="CIRCUIT_BREAKER",
            extra_data={
                "from_state": from_state.value,
                "to_state": to_state.value,
                "reason": reason,
                "failures": self._failures,
                "successes": self._stats.successes,
                "threshold": self.failure_threshold
            }
        )
    
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
                    old_state = self._state
                    self._state = CircuitState.CLOSED
                    self._failures = 0
                    self._half_open_successes = 0
                    self._half_open_call_count = 0
                    
                    # Log transition
                    self._log_state_transition(
                        old_state,
                        CircuitState.CLOSED,
                        f"Success threshold reached ({self._half_open_successes}/{self.success_threshold})"
                    )
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failures = 0
    
    def record_failure(self, error_type: ErrorType = ErrorType.UNKNOWN):
        """
        Record a failed request.
        
        Args:
            error_type: Classification of the error (transient, permanent, unknown)
                       Only transient errors count toward circuit opening.
        """
        with self._lock:
            self._stats.total_requests += 1
            self._stats.total_failures += 1
            self._last_failure_time = time.time()
            
            # Track error type distribution
            error_type_str = error_type.value
            self._stats.error_type_distribution[error_type_str] = \
                self._stats.error_type_distribution.get(error_type_str, 0) + 1
            
            # Track by error type
            if error_type == ErrorType.TRANSIENT:
                self._stats.transient_failures += 1
            elif error_type == ErrorType.PERMANENT:
                self._stats.permanent_failures += 1
            
            # Only transient errors count toward opening the circuit
            if error_type == ErrorType.TRANSIENT or error_type == ErrorType.UNKNOWN:
                self._failures += 1
                
                if self._state == CircuitState.HALF_OPEN:
                    # Any transient failure in half-open immediately opens circuit
                    old_state = self._state
                    self._state = CircuitState.OPEN
                    self._half_open_successes = 0
                    self._half_open_call_count = 0
                    self._stats.opened_at = time.time()
                    
                    # Log transition
                    self._log_state_transition(
                        old_state,
                        CircuitState.OPEN,
                        "Failure in half-open state"
                    )
                elif self._state == CircuitState.CLOSED:
                    if self._failures >= self.failure_threshold:
                        # Open circuit after failure threshold
                        old_state = self._state
                        self._state = CircuitState.OPEN
                        self._stats.opened_at = time.time()
                        
                        # Log transition
                        self._log_state_transition(
                            old_state,
                            CircuitState.OPEN,
                            f"Failure threshold reached ({self._failures}/{self.failure_threshold})"
                        )
    
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
            
        Note:
            Caller is responsible for calling record_success() or record_failure()
            to avoid double-counting failures.
        """
        # Check if we should transition to half-open
        if self._state == CircuitState.OPEN:
            self._transition_to_half_open()
        
        # Reject if still open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        # Execute function (caller handles success/failure recording)
        result = func(*args, **kwargs)
        self.record_success()
        return result
    
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
            CircuitBreakerOpenError: If circuit is open or half-open call limit reached
            
        Note:
            Caller is responsible for calling record_success() or record_failure()
            to avoid double-counting failures.
        """
        # Check if we should transition to half-open
        if self._state == CircuitState.OPEN:
            self._transition_to_half_open()
        
        # Reject if still open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        # Check half-open call limit
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_call_count >= self.half_open_max_calls:
                    raise CircuitBreakerOpenError("Half-open call limit reached")
                self._half_open_call_count += 1
        
        # Execute async function (caller handles success/failure recording)
        result = await func(*args, **kwargs)
        self.record_success()
        return result
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failures = 0
            self._half_open_successes = 0
            self._half_open_call_count = 0
            self._last_failure_time = None
            self._stats.opened_at = None


def classify_error(exception: Exception) -> ErrorType:
    """
    Classify exception as transient or permanent for circuit breaker logic.
    
    Args:
        exception: The exception to classify
        
    Returns:
        ErrorType indicating if error is transient (retry-able) or permanent
        
    Examples:
        - Transient: RateLimitError, Timeout, ServiceUnavailable, Network errors
        - Permanent: AuthenticationError, InvalidRequestError, ValueError
        - Unknown: Treated as transient for safety
    """
    import litellm
    
    # Transient errors (retry makes sense)
    if isinstance(exception, (
        litellm.RateLimitError,
        litellm.Timeout,
        litellm.ServiceUnavailableError,
        ConnectionError,
        TimeoutError
    )):
        return ErrorType.TRANSIENT
    
    # Permanent errors (retry is pointless)
    if isinstance(exception, (
        litellm.AuthenticationError,
        litellm.InvalidRequestError,
        ValueError,
        TypeError
    )):
        return ErrorType.PERMANENT
    
    # Unknown → Treat as transient (safer default)
    return ErrorType.UNKNOWN


def calculate_backoff_with_jitter(
    base_delay: float,
    attempt: int,
    multiplier: float = 2.0,
    max_delay: float = 60.0,
    jitter_enabled: bool = True,
    max_jitter_ms: int = 1000
) -> float:
    """
    Calculate exponential backoff with optional jitter to prevent thundering herd.
    
    Args:
        base_delay: Base delay in seconds
        attempt: Attempt number (0-based)
        multiplier: Exponential multiplier (default: 2.0)
        max_delay: Maximum delay in seconds
        jitter_enabled: Enable randomized jitter
        max_jitter_ms: Maximum jitter in milliseconds
        
    Returns:
        Delay in seconds with jitter applied
        
    Example:
        >>> calculate_backoff_with_jitter(1.0, 0)  # ~1.0s ± 0.2s
        >>> calculate_backoff_with_jitter(1.0, 3)  # ~8.0s ± 1.0s
    """
    import random
    
    # Exponential backoff
    delay = min(base_delay * (multiplier ** attempt), max_delay)
    
    # Add jitter (±20% random variation)
    if jitter_enabled:
        jitter_range = min(delay * 0.2, max_jitter_ms / 1000.0)
        jitter = random.uniform(-jitter_range, jitter_range)
        delay = max(0.1, delay + jitter)  # Minimum 100ms
    
    return delay


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global circuit breakers per provider
_circuit_breakers: Dict[str, CircuitBreaker] = {}
_breakers_lock = Lock()


def get_circuit_breaker(provider: str) -> CircuitBreaker:
    """
    Get or create circuit breaker for a provider with settings from config.
    
    Args:
        provider: LLM provider name (e.g., "ollama", "openai", "azure")
        
    Returns:
        CircuitBreaker instance for the provider
    """
    from utils.config import get_settings
    
    with _breakers_lock:
        if provider not in _circuit_breakers:
            settings = get_settings()
            cb_settings = settings.circuit_breaker
            
            _circuit_breakers[provider] = CircuitBreaker(
                failure_threshold=cb_settings.failure_threshold,
                timeout=cb_settings.timeout,
                success_threshold=cb_settings.success_threshold,
                half_open_max_calls=cb_settings.half_open_max_calls,
                log_transitions=cb_settings.log_state_transitions
            )
            
            # Log circuit breaker creation
            verbose_logger.log(
                "INFO",
                f"🔧 Circuit Breaker created for '{provider}' (threshold={cb_settings.failure_threshold}, timeout={cb_settings.timeout}s)",
                component="CIRCUIT_BREAKER"
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

