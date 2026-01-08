# Deployment Guide

[🇬🇧 English](deployment.md) | [🇩🇪 Deutsch](../de/bereitstellung.md)

Complete guide for deploying CEREBRO-RED v2 locally and on Railway cloud platform.

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Railway Deployment](#railway-deployment)
3. [Health Checks](#health-checks)
4. [Demo Mode](#demo-mode)
5. [Troubleshooting](#troubleshooting)

## Local Deployment

### Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- Ollama installed and running (for local LLM testing)
- 4GB+ RAM available
- Ports 9000 (backend) and 3000 (frontend) available

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Leviticus-Triage/cerebro-red-v2.git
cd cerebro-red-v2

# 2. Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for most cases)

# 3. Start services
docker compose up -d

# 4. Verify deployment
curl http://localhost:9000/health
```

### Step-by-Step Setup

#### 1. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull qwen3:8b
ollama pull qwen2.5:3b

# Start Ollama service
ollama serve
```

#### 2. Configure Environment

Create `.env` file:

```bash
# Application
CEREBRO_HOST=0.0.0.0
CEREBRO_PORT=9000
CEREBRO_ENV=production

# Ollama
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434
OLLAMA_MODEL_ATTACKER=qwen3:8b
OLLAMA_MODEL_TARGET=qwen2.5:3b
OLLAMA_MODEL_JUDGE=qwen3:8b

# Database
DATABASE_URL=sqlite+aiosqlite:////app/data/cerebro.db
AUDIT_LOG_PATH=/app/data/audit_logs
```

#### 3. Start Services

```bash
# Start all services
docker compose up -d

# Or start backend only
docker compose up -d cerebro-backend

# View logs
docker compose logs -f
```

#### 4. Verify Deployment

```bash
# Check service status
docker compose ps

# Test backend health
curl http://localhost:9000/health | jq

# Test frontend (if running)
curl -I http://localhost:3000
```

### Access Points

- **Backend API**: http://localhost:9000
- **API Documentation**: http://localhost:9000/docs
- **Frontend UI**: http://localhost:3000
- **Health Check**: http://localhost:9000/health

## Railway Deployment

### Prerequisites

- Railway account (free tier available)
- GitHub repository connected to Railway
- Docker image built and pushed to GitHub Container Registry (optional)

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `Leviticus-Triage/cerebro-red-v2`

### Step 2: Configure Environment Variables

In Railway dashboard, set environment variables:

```bash
# Application
CEREBRO_ENV=production
CEREBRO_HOST=0.0.0.0
CEREBRO_PORT=$PORT  # Railway provides $PORT

# Demo Mode (for public demo)
DEMO_MODE=true

# Ollama (if using Railway Ollama service)
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_API_BASE=http://ollama-service:11434

# Or use cloud LLM
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=sqlite+aiosqlite:////app/data/cerebro.db
AUDIT_LOG_PATH=/app/data/audit_logs

# Security
API_KEY_ENABLED=false  # Disable for demo
CORS_ORIGINS=https://your-railway-domain.railway.app
```

### Step 3: Configure Railway Settings

Create `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "docker/Dockerfile.backend"
  },
  "deploy": {
    "startCommand": "python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Step 4: Deploy

Railway automatically:
1. Detects `railway.json` configuration
2. Builds Docker image from `docker/Dockerfile.backend`
3. Deploys to Railway infrastructure
4. Runs health checks
5. Provides public URL

### Step 5: Verify Deployment

```bash
# Get Railway URL
railway domain

# Test health endpoint
curl https://your-app.railway.app/health

# Test API
curl https://your-app.railway.app/api/experiments
```

## Health Checks

### Backend Health Endpoint

```bash
curl http://localhost:9000/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "cerebro-red-v2",
  "version": "2.0.0",
  "components": {
    "database": "healthy",
    "llm_providers": {
      "ollama": "healthy"
    },
    "telemetry": "healthy",
    "cors": "configured"
  }
}
```

### Circuit Breaker Status

```bash
curl http://localhost:9000/health/circuit-breakers
```

**Response**:
```json
{
  "openai": {
    "state": "CLOSED",
    "failure_count": 0,
    "last_failure": null
  }
}
```

### Docker Health Check

Docker Compose automatically monitors health:

```bash
# View health status
docker compose ps

# Expected output:
# NAME               STATUS
# cerebro-backend    Up 5 minutes (healthy)
```

## Demo Mode

### Configuration

Enable demo mode for read-only public instances:

```bash
DEMO_MODE=true
```

### Demo Mode Behavior

- **Read Operations**: Allowed (GET requests return mock data)
- **Write Operations**: Blocked (POST/PUT/DELETE return 403)
- **Mock Data**: Pre-configured experiments (running, failed, completed)
- **Guided Tour**: Frontend shows interactive tour automatically

### Mock Data

Demo mode serves static mock data:

- **3 Pre-configured Experiments**: Showcase different states
- **Sample Vulnerabilities**: Demonstrate findings
- **Realistic Telemetry**: Example audit logs

### Disabling Demo Mode

For production deployment:

```bash
DEMO_MODE=false
# Or omit DEMO_MODE variable entirely
```

## Troubleshooting

### Local Deployment Issues

#### Services Not Starting

```bash
# Check logs
docker compose logs cerebro-backend

# Verify Docker is running
docker ps

# Check port conflicts
lsof -i :9000
lsof -i :3000
```

#### Ollama Connection Failed

```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check host.docker.internal resolution
docker compose exec cerebro-backend ping host.docker.internal

# Linux fix: Ensure extra_hosts in docker-compose.yml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

#### Database Errors

```bash
# Check volume permissions
docker compose exec cerebro-backend ls -la /app/data

# Verify database exists
docker compose exec cerebro-backend test -f /app/data/cerebro.db

# Check disk space
df -h
```

### Railway Deployment Issues

#### Build Failures

1. Check Railway build logs
2. Verify `railway.json` syntax
3. Ensure Dockerfile path is correct
4. Check environment variables are set

#### Health Check Failures

1. Verify `$PORT` environment variable is set
2. Check start command matches Railway config
3. Review application logs in Railway dashboard
4. Test health endpoint manually

#### Service Unavailable

1. Check Railway service status
2. Verify resource limits (free tier: 512MB RAM)
3. Review error logs in Railway dashboard
4. Check database connectivity

### Performance Optimization

#### For Local Development

```yaml
# docker-compose.override.yml
services:
  cerebro-backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

#### For Production

```yaml
# docker-compose.yml
services:
  cerebro-backend:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

---

**Next Steps**:
- See [Configuration Guide](configuration.md) for detailed settings
- Read [Architecture Guide](architecture.md) for system design
- Check [Security Guide](security.md) for production hardening
