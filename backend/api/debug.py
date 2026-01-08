"""
backend/api/debug.py
====================

Debug endpoints for testing error handling and logging.
Only available in development mode (CEREBRO_DEBUG=true).
"""

import logging
import traceback
from fastapi import APIRouter, HTTPException, Depends
from api.auth import verify_api_key
from api.responses import api_response
from utils.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/force-error")
async def force_error(error_type: str = "generic"):
    """
    Force an error for testing traceback logging.
    
    Args:
        error_type: Type of error to raise (generic, value, key, type, zero_division)
        
    Available in all environments for testing purposes.
    """
    
    logger.info(f"[DEBUG-ENDPOINT] Forcing error type: {error_type}")
    
    try:
        if error_type == "value":
            raise ValueError("This is a forced ValueError for testing traceback logging")
        elif error_type == "key":
            raise KeyError("forced_key_error")
        elif error_type == "type":
            raise TypeError("This is a forced TypeError")
        elif error_type == "zero_division":
            _ = 1 / 0
        else:
            raise Exception("This is a forced generic Exception for testing")
    except Exception as e:
        logger.error(f"[DEBUG-ENDPOINT] Caught forced error: {type(e).__name__}")
        logger.error(f"[DEBUG-ENDPOINT] Error message: {str(e)}")
        logger.error(f"[DEBUG-ENDPOINT] Full traceback:\n{traceback.format_exc()}")
        
        # Re-raise to test exception handlers
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/test-logging")
async def test_logging():
    """
    Test all logging levels to verify configuration.
    
    Available in all environments for testing purposes.
    """
    settings = get_settings()
    
    logger.debug("[TEST] This is a DEBUG log")
    logger.info("[TEST] This is an INFO log")
    logger.warning("[TEST] This is a WARNING log")
    logger.error("[TEST] This is an ERROR log")
    logger.critical("[TEST] This is a CRITICAL log")
    
    return api_response({
        "message": "Logging test complete - check Docker logs",
        "log_level": settings.app.log_level,
        "verbosity": settings.app.verbosity,
        "expected_logs": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    })
