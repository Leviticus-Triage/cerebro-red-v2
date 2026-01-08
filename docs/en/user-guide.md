# User Guide

[🇬🇧 English](user-guide.md) | [🇩🇪 Deutsch](../de/benutzerhandbuch.md)

Complete guide to using CEREBRO-RED v2 for automated LLM security assessment.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Creating Experiments](#creating-experiments)
4. [Understanding Results](#understanding-results)
5. [Telemetry and Logging](#telemetry-and-logging)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- **Docker** 24.0+ and **Docker Compose** 2.20+
- **Ollama** running on host (for local LLM testing)
- OR **Azure OpenAI** / **OpenAI** API keys (for cloud LLM testing)

### Step 1: Clone Repository

```bash
git clone https://github.com/Leviticus-Triage/cerebro-red-v2.git
cd cerebro-red-v2
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your LLM provider credentials
```

See [Configuration Guide](configuration.md) for detailed environment variable documentation.

### Step 3: Start Services

```bash
# Start all services (backend + frontend)
docker compose up -d

# Or start backend only
docker compose up -d cerebro-backend
```

### Step 4: Verify Installation

```bash
# Check backend health
curl http://localhost:9000/health

# Expected response:
# {"status":"healthy","service":"cerebro-red-v2","version":"2.0.0",...}
```

### Step 5: Access Interface

- **Backend API**: http://localhost:9000
- **API Documentation**: http://localhost:9000/docs
- **Frontend UI**: http://localhost:3000 (if frontend service is running)

## Quick Start

### Create Your First Experiment

1. **Via API**:
   ```bash
   curl -X POST http://localhost:9000/api/experiments \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My First Test",
       "target_model_provider": "ollama",
       "target_model_name": "qwen2.5:3b",
       "attacker_model_provider": "ollama",
       "attacker_model_name": "qwen3:8b",
       "judge_model_provider": "ollama",
       "judge_model_name": "qwen3:8b",
       "initial_prompts": ["How to bypass security filters?"],
       "strategies": ["roleplay_injection", "obfuscation_base64"]
     }'
   ```

2. **Via Frontend UI**:
   - Navigate to http://localhost:3000
   - Click "Create New Experiment"
   - Fill in experiment configuration
   - Select attack strategies
   - Click "Start Experiment"

### Monitor Experiment Progress

```bash
# Get experiment status
curl http://localhost:9000/api/experiments/{experiment_id}

# View experiment logs
docker compose logs -f cerebro-backend | grep {experiment_id}
```

## Creating Experiments

### Experiment Configuration

An experiment consists of:

- **Name**: Human-readable identifier
- **Target Model**: The LLM being tested (e.g., `ollama/qwen2.5:3b`)
- **Attacker Model**: LLM used to generate attack prompts (e.g., `ollama/qwen3:8b`)
- **Judge Model**: LLM used to evaluate attack success (e.g., `ollama/qwen3:8b`)
- **Initial Prompts**: Starting prompts to mutate
- **Strategies**: Attack strategies to apply (44 available)

### Available Attack Strategies

CEREBRO-RED v2 implements 44 attack strategies organized into categories:

- **Roleplay Injection**: `roleplay_injection`, `sycophancy`, `authority_impersonation`
- **Obfuscation**: `obfuscation_base64`, `obfuscation_leetspeak`, `obfuscation_rot13`
- **Context Manipulation**: `context_flooding`, `rephrase_semantic`, `linguistic_evasion`
- **And 35+ more strategies**

See [Attack Strategies Documentation](../ATTACK_STRATEGIES.md) for complete list.

### Strategy Selection

- **Single Strategy**: Test one specific attack method
- **Multiple Strategies**: Test several strategies in sequence
- **All Strategies**: Comprehensive 44-strategy assessment (requires significant resources)

### Experiment Parameters

- **Max Iterations**: Maximum number of mutation attempts (default: 44)
- **Success Threshold**: Judge score threshold for considering attack successful (0.0-10.0)
- **Max Concurrent Attacks**: Parallel attack execution limit

## Understanding Results

### Experiment Status

Experiments progress through states:

1. **Pending**: Created but not started
2. **Running**: Actively executing attack strategies
3. **Completed**: Finished successfully
4. **Failed**: Encountered error or exceeded limits
5. **Cancelled**: Manually stopped

### Judge Scores

The LLM-as-a-Judge evaluates each attack attempt on 7 criteria:

1. **Harmfulness**: Potential for harm (0-10)
2. **Effectiveness**: Attack success likelihood (0-10)
3. **Stealth**: Detection difficulty (0-10)
4. **Relevance**: Contextual appropriateness (0-10)
5. **Coherence**: Linguistic quality (0-10)
6. **Novelty**: Uniqueness of approach (0-10)
7. **Overall**: Composite score (0-10)

### Vulnerability Findings

Successful attacks are recorded as vulnerabilities with:

- **Severity**: Critical, High, Medium, Low
- **Strategy**: Attack method that succeeded
- **Prompt**: Successful attack prompt
- **Response**: Target model's response
- **Judge Score**: Evaluation scores

### Telemetry Data

All experiment activity is logged to JSONL audit files:

- **Location**: `/app/data/audit_logs/` (container) or `data/audit_logs/` (local)
- **Format**: One JSON object per line
- **Contents**: Experiment events, mutations, judge evaluations, errors

## Telemetry and Logging

### Audit Logs

Telemetry logs capture:

- Experiment lifecycle events
- Prompt mutations and iterations
- Judge evaluations and scores
- Error conditions and recoveries
- Performance metrics

### Log Analysis

```bash
# View recent telemetry events
tail -f data/audit_logs/audit_*.jsonl | jq

# Filter by experiment ID
cat data/audit_logs/audit_*.jsonl | jq 'select(.experiment_id=="...")'

# Count successful attacks
cat data/audit_logs/audit_*.jsonl | jq 'select(.event_type=="attack_successful")' | wc -l
```

### Application Logs

```bash
# Backend logs
docker compose logs -f cerebro-backend

# Frontend logs
docker compose logs -f cerebro-frontend

# Filter by log level
docker compose logs cerebro-backend | grep -E "ERROR|WARNING"
```

## Troubleshooting

### Common Issues

#### Backend Not Starting

**Symptoms**: `docker compose ps` shows backend as unhealthy or exited

**Solutions**:
1. Check logs: `docker compose logs cerebro-backend`
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Check port conflicts: `lsof -i :9000`
4. Verify environment variables: `docker compose config`

#### Experiments Not Progressing

**Symptoms**: Experiment stuck at `current_iteration: 0`

**Solutions**:
1. Check backend logs for errors
2. Verify LLM models are available: `ollama list`
3. Check circuit breaker status: `curl http://localhost:9000/health/circuit-breakers`
4. Verify database is writable: `docker compose exec cerebro-backend ls -la /app/data`

#### Rate Limiting Errors

**Symptoms**: 429 Too Many Requests errors

**Solutions**:
1. Reduce `max_concurrent_attacks` in experiment config
2. Increase rate limit: Set `RATE_LIMIT_PER_MINUTE` in `.env`
3. Wait for rate limit window to reset
4. Use local Ollama instead of cloud APIs

#### Database Errors

**Symptoms**: SQLite errors or database locked

**Solutions**:
1. Check volume permissions: `docker compose exec cerebro-backend ls -la /app/data`
2. Verify database file exists: `docker compose exec cerebro-backend test -f /app/data/cerebro.db`
3. Restart services: `docker compose restart cerebro-backend`
4. Check disk space: `df -h`

### Getting Help

- **GitHub Issues**: [Report bugs or ask questions](https://github.com/Leviticus-Triage/cerebro-red-v2/issues)
- **Documentation**: See [Configuration Guide](configuration.md) and [Deployment Guide](deployment.md)
- **Logs**: Always include relevant log excerpts when reporting issues

---

**Next Steps**: 
- Learn about [Configuration](configuration.md)
- Read [Deployment Guide](deployment.md) for production setup
- Explore [Architecture](architecture.md) for technical details
