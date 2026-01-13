# Copyright 2024-2026 Cerebro-Red v2 Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
backend/main.py
===============

FastAPI application entrypoint for CEREBRO-RED v2.

This module initializes the FastAPI application, sets up database connections,
configures middleware (CORS, Rate Limiting), registers routers, and handles
startup/shutdown events.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import init_db, close_db, AsyncSessionLocal
from core.telemetry import get_audit_logger
from utils.config import get_settings
from utils.llm_client import get_llm_client
from api import (
    experiments_router,
    scans_router,
    results_router,
    vulnerabilities_router,
    telemetry_router,
    websocket_router,
    demo_router
)
from api import templates
from api.exceptions import (
    CerebroException,
    cerebro_exception_handler,
    generic_exception_handler
)
from api.rate_limit import rate_limit_middleware
from api.auth import verify_api_key
from fastapi import Depends
from utils.circuit_breaker import get_all_circuit_breakers, reset_circuit_breaker, get_circuit_breaker
from api.responses import api_response


# ============================================================================
# Logging Configuration (MUST be before any logger usage)
# ============================================================================

def configure_logging():
    """
    Configure application-wide logging with DEBUG level and forced flush.
    
    Features:
    - Always uses DEBUG level (not dependent on settings)
    - Forces immediate flush to stdout (critical for Docker logs)
    - Structured format with timestamps, module names, levels
    - All loggers inherit this configuration
    """
    import logging
    import sys
    
    # Force DEBUG level as requested
    log_level = logging.DEBUG
    
    # Create formatter with detailed information
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Force flush after each log (critical for Docker)
    class FlushingStreamHandler(logging.StreamHandler):
        def emit(self, record):
            super().emit(record)
            self.flush()
    
    flushing_handler = FlushingStreamHandler(sys.stdout)
    flushing_handler.setLevel(log_level)
    flushing_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[flushing_handler],
        force=True  # Override any existing configuration
    )
    
    # Set level for all existing loggers
    logging.getLogger().setLevel(log_level)
    
    # Explicitly set level for key modules
    for module in ['uvicorn', 'fastapi', 'sqlalchemy', 'core', 'api', 'utils']:
        logging.getLogger(module).setLevel(log_level)
    
    # Log configuration summary
    logger = logging.getLogger(__name__)
    logger.info(f" Logging configured: Level=DEBUG, Flush=Forced, Format=Structured")
    logger.debug(f"[DEBUG-TEST] This is a DEBUG log - if you see this, DEBUG logging works!")
    
    return logger

# Initialize logging BEFORE creating FastAPI app
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Initialize database on startup
    - Close database connections on shutdown
    - Run payload coverage audit on startup
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Startup
    logger.info(" CEREBRO-RED v2 starting up...")
    
    # Load and log settings
    settings = get_settings()
    logger.info(f" CEREBRO-RED v2 Starting...")
    logger.info(f"   Environment: {settings.app.env}")
    logger.info(f"   Demo Mode: {'ENABLED (read-only)' if settings.app.demo_mode else 'DISABLED'}")
    logger.info(f"   Port: {settings.app.port}")
    logger.info(f"   Verbosity Level: {settings.app.verbosity}")
    logger.info(f"   Code Flow Enabled: {settings.app.verbosity >= 3}")
    
    # Initialize database
    await init_db()
    logger.info(" Database initialized")
    
    # Event loop diagnostics
    loop = asyncio.get_event_loop()
    logger.info(f"[STARTUP] Event loop: {loop}")
    logger.info(f"[STARTUP] Event loop running: {loop.is_running()}")
    logger.info(f"[STARTUP] Event loop closed: {loop.is_closed()}")
    logger.info(f"[STARTUP] Event loop type: {type(loop).__name__}")
    
    # === PHASE 3: PAYLOAD COVERAGE AUDIT ===
    logger.info(" Running payload coverage audit...")
    from core.payloads import get_payload_manager
    
    payload_manager = get_payload_manager()
    audit_result = payload_manager.audit_payload_coverage()
    
    # Log summary to console
    logger.info(f" Payload Coverage Audit Results:")
    logger.info(f"   Total Strategies: {audit_result['total_strategies']}")
    logger.info(f"   Covered: {audit_result['covered_strategies']} ({audit_result['coverage_percent']:.1f}%)")
    logger.info(f"   Well-Covered (>=3 templates): {audit_result['well_covered_strategies']} ({audit_result['well_covered_percent']:.1f}%)")
    logger.info(f"   {audit_result['recommendation']}")
    
    if audit_result['missing_strategies']:
        logger.warning(f" Missing templates for {len(audit_result['missing_strategies'])} strategies:")
        for strategy in audit_result['missing_strategies'][:5]:  # Show first 5
            logger.warning(f"   - {strategy}")
        if len(audit_result['missing_strategies']) > 5:
            logger.warning(f"   ... and {len(audit_result['missing_strategies']) - 5} more")
    
    if audit_result['under_covered_strategies']:
        logger.warning(f" Under-covered (<3 templates) for {len(audit_result['under_covered_strategies'])} strategies:")
        for strategy in audit_result['under_covered_strategies'][:5]:
            logger.warning(f"   - {strategy}")
    
    # Log full audit to telemetry for analysis
    audit_logger = get_audit_logger()
    audit_logger.log_event(
        event_type="payload_coverage_audit",
        metadata=audit_result
    )
    
    # Fail startup if coverage is critically low (<50%)
    if audit_result['coverage_percent'] < 50:
        logger.error(" CRITICAL: Payload coverage below 50% - Cannot start")
        raise RuntimeError(f"Insufficient payload coverage: {audit_result['coverage_percent']:.1f}%")
    
    logger.info(" Payload coverage audit complete")
    
    # === TEMPLATE UPDATER: Schedule automatic updates ===
    from core.template_updater import get_template_updater
    
    settings = get_settings()
    update_task = None
    
    # Schedule automatic template updates (daily at 2 AM UTC)
    async def scheduled_template_update():
        """Background task for automatic template updates."""
        import logging
        from datetime import datetime, timedelta
        update_logger = logging.getLogger(__name__)
        
        # Calculate seconds until next 2 AM UTC
        def seconds_until_2am():
            now = datetime.utcnow()
            target = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            return (target - now).total_seconds()
        
        # Wait until first 2 AM
        initial_wait = seconds_until_2am()
        update_logger.info(f"⏰ Next template update scheduled in {initial_wait/3600:.1f} hours (at 2 AM UTC)")
        await asyncio.sleep(initial_wait)
        
        while True:
            try:
                update_logger.info(" Starting scheduled template update...")
                updater = get_template_updater()
                result = await updater.update_all_repositories(create_backup=True)
                
                if result.get("success"):
                    update_logger.info(
                        f" Scheduled update complete: "
                        f"{result['total_templates_added']} templates added, "
                        f"{result['total_templates_updated']} templates updated"
                    )
                else:
                    failed_repos = [r["repo_name"] for r in result.get("repositories", []) if not r.get("success")]
                    update_logger.warning(f" Scheduled template update had failures: {', '.join(failed_repos)}")
                
                # Wait until next 2 AM UTC (24 hours)
                await asyncio.sleep(24 * 3600)
                    
            except asyncio.CancelledError:
                update_logger.info(" Scheduled template update task cancelled")
                break
            except Exception as e:
                update_logger.error(f" Error in scheduled template update: {e}")
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)
    
    # Start background task for scheduled updates (if enabled)
    if settings.template_update.auto_update:
        logger.info(" Automatic template updates enabled (daily at 2 AM UTC)")
        update_task = asyncio.create_task(scheduled_template_update())
    else:
        logger.info("Automatic template updates disabled (set TEMPLATE_UPDATE_AUTO_UPDATE=true to enable)")
    
    yield
    
    # Shutdown
    logger.info(" CEREBRO-RED v2 shutting down...")
    
    # Cancel update task if running
    if update_task:
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass
    
    await close_db()


app = FastAPI(
    title="CEREBRO-RED v2 API",
    description="""
    # Autonomous Local LLM Red Teaming Suite - Research Edition
    
    ## Overview
    CEREBRO-RED v2 implements the PAIR (Prompt Automatic Iterative Refinement) algorithm
    for automated vulnerability discovery in Large Language Models.
    
    ## Features
    - **Multi-Provider LLM Support**: Ollama, Azure OpenAI, OpenAI
    - **8 Attack Strategies**: Obfuscation, Context Flooding, Roleplay Injection, etc.
    - **LLM-as-a-Judge**: Semantic evaluation with 7 criteria
    - **Real-Time Progress**: WebSocket streaming for live updates
    - **Research-Grade Telemetry**: JSONL audit logs for analysis
    
    ## Authentication
    All endpoints (except `/health`, `/docs`, `/metrics`) require API key authentication via `X-API-Key` header.
    
    ## Rate Limiting
    Default: 60 requests per minute per IP address.
    
    ## References
    - PAIR Paper: https://arxiv.org/abs/2310.08419
    - GitHub: https://github.com/your-org/cerebro-red-v2
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "experiments", "description": "Experiment CRUD operations"},
        {"name": "scans", "description": "Scan execution and control"},
        {"name": "results", "description": "Experiment results and exports"},
        {"name": "vulnerabilities", "description": "Vulnerability findings"},
        {"name": "telemetry", "description": "Telemetry and metrics"},
        {"name": "websocket", "description": "Real-time progress streaming"},
    ]
)


# ============================================================================
# Middleware Configuration
# ============================================================================

# CORS Middleware - Load settings and configure CORS
def configure_cors():
    """Configure CORS middleware with settings."""
    settings = get_settings()
    origins_str = settings.security.cors_origins or "http://localhost:3000,http://localhost:5173"
    origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    # Handle wildcard '*' for unrestricted access (demo mode)
    if '*' in origins:
        # FastAPI CORSMiddleware requires ['*'] as list, not string
        return ['*'], settings.security.cors_allow_credentials
    
    # Always include common development origins (only if not using wildcard)
    default_origins = [
        "http://localhost:3000",   # Production frontend
        "http://localhost:5173",   # Vite dev server
        "http://localhost:8000",   # Legacy port
        "http://localhost:9000",   # Current backend port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:9000",
    ]
    for origin in default_origins:
        if origin not in origins:
            origins.append(origin)
    
    return origins, settings.security.cors_allow_credentials

cors_origins, cors_credentials = configure_cors()

# Log CORS configuration for debugging
import logging
logger = logging.getLogger(__name__)
logger.info(f"CORS configured with origins: {cors_origins}")
logger.info(f"CORS credentials: {cors_credentials}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.options("/{path:path}")
async def options_handler(path: str):
    """
    Explicit OPTIONS handler for CORS preflight debugging.
    This is handled by CORSMiddleware, but we log it for visibility.
    
    Note: Response is automatically wrapped in {data: ...} by middleware.
    """
    logger.debug(f"OPTIONS request for path: {path}")
    return {"message": "OK"}

# Rate Limiting Middleware
app.middleware("http")(rate_limit_middleware)

# JSON Response Wrapper Middleware
@app.middleware("http")
async def json_response_wrapper_middleware(request: Request, call_next):
    """
    Middleware to automatically wrap JSON responses in {data: ...} format.
    
    Ensures all JSON responses conform to ApiResponse<T> structure while:
    - Preserving status codes and headers
    - Avoiding double-wrapping already wrapped responses
    - Skipping non-JSON responses (e.g., /metrics text/plain)
    """
    response = await call_next(request)
    
    # Only process JSON responses
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type:
        return response
    
    # Skip error responses (they have their own format)
    if response.status_code >= 400:
        return response
    
    # Process JSONResponse
    if isinstance(response, JSONResponse):
        try:
            # Get the response body
            body = response.body
            if not body:
                return response
            
            # Decode and parse JSON
            body_str = body.decode("utf-8") if isinstance(body, bytes) else body
            parsed = json.loads(body_str)
            
            # Skip if already wrapped in {data: ...}
            if isinstance(parsed, dict) and "data" in parsed and len(parsed) == 1:
                return response
            
            # Wrap unwrapped JSON responses
            return JSONResponse(
                content={"data": parsed},
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except (json.JSONDecodeError, AttributeError, TypeError):
            # If parsing fails, return original response
            return response
    
    # For Response objects with JSON body
    if hasattr(response, "body") and response.body:
        try:
            body_str = response.body.decode("utf-8") if isinstance(response.body, bytes) else str(response.body)
            parsed = json.loads(body_str)
            
            # Skip if already wrapped
            if isinstance(parsed, dict) and "data" in parsed and len(parsed) == 1:
                return response
            
            # Wrap unwrapped responses
            return JSONResponse(
                content={"data": parsed},
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except (json.JSONDecodeError, AttributeError, TypeError):
            return response
    
    return response


# ============================================================================
# Exception Handlers
# ============================================================================

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for HTTPException (including rate limit 429 errors).
    
    Ensures CORS headers are included even for error responses.
    """
    origin = request.headers.get("origin")
    
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": exc.status_code,
            "path": str(request.url.path)
        },
        headers=exc.headers or {}
    )
    
    # Add CORS headers if origin is present
    if origin:
        from utils.config import get_settings
        settings = get_settings()
        origins_str = settings.security.cors_origins or "http://localhost:3000,http://localhost:5173"
        allowed_origins = [o.strip() for o in origins_str.split(",") if o.strip()]
        # Add default origins
        default_origins = [
            "http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://localhost:9000",
            "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8000", "http://127.0.0.1:9000"
        ]
        allowed_origins.extend(default_origins)
        
        if origin in allowed_origins or "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(CerebroException, cerebro_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ============================================================================
# Router Registration
# ============================================================================

app.include_router(experiments_router, prefix="/api/v1/experiments", tags=["experiments"])
app.include_router(scans_router, prefix="/api/v1/scan", tags=["scans"])
app.include_router(results_router, prefix="/api/v1/results", tags=["results"])
app.include_router(vulnerabilities_router, prefix="/api/v1/vulnerabilities", tags=["vulnerabilities"])
app.include_router(telemetry_router, prefix="/api/v1/telemetry", tags=["telemetry"])
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["Templates"])

# Demo mode endpoints (conditionally enabled, no auth required)
settings = get_settings()
if settings.app.demo_mode:
    app.include_router(demo_router, prefix="/api/v1/demo", tags=["demo"])
    logger.info(" Demo mode enabled - mock data endpoints available at /api/v1/demo/experiments")

# Debug endpoints (always available for testing)
from api import debug
app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])
logger = logging.getLogger(__name__)
logger.info(" Debug endpoints enabled (/api/v1/debug/force-error, /api/v1/debug/test-logging)")


# ============================================================================
# Metrics Endpoint (at root level, no auth required)
# ============================================================================

@app.get("/metrics", response_class=Response)
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.
    
    Returns metrics in Prometheus text format.
    No authentication required for monitoring systems.
    """
    # Note: In production, you would use prometheus_client library
    # For now, return basic metrics structure
    
    metrics_lines = [
        "# HELP cerebro_experiments_total Total number of experiments",
        "# TYPE cerebro_experiments_total counter",
        "cerebro_experiments_total 0",
        "",
        "# HELP cerebro_experiments_success Successful experiments",
        "# TYPE cerebro_experiments_success counter",
        "cerebro_experiments_success 0",
        "",
        "# HELP cerebro_iterations_total Total iterations",
        "# TYPE cerebro_iterations_total counter",
        "cerebro_iterations_total 0",
        "",
        "# HELP cerebro_vulnerabilities_found Vulnerabilities found",
        "# TYPE cerebro_vulnerabilities_found counter",
        "cerebro_vulnerabilities_found{severity=\"critical\"} 0",
        "cerebro_vulnerabilities_found{severity=\"high\"} 0",
        "cerebro_vulnerabilities_found{severity=\"medium\"} 0",
        "cerebro_vulnerabilities_found{severity=\"low\"} 0",
        "",
        "# HELP cerebro_llm_latency_seconds LLM request latency",
        "# TYPE cerebro_llm_latency_seconds histogram",
        "cerebro_llm_latency_seconds_bucket{le=\"0.1\"} 0",
        "cerebro_llm_latency_seconds_bucket{le=\"0.5\"} 0",
        "cerebro_llm_latency_seconds_bucket{le=\"1.0\"} 0",
        "cerebro_llm_latency_seconds_bucket{le=\"+Inf\"} 0",
        "",
        "# HELP cerebro_active_experiments Currently running experiments",
        "# TYPE cerebro_active_experiments gauge",
        "cerebro_active_experiments 0",
    ]
    
    return Response(
        content="\n".join(metrics_lines),
        media_type="text/plain"
    )


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: API information (automatically wrapped by middleware)
    """
    return {
        "name": "CEREBRO-RED v2",
        "version": "2.0.0",
        "description": "Autonomous Local LLM Red Teaming Suite",
        "docs_url": "/docs",
        "health_url": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        - status: "healthy" | "degraded" | "unhealthy"
        - components: Status of each component (database, LLM providers, telemetry)
        - version: API version
        - timestamp: Current timestamp
        
    Note: Response is automatically wrapped in {data: ...} by middleware.
    """
    settings = get_settings()
    
    # Check database
    db_status = "healthy"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"
    
    # Check LLM providers
    llm_status = {}
    try:
        llm_client = get_llm_client()
        config = llm_client.settings.get_llm_config("target")
        provider = config.get("provider", "unknown")
        llm_status[provider] = "healthy"
    except Exception:
        llm_status["unknown"] = "unavailable"
    
    # Check telemetry
    telemetry_status = "healthy"
    try:
        audit_logger = get_audit_logger()
        if not audit_logger.log_path.exists():
            telemetry_status = "degraded"
    except Exception:
        telemetry_status = "unhealthy"
    
    # Determine overall status
    overall_status = "healthy"
    if db_status == "unhealthy" or telemetry_status == "unhealthy":
        overall_status = "unhealthy"
    elif any(status == "unavailable" for status in llm_status.values()):
        overall_status = "degraded"
    
    # Add CORS configuration to response
    cors_config = {
        "origins": cors_origins,
        "credentials": cors_credentials,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    }
    
    return {
        "status": overall_status,
        "service": "cerebro-red-v2",
        "version": "2.0.0",
        "demo_mode": settings.app.demo_mode,
        "components": {
            "database": db_status,
            "llm_providers": llm_status,
            "telemetry": telemetry_status,
            "cors": "configured"
        },
        "cors_config": cors_config if settings.app.debug else None,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Circuit Breaker Health Endpoints
# ============================================================================

@app.get("/health/circuit-breakers", dependencies=[Depends(verify_api_key)])
async def get_circuit_breaker_stats():
    """
    Get circuit breaker statistics for all providers.
    
    Returns:
        Dictionary with circuit breaker stats per provider including:
        - State (closed/open/half_open)
        - Failure/success counts
        - Error type distribution (transient/permanent)
        - Failure rate
        - Circuit breaker configuration
    """
    breakers = get_all_circuit_breakers()
    stats = {}
    
    for provider, breaker in breakers.items():
        breaker_stats = breaker.stats
        
        # Calculate failure rate
        failure_rate = 0.0
        if breaker_stats.total_requests > 0:
            failure_rate = breaker_stats.total_failures / breaker_stats.total_requests
        
        stats[provider] = {
            "state": breaker_stats.state.value,
            "failures": breaker_stats.failures,
            "successes": breaker_stats.successes,
            "total_requests": breaker_stats.total_requests,
            "total_failures": breaker_stats.total_failures,
            "transient_failures": breaker_stats.transient_failures,
            "permanent_failures": breaker_stats.permanent_failures,
            "error_type_distribution": breaker_stats.error_type_distribution,
            "failure_rate": round(failure_rate, 4),
            "last_failure_time": breaker_stats.last_failure_time,
            "last_success_time": breaker_stats.last_success_time,
            "opened_at": breaker_stats.opened_at,
            "config": {
                "failure_threshold": breaker.failure_threshold,
                "success_threshold": breaker.success_threshold,
                "timeout": breaker.timeout,
                "half_open_max_calls": breaker.half_open_max_calls,
            }
        }
    
    return api_response(stats)


@app.post("/health/circuit-breakers/{provider}/reset", dependencies=[Depends(verify_api_key)])
async def reset_circuit_breaker_endpoint(provider: str):
    """
    Reset circuit breaker for a specific provider.
    
    Args:
        provider: LLM provider name (e.g., "ollama", "openai", "azure")
        
    Returns:
        Success message
    """
    try:
        reset_circuit_breaker(provider)
        return api_response({"message": f"Circuit breaker reset for {provider}", "provider": provider})
    except KeyError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit breaker not found for provider: {provider}"
        )

