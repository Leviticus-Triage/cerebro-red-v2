"""
backend/api/rate_limit.py
==========================

Rate limiting middleware for CEREBRO-RED v2 API.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
from fastapi import Request, HTTPException
from utils.config import get_settings


class RateLimiter:
    """
    IP-based rate limiter with configurable requests per minute.
    
    Tracks requests per IP address and enforces limits using sliding window.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute per IP
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
    
    async def check_rate_limit(self, request: Request) -> None:
        """
        Check if request exceeds rate limit.
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now()
        
        # Clean old requests (older than 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.requests[client_ip].append(now)


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for rate limiting.
    
    Checks rate limit before processing request (except for excluded paths).
    """
    settings = get_settings()
    
    # Skip rate limiting if disabled
    if not settings.security.rate_limit_enabled:
        response = await call_next(request)
        return response
    
    # Exclude certain paths from rate limiting
    excluded_paths = ["/health", "/", "/docs", "/openapi.json", "/redoc", "/metrics"]
    if request.url.path in excluded_paths:
        response = await call_next(request)
        return response
    
    # Exclude monitoring/polling endpoints from rate limiting (they poll frequently)
    polling_paths = [
        "/api/scan/status",
        "/api/experiments/",
        "/api/vulnerabilities",
        "/api/results",
    ]
    if any(request.url.path.startswith(path) for path in polling_paths):
        response = await call_next(request)
        return response
    
    # Check rate limit
    await rate_limiter.check_rate_limit(request)
    
    # Process request
    response = await call_next(request)
    return response

