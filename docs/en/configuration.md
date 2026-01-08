# Configuration Guide

[🇬🇧 English](configuration.md) | [🇩🇪 Deutsch](../de/konfiguration.md)

Complete reference for configuring CEREBRO-RED v2 environment variables and settings.

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [LLM Provider Configuration](#llm-provider-configuration)
3. [Database Configuration](#database-configuration)
4. [Security Settings](#security-settings)
5. [Performance Tuning](#performance-tuning)

## Environment Variables

### Application Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CEREBRO_HOST` | `0.0.0.0` | Host address to bind (use `0.0.0.0` for Docker, `127.0.0.1` for local) |
| `CEREBRO_PORT` | `9000` | Backend service port |
| `CEREBRO_ENV` | `production` | Environment mode: `development` or `production` |
| `DEBUG_MODE` | `false` | Enable debug logging and endpoints |
| `CEREBRO_LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `CEREBRO_VERBOSITY` | `1` | Verbosity level (0-5, higher = more verbose) |

### Example `.env` File

```bash
# Application
CEREBRO_HOST=0.0.0.0
CEREBRO_PORT=9000
CEREBRO_ENV=production
DEBUG_MODE=false

# Logging
CEREBRO_LOG_LEVEL=INFO
CEREBRO_VERBOSITY=1
```

## LLM Provider Configuration

CEREBRO-RED v2 supports multiple LLM providers via LiteLLM.

### Ollama (Local)

Best for: Privacy, offline operation, no API costs

```bash
# Ollama Configuration
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_HOST=http://host.docker.internal:11434

# Model Selection
OLLAMA_MODEL_ATTACKER=qwen3:8b
OLLAMA_MODEL_TARGET=qwen2.5:3b
OLLAMA_MODEL_JUDGE=qwen3:8b
```

**Setup**:
1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Pull models: `ollama pull qwen3:8b qwen2.5:3b`
3. Start Ollama: `ollama serve`

**Docker Note**: Use `host.docker.internal:11434` to access host Ollama from container.

### Azure OpenAI

Best for: Enterprise deployments, high-quality mutations

```bash
# Azure OpenAI Configuration
DEFAULT_LLM_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Model Selection (use deployment names)
AZURE_OPENAI_MODEL_ATTACKER=gpt-4-deployment
AZURE_OPENAI_MODEL_TARGET=gpt-3.5-turbo-deployment
AZURE_OPENAI_MODEL_JUDGE=gpt-4-deployment
```

### OpenAI

Best for: Fast responses, production testing

```bash
# OpenAI Configuration
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_ORG_ID=org-your-org-id  # Optional

# Model Selection
OPENAI_MODEL_ATTACKER=gpt-4
OPENAI_MODEL_TARGET=gpt-3.5-turbo
OPENAI_MODEL_JUDGE=gpt-4
```

## Database Configuration

### SQLite (Default)

```bash
DATABASE_URL=sqlite+aiosqlite:////app/data/cerebro.db
AUDIT_LOG_PATH=/app/data/audit_logs
```

**Paths**:
- **Container**: `/app/data/cerebro.db` (persisted via Docker volume)
- **Local**: `data/experiments/cerebro.db` (relative to backend directory)

**Volumes** (docker-compose.yml):
- `cerebro-data`: Main database storage
- `cerebro-experiments`: Experiment data
- `cerebro-audit-logs`: Telemetry logs
- `cerebro-results`: Analysis results

### PostgreSQL (Optional)

For production deployments requiring concurrent access:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cerebro
```

**Note**: Requires additional database setup and connection pooling configuration.

## Security Settings

### API Authentication

```bash
# API Key Authentication
API_KEY=your-secret-api-key
API_KEY_ENABLED=true
```

**Usage**:
```bash
curl -H "X-API-Key: your-secret-api-key" http://localhost:9000/api/experiments
```

**Disable for Development**:
```bash
API_KEY_ENABLED=false
```

### CORS Configuration

```bash
# Allowed Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000,http://localhost:9000

# Enable Credentials
CORS_CREDENTIALS=true
```

**Production**: Restrict to your frontend domain:
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Rate Limiting

```bash
# Requests per minute per IP
RATE_LIMIT_PER_MINUTE=60
```

**Adjust for**:
- **Local Development**: `RATE_LIMIT_PER_MINUTE=1000` (relaxed)
- **Production**: `RATE_LIMIT_PER_MINUTE=60` (standard)
- **High Traffic**: `RATE_LIMIT_PER_MINUTE=120` (increased)

## Performance Tuning

### Circuit Breaker Configuration

```bash
# Failure threshold before opening circuit
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5

# Timeout before attempting recovery (seconds)
CIRCUIT_BREAKER_TIMEOUT=60
```

**For Local Ollama** (slower responses):
```bash
CIRCUIT_BREAKER_FAILURE_THRESHOLD=15
CIRCUIT_BREAKER_TIMEOUT=120
CIRCUIT_BREAKER_JITTER_ENABLED=true
```

### Resource Limits

**Docker Compose** (docker-compose.yml):
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

**Adjust for**:
- **Small Experiments**: 2G RAM, 1 CPU
- **44-Strategy Tests**: 4G RAM, 2 CPUs
- **Production**: 8G RAM, 4 CPUs

### Concurrency Settings

```bash
# Maximum concurrent attack operations
MAX_CONCURRENT_ATTACKS=5
```

**Recommendations**:
- **Local Ollama**: `MAX_CONCURRENT_ATTACKS=3` (avoid overwhelming local LLM)
- **Cloud APIs**: `MAX_CONCURRENT_ATTACKS=10` (utilize API rate limits)
- **Large Experiments**: `MAX_CONCURRENT_ATTACKS=5` (balanced)

## Docker Compose Override

Create `docker-compose.override.yml` for local development:

```yaml
services:
  cerebro-backend:
    environment:
      - CEREBRO_ENV=development
      - DEBUG_MODE=true
      - CEREBRO_LOG_LEVEL=DEBUG
    volumes:
      - ./backend:/app  # Live code reload
```

**Usage**:
```bash
docker compose up -d  # Automatically uses override file
```

## Validation

### Verify Configuration

```bash
# Check environment variables
docker compose config

# Test backend configuration
curl http://localhost:9000/health | jq '.components'

# Verify LLM connectivity
curl http://localhost:9000/health | jq '.components.llm_providers'
```

### Common Configuration Issues

1. **Ollama Connection Failed**
   - Verify Ollama is running: `curl http://localhost:11434/api/tags`
   - Check `host.docker.internal` resolution (Linux: use `extra_hosts` in docker-compose.yml)

2. **API Key Authentication Failing**
   - Verify `API_KEY` matches request header `X-API-Key`
   - Check `API_KEY_ENABLED=true` is set

3. **Database Locked**
   - Ensure only one backend instance accesses database
   - Check volume permissions: `docker compose exec cerebro-backend ls -la /app/data`

---

**Next Steps**:
- See [Deployment Guide](deployment.md) for production configuration
- Read [Security Guide](security.md) for security best practices
- Check [User Guide](user-guide.md) for usage examples
