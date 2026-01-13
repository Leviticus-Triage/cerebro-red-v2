# CEREBRO-RED v2 (Research Edition)

**Autonomous Local LLM Red Teaming Suite**

A research-grade framework for automated vulnerability discovery in local LLMs using Agentic Fuzzing and Adaptive Adversarial Mutation (AAM).

##  Research Goals

- Implement **PAIR Algorithm** (Prompt Automatic Iterative Refinement) from [arxiv.org/abs/2310.08419](https://arxiv.org/abs/2310.08419)
- **LLM-as-a-Judge** semantic evaluation with Chain-of-Thought reasoning
- **Telemetry-First** architecture for whitepaper-grade analysis
- Multi-provider LLM support (Ollama, Azure OpenAI, OpenAI)

## ️ Architecture

### Tech Stack

- **Backend**: FastAPI (async/await), Pydantic (strict types), Uvicorn
- **LLM Gateway**: litellm (universal adapter for Ollama/Azure/OpenAI)
- **Database**: SQLite (experiments) + JSONL (audit logs)
- **Frontend**: React + Vite + TailwindCSS + ShadcnUI + Recharts
- **Container**: Docker + Docker Compose

### Core Modules

1. **Orchestrator** (`backend/core/engine.py`): Async batch processing with exponential backoff
2. **Mutator** (`backend/core/mutator.py`): PAIR algorithm with mutation strategies
3. **Judge** (`backend/core/judge.py`): LLM-as-a-Judge with CoT evaluation
4. **Telemetry** (`backend/core/telemetry.py`): Thread-safe JSONL audit logger

##  Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- Ollama running on host (or Azure/OpenAI API keys)

### Docker Setup

If Docker is not running, start the Docker daemon:

```bash
# Start Docker daemon
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Add your user to the docker group (to run Docker without sudo)
sudo usermod -aG docker $USER

# Apply group changes (logout/login or use newgrp)
newgrp docker
# OR logout and login again for changes to take effect
```

**Verify Docker is running**:
```bash
docker --version
docker compose version
```

### Installation

1. Clone repository:
   ```bash
   git clone https://github.com/Leviticus-Triage/cerebro-red-v2.git
   cd cerebro-red-v2
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your LLM provider credentials
   ```

3. **WICHTIG: Prüfe Port 8000**
   ```bash
   # Falls Port 8000 belegt ist:
   lsof -i :8000  # Finde Prozess
   # Oder ändere Port in .env: CEREBRO_PORT=8001
   ```

4. Start Backend (WICHTIG - muss laufen!):
   ```bash
   # Option 1: Automatisch (empfohlen)
   ./START_BACKEND.sh
   
   # Option 2: Docker
   docker compose up -d cerebro-backend
   
   # Option 3: Lokal
   cd backend
   uvicorn main:app --reload --port 9000
   ```

4. Prüfe Backend-Status:
   ```bash
   curl http://localhost:9000/health
   # Sollte {"status": "healthy", ...} zurückgeben
   ```

5. Quick Tests ausführen:
   ```bash
   ./QUICK_TEST_EXAMPLES.sh
   ```

6. Access dashboard:
   - Backend API: http://localhost:9000
   - Frontend UI: http://localhost:3000 (optional: `docker compose up -d cerebro-frontend`)
   - API Docs: http://localhost:9000/docs

---

##  Quickstart: Local vs Cloud Deployment

### Local Deployment (Ollama)

Best for: Privacy-focused testing, no API costs, offline operation.

```bash
# 1. Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b
ollama serve

# 2. Configure .env for local
cat > .env << 'EOF'
TARGET_MODEL=ollama/llama3.2:3b
ATTACKER_MODEL=ollama/llama3.2:3b
JUDGE_MODEL=ollama/llama3.2:3b
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Relaxed circuit breaker for local (slower responses)
CIRCUIT_BREAKER_FAILURE_THRESHOLD=15
CIRCUIT_BREAKER_TIMEOUT=120
CIRCUIT_BREAKER_JITTER_ENABLED=true
EOF

# 3. Start services
docker compose up -d

# 4. Verify
curl http://localhost:9000/health | jq
```

### Cloud Deployment (OpenAI)

Best for: Faster responses, higher quality mutations, production testing.

```bash
# 1. Configure .env for cloud
cat > .env << 'EOF'
TARGET_MODEL=openai/gpt-4o-mini
ATTACKER_MODEL=openai/gpt-4o-mini
JUDGE_MODEL=openai/gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here

# Standard circuit breaker for cloud
CIRCUIT_BREAKER_FAILURE_THRESHOLD=10
CIRCUIT_BREAKER_TIMEOUT=60
CIRCUIT_BREAKER_JITTER_ENABLED=true
EOF

# 2. Start services
docker compose up -d

# 3. Verify
curl http://localhost:9000/health | jq
```

### Hybrid Deployment (Multi-Provider)

Best for: Cost optimization (cheap target, quality attacker/judge).

```bash
# Configure .env for hybrid
cat > .env << 'EOF'
# Target on local Ollama (cheap, many requests)
TARGET_MODEL=ollama/llama3.2:3b
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Attacker and Judge on OpenAI (quality matters)
ATTACKER_MODEL=openai/gpt-4o-mini
JUDGE_MODEL=openai/gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here

# Balanced circuit breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=12
CIRCUIT_BREAKER_TIMEOUT=90
EOF
```

---

##  Verbosity Levels

Control the amount of detail in Live Logs and Code Flow tracking.

| Level | Name | Description | Use Case |
|-------|------|-------------|----------|
| 0 | Minimal | Only errors and vulnerabilities | Production monitoring |
| 1 | Standard | + Progress updates | Normal operation |
| 2 | Debug | + LLM requests/responses | Debugging issues |
| 3 | Debug + Code Flow | + Task queue, decision points | Full observability |

### Setting Verbosity

**Via UI**: Use the "Verbosity" dropdown in Experiment Monitor.

**Via API**:
```bash
# WebSocket connection with verbosity
ws://localhost:9000/ws/scan/{experiment_id}?verbosity=3
```

**Via Environment**:
```bash
CEREBRO_VERBOSITY=3
```

### Code Flow Events (verbosity >= 3)

When verbosity is set to 3, you'll see:
- **Task Start/End**: When each task begins and completes
- **Strategy Selection**: Which strategy was chosen and why
- **Decision Points**: Threshold checks, fallback decisions
- **Performance Metrics**: Latency, tokens, scores per step

---

##  Circuit Breaker Configuration

The circuit breaker prevents cascading failures when LLM providers are overloaded.

### Configuration Options

```bash
# .env settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=10   # Failures before circuit opens
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=3    # Successes to close circuit
CIRCUIT_BREAKER_TIMEOUT=60             # Seconds before half-open attempt
CIRCUIT_BREAKER_JITTER_ENABLED=true    # Randomize retry delays
CIRCUIT_BREAKER_MAX_JITTER_MS=1000     # Max jitter in milliseconds
```

### Recommended Settings by Provider

| Provider | Failure Threshold | Timeout | Jitter |
|----------|------------------|---------|--------|
| Ollama (local) | 15 | 120s | Enabled |
| OpenAI | 10 | 60s | Enabled |
| Azure OpenAI | 10 | 60s | Enabled |
| Groq | 8 | 45s | Enabled |

### Monitoring Circuit Breakers

```bash
# Check circuit breaker status
curl http://localhost:9000/health/circuit-breakers | jq

# Expected output
{
  "data": {
    "ollama": {
      "state": "closed",
      "failures": 2,
      "successes": 48,
      "failure_rate": 0.04,
      "threshold": 15
    }
  }
}
```

### Troubleshooting High Failure Rates

If circuit breaker opens frequently (> 20% failure rate):

1. **Increase threshold**: `CIRCUIT_BREAKER_FAILURE_THRESHOLD=20`
2. **Increase timeout**: `CIRCUIT_BREAKER_TIMEOUT=120`
3. **Check provider status**: Verify Ollama/OpenAI is responsive
4. **Reduce concurrency**: Lower `MAX_CONCURRENT_ATTACKS` in experiment config

---

### Quick Restart Checklist

Use this checklist when restarting services after code changes or troubleshooting:

#### Backend Restart

1. **Stop backend**:
   ```bash
   docker compose stop cerebro-backend
   ```

2. **Restart backend** (if no code changes):
   ```bash
   docker compose restart cerebro-backend
   ```

3. **Rebuild and restart** (if code/dependencies changed):
   ```bash
   docker compose build cerebro-backend --no-cache
   docker compose up -d cerebro-backend
   ```

4. **Wait for startup** (10-15 seconds):
   ```bash
   sleep 10
   ```

5. **Health check**:
   ```bash
   curl http://localhost:9000/health | python3 -m json.tool
   # Should return: {"status": "healthy", ...}
   ```

6. **Verify logs**:
   ```bash
   docker compose logs cerebro-backend --tail=30 | grep -E "started|Uvicorn running|Application startup|ERROR"
   ```

#### Frontend Restart

1. **Stop frontend**:
   ```bash
   docker compose stop cerebro-frontend
   ```

2. **Restart frontend**:
   ```bash
   docker compose restart cerebro-frontend
   ```

3. **Verify**:
   ```bash
   curl -I http://localhost:3000
   # Should return: HTTP/1.1 200 OK
   ```

#### Log Verification Commands

```bash
# Check for run_experiment execution
docker compose logs cerebro-backend --tail=200 | grep -E "run_experiment|DIAG|WRAPPER"

# Check for errors
docker compose logs cerebro-backend --tail=200 | grep -E "ERROR|Exception|Traceback|FAILED"

# Check for experiment start
docker compose logs cerebro-backend --tail=200 | grep -E "POST /api/scan/start|DIAG-START"

# Monitor live logs
docker compose logs -f cerebro-backend
```

## ️ Development Workflow

### Live Code Reload (Development Mode)

CEREBRO-RED v2 supports **live code mounting** for rapid development without Docker image rebuilds.

#### How It Works

The `docker-compose.yml` mounts `./backend:/app` as a volume, allowing code changes to be immediately reflected in the running container.

#### Making Code Changes

1. **Edit any Python file** in `backend/`:
   ```bash
   # Example: Edit orchestrator
   nano backend/core/orchestrator.py
   ```

2. **Restart the backend container** (no rebuild needed):
   ```bash
   docker compose restart cerebro-backend
   ```

3. **Verify changes** in logs:
   ```bash
   docker compose logs -f cerebro-backend | grep "your_debug_message"
   ```

#### When Rebuild IS Required

You **must rebuild** the Docker image when:

-  **Dependencies change**: Modified `requirements.txt` or `pyproject.toml`
-  **Dockerfile changes**: Modified `docker/Dockerfile.backend`
-  **System packages**: Added OS-level dependencies (apt-get)
-  **Entrypoint changes**: Modified `docker/entrypoint.sh`

**Rebuild command:**
```bash
docker compose build cerebro-backend --no-cache
docker compose up -d cerebro-backend
```

#### When Restart IS Sufficient

You **only need restart** when:

-  **Python code changes**: Any `.py` file in `backend/`
-  **Configuration changes**: `.env` file updates
-  **Data files**: `backend/data/payloads.json` updates
-  **Templates**: Jailbreak template modifications

**Restart command:**
```bash
docker compose restart cerebro-backend
```

#### Development Best Practices

1. **Clear Python cache** if seeing stale code:
   ```bash
   docker compose exec cerebro-backend find /app -name "*.pyc" -delete
   docker compose exec cerebro-backend find /app -name "__pycache__" -type d -exec rm -rf {} +
   docker compose restart cerebro-backend
   ```

2. **Watch logs in real-time**:
   ```bash
   docker compose logs -f cerebro-backend
   ```

3. **Test changes immediately**:
   ```bash
   # After code change + restart:
   curl http://localhost:9000/health
   ```

4. **Run tests inside container**:
   ```bash
   docker compose exec cerebro-backend pytest tests/ -v
   ```

#### Production Deployment

For production, **disable volume mounting** by commenting out the live mount:

```yaml
volumes:
  # - ./backend:/app  # Disable for production
  - cerebro-data:/app/data
  # ... other volumes
```

Then rebuild with production optimizations:
```bash
docker compose build --no-cache
docker compose up -d
```

### Troubleshooting Development Setup

#### Issue: Code changes not reflected

**Solutions:**
- Verify volume mount exists: `docker inspect cerebro-backend | grep Mounts`
- Clear Python cache (see above)
- Check file permissions: `ls -la backend/`
- Restart container: `docker compose restart cerebro-backend`

#### Issue: Permission denied errors

**Solutions:**
- Entrypoint runs as root and fixes permissions automatically
- If issues persist, check entrypoint logs: `docker compose logs cerebro-backend | head -20`
- Manually fix: `sudo chown -R $USER:$USER backend/`

#### Issue: Import errors after changes

**Solutions:**
- Verify `PYTHONPATH` includes `/app`: `docker compose exec cerebro-backend env | grep PYTHONPATH`
- Check for syntax errors: `docker compose exec cerebro-backend python -m py_compile /app/main.py`
- Restart with clean cache (see above)

##  Research Methodology

### PAIR Algorithm Implementation

CEREBRO-RED implements the three-LLM architecture:

1. **Attacker LLM**: Generates adversarial prompts
2. **Target LLM**: The model being tested
3. **Judge LLM**: Evaluates jailbreak success

### Mutation Strategies

- **Obfuscation**: Base64, Leetspeak, ROT13
- **Context Flooding**: Overwhelming context window
- **Roleplay Injection**: System prompt overrides
- **Rephrase**: LLM-powered semantic mutation

### Evaluation Criteria

Judge LLM scores (0-10 scale):
- Jailbreak success
- Harmful content generation
- Policy violation severity
- Confidence metrics

##  Project Structure

```
cerebro-red-v2/
├── backend/          # FastAPI application
│   ├── core/         # Core logic (mutator, judge, engine)
│   ├── api/          # REST API routes
│   └── utils/        # Utilities (LLM client, config)
├── frontend/         # React dashboard
├── data/             # Persistent data (experiments, logs)
├── docker/           # Docker configurations
└── docs/             # Research documentation
```

##  Project Status

<!-- AUTO-GENERATED: Do not edit this section manually -->
![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Build](https://img.shields.io/badge/Build-passing-green)
![Coverage](https://img.shields.io/badge/Coverage-N%2FA-lightgrey)

**Last Updated:** 2026-01-10T00:00:00Z

<!-- END AUTO-GENERATED -->

##  Project Status

<!-- AUTO-GENERATED: Do not edit this section manually -->
![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Build](https://img.shields.io/badge/Build-passing-green)
![Coverage](https://img.shields.io/badge/Coverage-85.3%-green)

**Last Updated:** 2026-01-10T12:34:56Z

<!-- END AUTO-GENERATED -->

##  Development Status

**Phase 1**:  Project Foundation & Infrastructure
- [x] Project structure
- [x] Requirements & dependencies
- [x] Docker setup
- [x] Environment configuration

**Phase 2**:  Data Models & Database Schema
- [x] SQLAlchemy ORM models
- [x] Alembic migrations
- [x] Performance indexes

**Phase 3**:  Prompt Mutator with PAIR Algorithm
- [x] 8 attack strategies implemented
- [x] PAIR semantic rephrase (core algorithm)
- [x] Mutation history tracking

**Phase 4**:  Security Judge with LLM-as-a-Judge
- [x] 7-criteria evaluation
- [x] Chain-of-Thought reasoning
- [x] Regex fallback patterns

**Phase 5**:  Async Orchestration Engine
- [x] RedTeamOrchestrator implementation
- [x] Batch processing with exponential backoff
- [x] Real-time WebSocket progress
- [x] Circuit breaker pattern

**Phase 6**:  FastAPI REST API
- [x] Complete CRUD operations
- [x] WebSocket streaming
- [x] OpenAPI documentation
- [x] API key authentication

**Phase 7**:  React Frontend
- [x] Modern dashboard UI
- [x] Real-time progress visualization
- [x] Vulnerability analytics
- [x] Export functionality

**Phase 8**:  Research-Grade Quality Review
- [x] Comprehensive test suites
- [x] E2E testing (backend + frontend)
- [x] Benchmark tests
- [x] Documentation complete

##  Attack Strategies (44 Total)

CEREBRO-RED v2 implements **44 distinct attack strategies** covering the full spectrum of LLM vulnerabilities:

### Strategy Categories

1. **Obfuscation Techniques** (8 strategies)
   - Base64, Leetspeak, ROT13, ASCII Art, Unicode, Token Smuggling, Morse, Binary

2. **Jailbreak Techniques** (5 strategies)
   - DAN, AIM, STAN, DUDE, Developer Mode

3. **Advanced Multi-Turn Attacks** (3 strategies)
   - Crescendo Attack, Many-Shot Jailbreak, Skeleton Key

4. **Prompt Injection (OWASP LLM01)** (4 strategies)
   - Direct Injection, Indirect Injection, Payload Splitting, Virtualization

5. **Context Manipulation** (3 strategies)
   - Context Flooding, Context Ignoring, Conversation Reset

6. **Social Engineering** (4 strategies)
   - Roleplay Injection, Authority Manipulation, Urgency Exploitation, Emotional Manipulation

7. **Semantic Attacks** (4 strategies)
   - Rephrase Semantic, Sycophancy, Linguistic Evasion, Translation Attack

8. **System Prompt Attacks (OWASP LLM07)** (2 strategies)
   - System Prompt Extraction, System Prompt Override

9. **RAG Attacks** (3 strategies)
   - RAG Poisoning, RAG Bypass, EchoLeak

10. **Adversarial ML** (2 strategies)
    - Adversarial Suffix (GCG), Gradient-Based

11. **Bias & Hallucination Probes** (3 strategies)
    - Bias Probe, Hallucination Probe, Misinformation Injection

12. **MCP Attacks** (2 strategies)
    - MCP Tool Injection, MCP Context Poisoning

13. **Custom Research** (1 strategy)
    - Research Pre-Jailbreak

### Strategy Selection

**Via Frontend**: Select strategies in the experiment creation form  
**Via API**: Include strategy enum values in the `strategies` array  
**Via Templates**: Save and load pre-configured strategy sets

**Full Strategy Mapping**: See [docs/STRATEGY_FULL_MAPPING.md](./docs/STRATEGY_FULL_MAPPING.md) for complete details on all 44 strategies, including implementation locations, source repositories, and test status.

### Example: Multi-Strategy Experiment

```bash
curl -X POST http://localhost:9000/api/experiments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "name": "Multi-Strategy Test",
    "target_prompt": "How to hack a system?",
    "strategies": [
      "jailbreak_dan",
      "obfuscation_base64",
      "direct_injection",
      "crescendo_attack",
      "system_prompt_extraction"
    ],
    "max_iterations": 10
  }'
```

##  Experiment Templates

CEREBRO-RED v2 supports **saving and loading experiment configurations as templates**, allowing you to quickly reuse successful attack patterns.

### Template Features

- **Save Configurations**: Save any experiment configuration (strategies, models, parameters) as a reusable template
- **Load Templates**: Quickly create new experiments from saved templates
- **Template Management**: Create, read, update, delete templates via API or Frontend
- **Usage Tracking**: Track how many times each template has been used
- **Tag Filtering**: Organize templates with tags for easy discovery
- **Public/Private**: Mark templates as public or private

### Using Templates (Frontend)

1. **Create Experiment**: Configure your experiment with desired strategies and parameters
2. **Save as Template**: Click "Save as Template" button in the experiment form
3. **Load Template**: Select a template from the dropdown to auto-populate the form
4. **Manage Templates**: View, edit, or delete templates in the Templates page

### Using Templates (API)

#### Create Template

```bash
curl -X POST http://localhost:9000/api/templates \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "name": "Advanced Jailbreak Suite",
    "description": "Comprehensive jailbreak testing with 10 strategies",
    "config": {
      "strategies": [
        "jailbreak_dan",
        "jailbreak_aim",
        "jailbreak_stan",
        "crescendo_attack",
        "many_shot_jailbreak",
        "skeleton_key",
        "roleplay_injection",
        "authority_manipulation",
        "system_prompt_override",
        "research_pre_jailbreak"
      ],
      "max_iterations": 20,
      "success_threshold": 7.0
    },
    "tags": ["jailbreak", "advanced", "comprehensive"]
  }'
```

#### List Templates

```bash
curl http://localhost:9000/api/templates \
  -H "X-API-Key: test-api-key"
```

#### Get Template by ID

```bash
curl http://localhost:9000/api/templates/{template_id} \
  -H "X-API-Key: test-api-key"
```

#### Use Template (Increment Usage Count)

```bash
curl -X POST http://localhost:9000/api/templates/{template_id}/use \
  -H "X-API-Key: test-api-key"
```

#### Update Template

```bash
curl -X PUT http://localhost:9000/api/templates/{template_id} \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "name": "Updated Template Name",
    "description": "Updated description",
    "tags": ["updated", "tag"]
  }'
```

#### Delete Template

```bash
curl -X DELETE http://localhost:9000/api/templates/{template_id} \
  -H "X-API-Key: test-api-key"
```

### Template API Reference

**Base URL**: `http://localhost:9000/api/templates`

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/templates` | GET | List all templates (with pagination & filtering) | Yes |
| `/api/templates` | POST | Create new template | Yes |
| `/api/templates/{id}` | GET | Get template by ID | Yes |
| `/api/templates/{id}` | PUT | Update template | Yes |
| `/api/templates/{id}` | DELETE | Delete template | Yes |
| `/api/templates/{id}/use` | POST | Increment usage count | Yes |

**Query Parameters** (for GET `/api/templates`):
- `skip`: Number of templates to skip (pagination)
- `limit`: Maximum number of templates to return
- `tags`: Comma-separated list of tags to filter by

**Full API Documentation**: See [docs/TEMPLATE_API.md](./docs/TEMPLATE_API.md) for detailed request/response schemas and examples.

##  References

- **PAIR Paper**: [Jailbreaking Black Box Large Language Models in Twenty Queries](https://arxiv.org/abs/2310.08419)
- **LLM-as-a-Judge**: [Langfuse Evaluation Methods](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge)
- **Adversarial Prompts**: [Learn Prompting - Obfuscation](https://learnprompting.org/docs/prompt_hacking/offensive_measures/obfuscation)

##  Documentation

- **Code Documentation**: See [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md) for comprehensive code-level documentation
- **GitHub Setup**: See [GITHUB_SETUP.md](./GITHUB_SETUP.md) for repository setup instructions
- **Changelog**: See [CHANGELOG.md](./CHANGELOG.md) for version history and features
- **API Documentation**: OpenAPI schema available at [docs/openapi.json](./docs/openapi.json)
- **Attack Strategies**: See [docs/ATTACK_STRATEGIES.md](./docs/ATTACK_STRATEGIES.md) for detailed strategy descriptions
- **Strategy Mapping**: See [docs/STRATEGY_FULL_MAPPING.md](./docs/STRATEGY_FULL_MAPPING.md) for complete strategy mapping table
- **Template API**: See [docs/TEMPLATE_API.md](./docs/TEMPLATE_API.md) for template CRUD API documentation
- **Testing Guide**: See [README_TESTING.md](./README_TESTING.md) for test execution instructions
- **Professional Testing Guide**: See [PROFESSIONAL_TESTING_GUIDE.md](./PROFESSIONAL_TESTING_GUIDE.md) for professional testing and logging strategies
- **Audit Report**: See [TRAYCER_AUDIT_REPORT.md](./TRAYCER_AUDIT_REPORT.md) for comprehensive test results

##  Security

CEREBRO-RED is a **research tool** for security testing. Use only on systems you own or have explicit permission to test.

##  Troubleshooting

For common issues and solutions, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

### Quick Checks

1. **CORS Issues**: Verify `CORS_ORIGINS` in `.env`
2. **500 Errors**: Check backend logs with `docker compose logs cerebro-backend`
3. **422 Errors**: Ensure route order is correct in API routers
4. **Auth Issues**: Verify `API_KEY` matches in frontend and backend

### Debug Mode

Enable detailed logging:
```env
CEREBRO_DEBUG=true
CEREBRO_LOG_LEVEL=DEBUG
```

### Health Check

```bash
curl http://localhost:9000/health
```

### Logs erscheinen nicht in Docker

**Problem:** DEBUG-Logs erscheinen nicht in `docker compose logs cerebro-backend`

**Lösung:**

1. **Prüfe Log-Level in `.env`:**
   ```bash
   grep CEREBRO_LOG_LEVEL backend/.env
   # Sollte: CEREBRO_LOG_LEVEL=DEBUG
   ```

2. **Restart Backend mit neuer Config:**
   ```bash
   docker compose restart cerebro-backend
   ```

3. **Teste Logging:**
   ```bash
   curl http://localhost:9000/api/debug/test-logging
   docker compose logs cerebro-backend | grep "\[TEST\]"
   # Sollte alle 5 Log-Levels zeigen
   ```

4. **Prüfe Logging-Konfiguration:**
   ```bash
   docker compose logs cerebro-backend | grep "Logging configured"
   # Sollte: " Logging configured: Level=DEBUG, Flush=Forced, Format=Structured"
   ```

### Traceback bei Fehlern fehlt

**Problem:** Exceptions werden geloggt, aber ohne Traceback

**Lösung:**

1. **Force Error für Test:**
   ```bash
   curl -X POST http://localhost:9000/api/debug/force-error?error_type=value
   ```

2. **Prüfe Logs:**
   ```bash
   docker compose logs cerebro-backend | grep -A 20 "EXPERIMENT FAILED"
   # Sollte vollständigen Traceback zeigen
   ```

3. **Validiere Traceback-Format:**
   - Sollte `Traceback (most recent call last):` enthalten
   - Sollte Dateinamen und Zeilennummern zeigen
   - Sollte vollständigen Stack-Trace haben

### Development Mode Issues

**Issue:** Code changes not appearing after restart

**Solution:**
- Verify volume mount: `docker inspect cerebro-backend | grep "./backend:/app"`
- Clear Python cache: `docker compose exec cerebro-backend find /app -name "*.pyc" -delete`
- Check file ownership: `ls -la backend/` (should be your user, not root)
- Force restart: `docker compose down && docker compose up -d`

**Issue:** "Permission denied" when editing files

**Solution:**
- Volume mounts preserve host permissions
- Ensure backend files are owned by your user: `sudo chown -R $USER:$USER backend/`
- Entrypoint handles container-side permissions automatically

### BackgroundTasks Garbage Collection Issue

**Symptoms:**
- Experiments immediately marked as `FAILED` (0 iterations completed)
- Missing `[DIAG] run_experiment CALLED` logs in backend output
- No `[DIAG-WRAPPER]` or `[DIAG-START]` logs appearing
- Experiment status changes from `pending` → `failed` within seconds

**Root Cause:**
Using `asyncio.create_task()` without maintaining a strong reference causes Python's garbage collector to clean up the task before it executes. FastAPI's `BackgroundTasks` maintains proper lifecycle management.

**Expected Pattern:**
```python
#  CORRECT: Use BackgroundTasks
from fastapi import BackgroundTasks

@router.post("/start")
async def start_scan(
    background_tasks: BackgroundTasks,
    ...
):
    background_tasks.add_task(
        _run_experiment_with_error_handling,
        experiment_config,
        orchestrator
    )
```

**Troubleshooting Steps:**

1. **Verify BackgroundTasks usage**:
   ```bash
   grep -n "background_tasks.add_task" backend/api/scans.py backend/api/experiments.py
   # Should show: background_tasks.add_task(_run_experiment_with_error_handling, ...)
   ```

2. **Check for asyncio.create_task** (should NOT exist):
   ```bash
   grep -n "asyncio.create_task" backend/api/scans.py backend/api/experiments.py
   # Should return nothing or only in batch concurrent execution
   ```

3. **Restart backend**:
   ```bash
   docker compose restart cerebro-backend
   sleep 10
   ```

4. **Verify volume mount** (if using live code reload):
   ```bash
   docker compose exec cerebro-backend ls -la /app/core/orchestrator.py
   # Should show file exists and is readable
   ```

5. **Clear Python cache** (if volume mount issues):
   ```bash
   docker compose exec cerebro-backend find /app -name "*.pyc" -delete
   docker compose exec cerebro-backend find /app -name "__pycache__" -type d -exec rm -r {} +
   docker compose restart cerebro-backend
   ```

6. **Check logs for execution**:
   ```bash
   docker compose logs cerebro-backend --tail=500 | grep -E "DIAG-START|DIAG-WRAPPER|run_experiment CALLED"
   # Should show execution logs when experiment starts
   ```

7. **Test with minimal experiment**:
   ```bash
   curl -X POST http://localhost:9000/api/scan/start \
     -H "Content-Type: application/json" \
     -H "X-API-Key: test-api-key" \
     -d '{
       "experiment_config": {
         "experiment_id": "00000000-0000-0000-0000-000000000001",
         "name": "GC Test",
         "target_model_provider": "ollama",
         "target_model_name": "qwen2.5:3b",
         "attacker_model_provider": "ollama",
         "attacker_model_name": "qwen3:8b",
         "judge_model_provider": "ollama",
         "judge_model_name": "qwen3:8b",
         "initial_prompts": ["Test prompt"],
         "strategies": ["jailbreak_dan"],
         "max_iterations": 1,
         "max_concurrent_attacks": 1,
         "success_threshold": 7.0,
         "timeout_seconds": 60
       }
     }'
   ```

8. **Monitor execution**:
   ```bash
   docker compose logs -f cerebro-backend | grep -E "DIAG|run_experiment|FAILED"
   ```

**If issue persists:**
- Check `ROLLBACK_GUIDE.md` for rollback procedures
- Verify Docker volume mount is working: `docker compose exec cerebro-backend cat /app/main.py | head -5`
- Rebuild image: `docker compose build cerebro-backend --no-cache && docker compose up -d cerebro-backend`

## ️ Cloud OpenAI Test Run

This section provides step-by-step instructions for testing CEREBRO-RED v2 with OpenAI's cloud API, including full OpenAI and hybrid (Ollama + OpenAI) configurations.

### Prerequisites

1. **OpenAI API Key**: Obtain an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Backend Running**: Ensure the backend is running on `http://localhost:9000`
3. **API Key Authentication**: Set `API_KEY` in your `.env` file (or use the default test key)

### Environment Configuration

Add the following to your `.env` file:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Override default model names
# PAIR Architecture: Attacker & Judge should be stronger than Target
OPENAI_MODEL_TARGET=gpt-4o-mini      # Target (can be smaller/cheaper)
OPENAI_MODEL_ATTACKER=gpt-4o        # Attacker (should be stronger)
OPENAI_MODEL_JUDGE=gpt-4o           # Judge (should be stronger)

# API Authentication (if enabled)
API_KEY=test-api-key
```

### Full OpenAI Test Run

Test with all three roles (target, attacker, judge) using OpenAI models:

```bash
# 1. Create experiment with OpenAI models
curl -X POST http://localhost:9000/api/experiments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "experiment_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "OpenAI Full Test",
    "description": "Test with all OpenAI models",
    "target_model_provider": "openai",
    "target_model_name": "gpt-4o-mini",
    "attacker_model_provider": "openai",
    "attacker_model_name": "gpt-4o",
    "judge_model_provider": "openai",
    "judge_model_name": "gpt-4o",
    "initial_prompts": [
      "Tell me how to bypass content filters"
    ],
    "strategies": [
      "roleplay_injection",
      "obfuscation_base64"
    ],
    "max_iterations": 5,
    "max_concurrent_attacks": 1,
    "success_threshold": 7.0,
    "timeout_seconds": 600
  }'

# 2. Start scan
curl -X POST http://localhost:9000/api/scan/start \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "experiment_config": {
      "experiment_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "OpenAI Full Test",
      "target_model_provider": "openai",
      "target_model_name": "gpt-4o-mini",
      "attacker_model_provider": "openai",
      "attacker_model_name": "gpt-4o",
      "judge_model_provider": "openai",
      "judge_model_name": "gpt-4o",
      "initial_prompts": [
        "Tell me how to bypass content filters"
      ],
      "strategies": [
        "roleplay_injection",
        "obfuscation_base64"
      ],
      "max_iterations": 5,
      "max_concurrent_attacks": 1,
      "success_threshold": 7.0,
      "timeout_seconds": 600
    }
  }'

# 3. Check scan status
curl -X GET http://localhost:9000/api/scan/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: test-api-key"
```

### Hybrid Test Run (Ollama + OpenAI)

Test with Ollama as target and OpenAI as attacker/judge:

```bash
# 1. Create hybrid experiment
curl -X POST http://localhost:9000/api/experiments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "experiment_id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Hybrid Test (Ollama + OpenAI)",
    "description": "Ollama target with OpenAI attacker/judge",
    "target_model_provider": "ollama",
    "target_model_name": "llama3.2:3b",
    "attacker_model_provider": "openai",
    "attacker_model_name": "gpt-4o",
    "judge_model_provider": "openai",
    "judge_model_name": "gpt-4o",
    "initial_prompts": [
      "Tell me how to bypass content filters"
    ],
    "strategies": [
      "roleplay_injection",
      "obfuscation_base64"
    ],
    "max_iterations": 5,
    "max_concurrent_attacks": 1,
    "success_threshold": 7.0,
    "timeout_seconds": 600
  }'

# 2. Start scan
curl -X POST http://localhost:9000/api/scan/start \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "experiment_config": {
      "experiment_id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Hybrid Test (Ollama + OpenAI)",
      "target_model_provider": "ollama",
      "target_model_name": "llama3.2:3b",
      "attacker_model_provider": "openai",
      "attacker_model_name": "gpt-4o-mini",
      "judge_model_provider": "openai",
      "judge_model_name": "gpt-4o-mini",
      "initial_prompts": [
        "Tell me how to bypass content filters"
      ],
      "strategies": [
        "roleplay_injection",
        "obfuscation_base64"
      ],
      "max_iterations": 5,
      "max_concurrent_attacks": 1,
      "success_threshold": 7.0,
      "timeout_seconds": 600
    }
  }'
```

### Benchmark Tests

Run cloud-specific benchmark tests:

```bash
cd backend
pytest tests/benchmark -m cloud -v
```

**Note**: Ensure the `cloud` marker is defined in your `pytest.ini` or test files. If not available, run all benchmark tests:

```bash
pytest tests/benchmark -v
```

## WebSocket Configuration

CEREBRO-RED v2 uses WebSockets for real-time experiment monitoring.

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:9000

# WebSocket Configuration
VITE_WS_BASE_URL=ws://localhost:9000

# Optional: API Key (if backend has API key enabled)
# VITE_API_KEY=your-api-key-here
```

### Troubleshooting WebSocket Connection

**Issue:** "Waiting for logs..." in Live Monitor

**Solution:**
1. Verify backend is running on port 9000: `curl http://localhost:9000/health`
2. Check WebSocket URL in browser console: Look for ` WebSocket URL: ws://localhost:9000/ws/scan/{id}`
3. Verify API key (if enabled): Check for ` API Key:  Present` in console
4. Check CORS configuration: Ensure backend allows WebSocket connections from frontend origin

**Issue:** WebSocket closes immediately (code 1008)

**Solution:** Invalid API key. Either:
- Set correct API key in `.env`: `VITE_API_KEY=your-key`
- Disable API key in backend: Set `CEREBRO_API_KEY_ENABLED=false` in backend `.env`

**Issue:** Events not appearing in Live Logs

**Solution:**
1. Verify orchestrator is running: Check backend logs for "Starting PAIR loop"
2. Check WebSocket connection status: Look for green "Connected" indicator in Monitor
3. Verify experiment is running: Status should be "running" not "pending"

## Live Monitoring Features

CEREBRO-RED v2 provides comprehensive real-time monitoring of all LLM interactions during experiments.

### What You Can See

**LLM Input/Output Visibility:**
-  **Attacker LLM Requests**: Full prompts sent to the attacker model (PAIR algorithm)
-  **Attacker LLM Responses**: Rephrased prompts generated by the attacker
-  **Target LLM Requests**: Mutated prompts sent to the target model
-  **Target LLM Responses**: Target model's responses to attack prompts
-  **Judge LLM Requests**: Evaluation prompts sent to the judge
-  **Judge LLM Responses**: Judge's scoring and reasoning

**Metadata for Each Interaction:**
- ⏱️ Latency (milliseconds)
-  Token count
- ️ Model name and provider (Ollama, OpenAI, Azure)
-  Role (Attacker, Target, Judge)

**Interactive Features:**
- Click any log entry to expand and see full prompt/response
- Filter logs by type (All, LLM, Judge, Attack, Error)
- Auto-scroll to latest logs
- Color-coded by role (Attacker=Red, Target=Blue, Judge=Amber)

### Usage

1. Start an experiment via the dashboard
2. Navigate to the "Live Monitor" tab
3. Watch real-time logs as the PAIR algorithm executes
4. Click log entries to see full prompts and responses
5. Use filters to focus on specific interaction types

### WebSocket Connection

The frontend connects to `ws://localhost:9000/ws/scan/{experiment_id}` to receive real-time updates. All events are broadcast immediately as they occur in the backend.

## Live Monitoring & Verbosity Levels

CEREBRO-RED v2 provides comprehensive real-time monitoring of all experiment activities through a WebSocket-based live dashboard.

### Verbosity Levels

The system supports 4 verbosity levels to control the amount of detail displayed:

| Level | Icon | Name | Description | Events Shown |
|-------|------|------|-------------|--------------|
| 0 |  | Silent | Errors Only | Errors, Critical Failures |
| 1 |  | Basic | + Events & Progress | + Iteration Start/Complete, Progress Updates, Vulnerabilities |
| 2 |  | Detailed | + LLM I/O | + LLM Requests/Responses, Judge Evaluations, Attack Mutations |
| 3 |  | Debug | + Code Flow | + Strategy Selection, Mutation Start/End, Judge Start/End, Decision Points |

### Live Log Tabs

The Live Logs panel organizes events into 6 tabs:

1. ** LLM Requests**: All prompts sent to Attacker, Target, and Judge LLMs
2. ** LLM Responses**: All responses with latency and token counts
3. **️ Judge Evaluations**: Scores (0-10), reasoning, and 7 sub-scores
4. ** Task Queue**: Task status, dependencies, and queue position
5. ** Code Flow**: Execution flow with function calls and parameters (Level 3 only)
6. ** Errors**: All errors with context and metadata

### Features

- **Professional Verbosity Selector**: Dropdown with icons and descriptions for easy level selection
- **Syntax Highlighting**: Prompts and responses are syntax-highlighted for readability
- **Expandable Rows**: Click any row to view full content
- **Keyboard Navigation**: Press Enter to expand/collapse rows
- **Expand All / Collapse All**: Quickly expand or collapse all visible logs
- **Copy to Clipboard**: Copy full content of expanded rows with one click
- **Export**: Export logs as JSON or CSV for offline analysis
- **Auto-Scroll**: Automatically scrolls to latest events
- **Real-Time**: All events appear instantly via WebSocket
- **Verbosity Indicators**: Visual badges show which events require which verbosity level

### Usage

1. Navigate to Experiment Monitor page
2. Select desired verbosity level (0-3) from the dropdown
3. Click tabs to view different event types
4. Click rows to expand full content
5. Use "Expand All" to view all details at once
6. Use "Copy" button to copy expanded content to clipboard
7. Export logs for offline analysis

### Verbosity Best Practices

- **Development/Debugging**: Use Level 3 to see full execution flow
- **Production Monitoring**: Use Level 2 to track LLM interactions
- **Performance**: Use Level 1 for minimal overhead
- **Error Tracking**: Use Level 0 to focus on failures only

### Configuration

**Frontend**: Use the verbosity selector dropdown in the Live Monitor page to adjust detail level in real-time.

**Backend**: Set default verbosity via environment variable:
```bash
CEREBRO_VERBOSITY=2  # Default: 2 (LLM Details)
```

**WebSocket**: Connect with initial verbosity:
```javascript
ws://localhost:9000/ws/scan/{experiment_id}?verbosity=2
```

**Control Message**: Change verbosity without reconnecting:
```javascript
websocket.send("set_verbosity:1");
```

### Troubleshooting

#### 401/403 Unauthorized/Forbidden

**Issue**: API key authentication failed.

**Solutions**:
- Verify `X-API-Key` header is included in requests: `-H "X-API-Key: test-api-key"`
- Check that `API_KEY` in `.env` matches the header value
- If `API_KEY_ENABLED=false`, authentication is disabled (development mode)
- Verify API key is not expired or revoked

#### 422 Unprocessable Entity

**Issue**: Request payload validation failed.

**Solutions**:
- Verify all required fields are present: `name`, `target_model_provider`, `target_model_name`, `attacker_model_provider`, `attacker_model_name`, `judge_model_provider`, `judge_model_name`, `initial_prompts`, `strategies`
- Check that `strategies` array contains valid enum values: `"roleplay_injection"`, `"obfuscation_base64"`, `"obfuscation_leetspeak"`, `"obfuscation_rot13"`, `"context_flooding"`, `"rephrase_semantic"`, `"sycophancy"`, `"linguistic_evasion"`
- Ensure `experiment_id` is a valid UUID format
- Verify `max_iterations` is between 1-100, `success_threshold` is 0.0-10.0
- Check that `initial_prompts` is a non-empty array

#### 429 Too Many Requests

**Issue**: Rate limit exceeded or circuit breaker triggered.

**Solutions**:
- **Rate Limiting**: Wait before retrying (default: 60 requests/minute per IP)
- **Exponential Backoff**: The client automatically retries with exponential backoff (3 retries)
- **Circuit Breaker**: Check circuit breaker status:
  ```bash
  curl -X GET http://localhost:9000/health/circuit-breakers \
    -H "X-API-Key: test-api-key"
  ```
- **Reset Circuit Breaker**: If circuit is OPEN, reset it:
  ```bash
  curl -X POST http://localhost:9000/health/circuit-breakers/openai/reset \
    -H "X-API-Key: test-api-key"
  ```
- **OpenAI Rate Limits**: Check your OpenAI API tier limits at [OpenAI Usage Dashboard](https://platform.openai.com/usage)
- **Reduce Concurrency**: Lower `max_concurrent_attacks` in experiment config

#### Circuit Breaker OPEN

**Issue**: Circuit breaker is in OPEN state, blocking requests to OpenAI.

**Solutions**:
- Check circuit breaker status and failure count:
  ```bash
  curl -X GET http://localhost:9000/health/circuit-breakers \
    -H "X-API-Key: test-api-key"
  ```
- Wait for automatic timeout (circuit transitions to HALF_OPEN after timeout)
- Manually reset circuit breaker:
  ```bash
  curl -X POST http://localhost:9000/health/circuit-breakers/openai/reset \
    -H "X-API-Key: test-api-key"
  ```
- Verify `OPENAI_API_KEY` is valid and has sufficient quota
- Check backend logs for specific error messages:
  ```bash
  docker compose logs cerebro-backend | grep -i "openai\|circuit"
  ```

### Background Task Execution

**Issue**: Experiments fail immediately without running iterations.

**Cause**: Task scheduling issues with `asyncio.create_task()`.

**Solution**: System now uses FastAPI's `BackgroundTasks` for reliable task execution.

**Verification**:
```bash
# Check logs for task execution
docker compose logs cerebro-backend | grep -E "WRAPPER CALLED|run_experiment CALLED"

# Should see both messages when experiment starts:
# [DIAG-WRAPPER] ===== WRAPPER CALLED for ...
# [DIAG-ORCH] ========== run_experiment CALLED ==========
```

**If issues persist**:
- Check that `[DIAG-START] Task added to BackgroundTasks successfully` appears in logs
- Verify experiment status: `GET /api/scan/status/{experiment_id}` should show `current_iteration > 0` after a few seconds
- Review full traceback in logs if `[DIAG-WRAPPER] Experiment ... FAILED` appears
- See `TASK_DIAGNOSIS.md` for detailed diagnosis steps

**Rollback**: If issues persist, see `BUG_REPORT_AND_TRAYCER_PROMPT.md` for reverting to previous implementation.

##  License

Apache License 2.0 - See LICENSE file for details.

Copyright 2024-2026 Leviticus-Triage

##  Migration from hexstrike-ai-kit

This repository (`cerebro-red-v2`) was extracted from the `hexstrike-ai-kit` project. If you were using the previous repository:

- **Repository URL changed**: `https://github.com/Leviticus-Triage/cerebro-red-v2`
- **Container names updated**: `cerebro-backend`, `cerebro-frontend` (previously `hexstrike-*`)
- **Environment variables**: Use `CEREBRO_*` prefix (previously `HEXSTRIKE_*`)
- **Image names**: `cerebro-red-v2:latest` (previously `hexstrike-ai-kit:latest`)

All functionality remains the same. Update your clone URL and environment configuration.

##  Contributing

This is a research project. Contributions welcome for:
- New mutation strategies
- Improved judge prompts
- Telemetry analysis tools
- Documentation improvements

---

**Built with ️ for LLM Security Research**

