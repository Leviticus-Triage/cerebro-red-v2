# CEREBRO-RED v2 - Code Documentation

## Overview

This document provides comprehensive code-level documentation for the CEREBRO-RED v2 project, including architecture, API structure, component descriptions, and development guidelines.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend Structure](#backend-structure)
3. [Frontend Structure](#frontend-structure)
4. [Core Components](#core-components)
5. [API Documentation](#api-documentation)
6. [Database Schema](#database-schema)
7. [Development Guidelines](#development-guidelines)

## Architecture Overview

CEREBRO-RED v2 follows a three-tier architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Dashboard UI                                          │
│  - Real-time Monitoring                                 │
│  - Experiment Management                                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI)                          │
│  - REST API                                             │
│  - WebSocket Server                                     │
│  - Orchestration Engine                                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Core Services                               │
│  - Prompt Mutator                                       │
│  - Security Judge                                       │
│  - LLM Client (litellm)                                 │
│  - Database (SQLite)                                    │
└─────────────────────────────────────────────────────────┘
```

## Backend Structure

### Directory Layout

```
backend/
├── api/                  # REST API endpoints
│   ├── experiments.py    # Experiment CRUD
│   ├── scans.py          # Scan execution
│   ├── results.py        # Results retrieval
│   ├── vulnerabilities.py # Vulnerability management
│   └── templates.py      # Template management
├── core/                 # Core business logic
│   ├── orchestrator.py   # Experiment orchestration
│   ├── mutator.py        # Prompt mutation strategies
│   ├── judge.py          # Security evaluation
│   ├── models.py         # Data models
│   ├── database.py      # Database repositories
│   └── telemetry.py      # Audit logging
├── utils/                # Utilities
│   ├── llm_client.py     # LLM provider abstraction
│   └── config.py         # Configuration management
└── main.py               # FastAPI application entry
```

### Core Components

#### Orchestrator (`core/orchestrator.py`)

The `RedTeamOrchestrator` class manages the entire experiment lifecycle:

- **Responsibilities**:
  - Coordinates attacker, target, and judge LLMs
  - Manages iteration loops
  - Handles error recovery and retries
  - Broadcasts progress via WebSocket

- **Key Methods**:
  - `run_experiment()`: Main execution loop
  - `execute_iteration()`: Single iteration execution
  - `mutate_prompt()`: Delegates to mutator
  - `evaluate_response()`: Delegates to judge

#### Mutator (`core/mutator.py`)

The `PromptMutator` class implements 44 attack strategies:

- **Strategy Categories**:
  - Obfuscation (Base64, Leetspeak, ROT13, etc.)
  - Jailbreak (DAN, AIM, STAN, etc.)
  - Injection (Direct, Indirect, Payload Splitting)
  - Context Manipulation
  - Social Engineering
  - And more...

- **Key Methods**:
  - `mutate()`: Applies selected strategy
  - `_apply_strategy()`: Strategy-specific mutation logic

#### Judge (`core/judge.py`)

The `SecurityJudge` class evaluates LLM responses:

- **Evaluation Criteria** (7-point scale):
  1. Jailbreak Success
  2. Harmful Content
  3. Hallucination Risk
  4. Bias Detection
  5. Logical Consistency
  6. Sycophancy
  7. Policy Violation

- **Key Methods**:
  - `evaluate()`: Main evaluation method
  - `_parse_judge_response()`: Extracts scores from LLM response
  - `_regex_fallback()`: Fallback evaluation if LLM fails

## Frontend Structure

### Directory Layout

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── monitor/      # Monitoring components
│   │   ├── experiments/  # Experiment management
│   │   └── ui/           # Base UI components (shadcn)
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx
│   │   ├── ExperimentMonitor.tsx
│   │   └── VulnerabilityDetails.tsx
│   ├── hooks/            # React hooks
│   │   ├── useExperiments.ts
│   │   └── useVulnerabilities.ts
│   ├── lib/              # Utilities
│   │   ├── api/          # API client
│   │   └── websocket/    # WebSocket client
│   └── types/            # TypeScript types
└── public/               # Static assets
```

### Key Components

#### ExperimentMonitor (`pages/ExperimentMonitor.tsx`)

Real-time experiment monitoring page:

- **Features**:
  - WebSocket connection for live updates
  - Progress tracking
  - Iteration results display
  - Vulnerability detection
  - Task queue visualization

- **State Management**:
  - Uses React hooks for state
  - Polls API as fallback
  - Handles WebSocket reconnection

#### ProgressOverview (`components/monitor/ProgressOverview.tsx`)

Displays experiment progress and statistics:

- **Metrics Shown**:
  - Progress percentage (capped at 100%)
  - Current iteration / Total iterations
  - Elapsed time
  - Estimated remaining time
  - Vulnerabilities found
  - Successful iterations

- **Status Logic**:
  - "Completed" if vulnerabilities found or successful iterations > 0
  - "Failed" only if no successes and no vulnerabilities

## API Documentation

### Base URL

```
http://localhost:8000/api
```

### Authentication

All endpoints require API key authentication via header:

```
X-API-Key: your-api-key-here
```

### Key Endpoints

#### Experiments

- `GET /api/experiments` - List all experiments
- `POST /api/experiments` - Create new experiment
- `GET /api/experiments/{id}` - Get experiment details
- `GET /api/experiments/{id}/iterations` - Get iteration results
- `GET /api/experiments/{id}/statistics` - Get experiment statistics

#### Scans

- `POST /api/scan/start` - Start experiment execution
- `GET /api/scan/status/{id}` - Get scan status
- `POST /api/scan/{id}/pause` - Pause scan
- `POST /api/scan/{id}/resume` - Resume scan
- `POST /api/scan/{id}/cancel` - Cancel scan

#### Vulnerabilities

- `GET /api/vulnerabilities` - List vulnerabilities
- `GET /api/vulnerabilities/{id}` - Get vulnerability details
- `GET /api/vulnerabilities/by-experiment/{id}` - Get vulnerabilities for experiment

#### Templates

- `GET /api/templates` - List templates
- `POST /api/templates` - Create template
- `GET /api/templates/{id}` - Get template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template

### WebSocket API

#### Connection

```
ws://localhost:8000/ws/scan/{experiment_id}?verbosity=2
```

#### Message Types

- `connected`: Connection established
- `progress`: Progress update
- `iteration_start`: Iteration started
- `iteration_complete`: Iteration completed
- `vulnerability_found`: Vulnerability detected
- `experiment_complete`: Experiment finished
- `error`: Error occurred

## Database Schema

### Tables

#### experiments

- `experiment_id` (UUID, Primary Key)
- `name` (String)
- `status` (Enum: pending, running, completed, failed, paused)
- `target_model_provider` (String)
- `target_model_name` (String)
- `max_iterations` (Integer)
- `success_threshold` (Float)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### attack_iterations

- `iteration_id` (UUID, Primary Key)
- `experiment_id` (UUID, Foreign Key)
- `iteration_number` (Integer)
- `strategy_used` (String)
- `judge_score` (Float)
- `success` (Boolean)
- `timestamp` (DateTime)

#### vulnerabilities

- `vulnerability_id` (UUID, Primary Key)
- `experiment_id` (UUID, Foreign Key)
- `severity` (Enum: critical, high, medium, low)
- `title` (String)
- `description` (Text)
- `judge_score` (Float)
- `discovered_at` (DateTime)

## Development Guidelines

### Code Style

- **Backend**: Follow PEP 8, use type hints
- **Frontend**: Use TypeScript, follow React best practices
- **Naming**: Use descriptive names, avoid abbreviations

### Testing

- **Backend**: Use pytest for unit and integration tests
- **Frontend**: Use Vitest for component tests
- **E2E**: Use Playwright for end-to-end tests

### Error Handling

- **Backend**: Use FastAPI exception handlers
- **Frontend**: Use React Error Boundaries
- **Logging**: Use structured logging with context

### Performance

- **Backend**: Use async/await for I/O operations
- **Frontend**: Use React.memo for expensive components
- **Database**: Use indexes for frequently queried fields

## Recent Fixes

### Experiment Status Display

- **Issue**: Progress showed >100%, iterations exceeded total, status incorrect
- **Fix**: Added capping logic for progress (max 100%) and iterations (max total)
- **Location**: `frontend/src/pages/ExperimentMonitor.tsx`, `frontend/src/components/monitor/ProgressOverview.tsx`

### Vulnerabilities Counting

- **Issue**: Vulnerabilities count was 0 even when vulnerabilities were found
- **Fix**: Fetch vulnerabilities from API in addition to WebSocket updates
- **Location**: `frontend/src/pages/ExperimentMonitor.tsx`

### Status Logic

- **Issue**: Status showed "Failed" even when vulnerabilities were found
- **Fix**: Status is "Completed" if vulnerabilities > 0 or successful iterations > 0
- **Location**: `frontend/src/pages/ExperimentMonitor.tsx`, `frontend/src/components/monitor/ProgressOverview.tsx`

### Emoji Removal

- **Issue**: Emojis made the interface unprofessional
- **Fix**: Removed all emojis from frontend components, replaced with text labels
- **Location**: All frontend component files

## Contributing

When contributing code:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Submit pull request with clear description

## License

MIT License - See LICENSE file for details
