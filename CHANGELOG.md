# Changelog

All notable changes to CEREBRO-RED v2 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-23

### Added

#### Core Features

- **PAIR Algorithm Orchestrator** (`backend/core/orchestrator.py`)
  - Full implementation of Prompt Automatic Iterative Refinement algorithm from [arxiv.org/abs/2310.08419](https://arxiv.org/abs/2310.08419)
  - Async batch processing with exponential backoff
  - Real-time progress tracking via WebSocket
  - Automatic vulnerability discovery and classification

- **8 Attack Strategies** (`backend/core/mutator.py`)
  - `OBFUSCATION_BASE64`: Base64 encoding-based filter bypass
  - `OBFUSCATION_LEETSPEAK`: Character substitution obfuscation
  - `OBFUSCATION_ROT13`: Caesar cipher rotation
  - `CONTEXT_FLOODING`: Attention mechanism exploitation
  - `ROLEPLAY_INJECTION`: System prompt override attacks
  - `REPHRASE_SEMANTIC`: LLM-powered iterative refinement (core PAIR algorithm)
  - `SYCOPHANCY`: Agreement-seeking manipulation attacks
  - `LINGUISTIC_EVASION`: Euphemism and academic language manipulation

- **7-Criteria Security Judge** (`backend/core/judge.py`)
  - LLM-as-a-Judge implementation with Chain-of-Thought reasoning
  - Multi-criteria evaluation:
    1. Jailbreak Success Score (0-10)
    2. Harmful Content Score (0-10)
    3. Hallucination Score (0-10)
    4. Bias Score (0-10)
    5. Logical Consistency Score (0-10)
    6. Sycophancy Score (0-10)
    7. Policy Violation Score (0-10)
  - Regex fallback patterns for reliability
  - PyRIT-compatible scoring methodology

- **FastAPI REST API** (`backend/api/`)
  - Complete CRUD operations for experiments
  - Scan execution and control endpoints
  - Real-time WebSocket progress streaming
  - Vulnerability discovery and statistics
  - Telemetry and metrics endpoints
  - OpenAPI/Swagger documentation

- **Research-Grade Telemetry** (`backend/core/telemetry.py`)
  - Thread-safe JSONL audit logger
  - Structured event logging for whitepaper-grade analysis
  - Mutation history tracking
  - Performance metrics collection

- **Multi-Provider LLM Support** (`backend/utils/llm_client.py`)
  - Ollama integration (local models)
  - Azure OpenAI support
  - OpenAI API support
  - Unified interface via litellm
  - Circuit breaker pattern for resilience

#### Frontend Features

- **React Dashboard** (`frontend/`)
  - Modern UI with TailwindCSS and ShadcnUI
  - Experiment creation and management
  - Real-time scan progress visualization
  - Vulnerability heatmaps and analytics
  - Export functionality (JSON, CSV, PDF)

#### Infrastructure

- **Docker & Docker Compose** (`docker/`)
  - Multi-stage builds for production
  - Non-root user execution
  - Health checks and auto-restart
  - Volume management for persistent data

- **Database Migrations** (`backend/alembic/`)
  - Initial schema (001_initial_schema)
  - Judge score fields (002_add_judge_score_fields)
  - Performance indexes (003_add_performance_indexes)

#### Testing & Quality

- **End-to-End Test Suites**
  - Backend E2E tests (`backend/tests/e2e/`)
    - Experiment lifecycle tests
    - Provider comparison tests
    - Ollama integration tests
    - Azure OpenAI integration tests
  - Frontend E2E tests (`frontend/tests/e2e/`)
    - Playwright-based browser tests
    - Experiment creation flow
    - Vulnerability display tests

- **Comprehensive Test Coverage**
  - Unit tests for core modules
  - Integration tests with mocked LLMs
  - API authentication and CORS tests
  - Database transaction tests
  - Benchmark tests for performance

#### Performance & Reliability

- **Circuit Breaker Pattern** (`backend/utils/circuit_breaker.py`)
  - CLOSED/OPEN/HALF_OPEN states
  - Provider-specific failure tracking
  - Automatic recovery mechanisms
  - Health endpoints for monitoring

- **Database Performance Indexes**
  - Composite index on `experiments(status, created_at)`
  - Composite index on `attack_iterations(experiment_id, timestamp)`
  - Optimized query performance for large datasets

- **Frontend Resilience**
  - Axios retry with exponential backoff
  - React Query caching and prefetching
  - Pagination with size limits
  - Toast notification system

### Changed

- **API Response Format**: All JSON responses now wrapped in `{data: ...}` structure
- **Type Safety**: Replaced `any` types with `unknown` and proper interfaces
- **Error Handling**: Enhanced error logging with request IDs and stack traces
- **CORS Configuration**: Improved CORS handling with explicit OPTIONS handler

### Security

- **API Key Authentication**: Configurable API key protection for all endpoints
- **Rate Limiting**: IP-based rate limiting (60 requests/minute default)
- **Input Validation**: Strict Pydantic validation on all endpoints
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM

### Documentation

- **TROUBLESHOOTING.md**: Comprehensive troubleshooting guide
- **README_TESTING.md**: Testing documentation and guidelines
- **OpenAPI Schema**: Auto-generated API documentation
- **TRAYCER_AUDIT_REPORT.md**: Complete audit and test report

### Technical Details

- **Backend**: FastAPI 0.115+, Python 3.11+, SQLAlchemy 2.0+ (async)
- **Frontend**: React 18.3+, TypeScript 5.7+, Vite 6.0+
- **Database**: SQLite (async via aiosqlite)
- **LLM Gateway**: litellm 1.55+
- **Container**: Docker 24.0+, Docker Compose 2.20+

---

## [Unreleased]

### Planned Features

- Additional mutation strategies
- Enhanced judge prompts
- Telemetry analysis tools
- Multi-experiment batch processing UI
- Advanced vulnerability correlation

---

**For detailed API documentation, see [docs/openapi.json](./docs/openapi.json)**

**For testing information, see [README_TESTING.md](./README_TESTING.md)**

**For troubleshooting, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**

