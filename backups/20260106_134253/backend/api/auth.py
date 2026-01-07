"""
backend/api/auth.py
===================

API Key authentication middleware for CEREBRO-RED v2.
"""

import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from utils.config import get_settings
from pathlib import Path
from dotenv import load_dotenv

# Load .env file explicitly to ensure API_KEY_ENABLED is available
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> bool:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        True if authentication succeeds
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    # Check environment variable directly first (most reliable)
    api_key_enabled_env = os.environ.get("API_KEY_ENABLED", "").lower()
    if api_key_enabled_env in ("false", "0", "no", "off"):
        return True
    
    # Fallback to settings
    settings = get_settings()
    if not settings.security.api_key_enabled:
        return True
    
    # API key missing
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # API key invalid
    if api_key != settings.security.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return True

