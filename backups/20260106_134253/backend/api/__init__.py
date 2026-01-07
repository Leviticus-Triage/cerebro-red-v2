"""
backend/api/__init__.py
=======================

API router exports for CEREBRO-RED v2 FastAPI application.
"""

from .experiments import router as experiments_router
from .scans import router as scans_router
from .results import router as results_router
from .vulnerabilities import router as vulnerabilities_router
from .telemetry import router as telemetry_router
from .websocket import router as websocket_router
from .debug import router as debug_router

__all__ = [
    "experiments_router",
    "scans_router",
    "results_router",
    "vulnerabilities_router",
    "telemetry_router",
    "websocket_router",
    "debug_router",
]

