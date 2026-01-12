# CEREBRO-RED v2 Deployment Guide

This guide provides comprehensive instructions for deploying CEREBRO-RED v2 to various platforms, including cloud services (Railway, Heroku, AWS), containerized environments (Docker, Kubernetes), and local development setups.

## Table of Contents

- [Quick Start](#quick-start)
- [Railway Deployment](#railway-deployment)
- [Docker Deployment](#docker-deployment)
- [Local Development](#local-development)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Quick Start

The fastest way to deploy CEREBRO-RED v2 is using Railway with demo mode enabled:

1. Fork the repository to your GitHub account
2. Create a Railway account at [railway.app](https://railway.app)
3. Deploy from GitHub with one click
4. Railway automatically detects `railway.json` and deploys

For detailed instructions, see [Railway Deployment](#railway-deployment) below.

---

## Railway Deployment

Railway is a platform-as-a-service (PaaS) that provides simple cloud deployment with automatic SSL, dynamic scaling, and built-in monitoring. CEREBRO-RED v2 includes pre-configured Railway settings for seamless deployment.

### Prerequisites

- **Railway Account**: Free tier includes 512MB RAM, $5 credit/month ([Sign up](https://railway.app))
- **GitHub Repository**: Fork or clone CEREBRO-RED v2 to your GitHub account
- **Git Access**: Railway needs permission to access your repository

### Step 1: Create Railway Project

1. **Log in to Railway Dashboard**
   - Navigate to [railway.app](https://railway.app)
   - Click "Login" and authenticate with GitHub

2. **Create New Project**
   - Click "New Project" button
   - Select "Deploy from GitHub repo"
   - Choose your CEREBRO-RED v2 repository
   - Select the branch to deploy (typically `main`)

3. **Auto-Detection**
   - Railway automatically detects `railway.json` at repository root
   - Build configuration is loaded from `railway.json`:
     - **Builder**: DOCKERFILE
     - **Dockerfile Path**: `docker/Dockerfile.backend`
     - **Start Command**: `python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 2: Configure Environment Variables

Railway requires environment variables to be set in the dashboard. Use the `.env.railway` template as a guide:

1. **Open Environment Variables Settings**
   - In Railway dashboard, select your project
   - Navigate to **Settings** > **Environment**
   - Click "Raw Editor" for bulk paste

2. **Copy .env.railway Template**
   - Open `cerebro-red-v2/.env.railway` in your repository
   - Copy all environment variables
   - Paste into Railway's Raw Editor

3. **Customize Required Variables**

   **Demo Mode (Public Demo Instance)**:
   ```bash
   CEREBRO_DEMO_MODE=true
   CEREBRO_ENV=production
   API_KEY_ENABLED=false
   ```

   **Railway-Specific Variables**:
   ```bash
   CEREBRO_HOST=0.0.0.0
   CEREBRO_PORT=${PORT}  # Railway injects this automatically
   ```

   **CORS Configuration**:
   ```bash
   CORS_ORIGINS=https://*.railway.app
   ```

   **LLM Provider** (choose one):
   ```bash
   # Option 1: Ollama (requires separate Ollama service)
   DEFAULT_LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://ollama-service:11434

   # Option 2: OpenAI (cloud-based, requires API key)
   DEFAULT_LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   ```

4. **Save Environment Variables**
   - Click "Save" to apply changes
   - Railway will automatically redeploy with new configuration

### Step 3: Configure Build Settings

Railway should auto-detect build settings from `railway.json`, but verify:

1. **Navigate to Build Settings**
   - Click your service in Railway dashboard
   - Go to **Settings** > **Build**

2. **Verify Configuration**
   - **Builder**: `DOCKERFILE`
   - **Dockerfile Path**: `docker/Dockerfile.backend`
   - **Root Directory**: `/` (repository root)

3. **Optional: Custom Build Command**
   - For advanced use cases, you can override the build command
   - Default: Docker builds according to `Dockerfile.backend`

### Step 4: Deploy and Monitor

1. **Trigger Deployment**
   - Railway automatically deploys when:
     - Repository is connected for the first time
     - Environment variables are changed
     - New commits are pushed to the monitored branch

2. **Monitor Build Logs**
   - Click on your service in Railway dashboard
   - Navigate to **Deployments** tab
   - View real-time build logs:
     ```
     Building Docker image...
     Step 1/15 : FROM python:3.11-slim
     Step 2/15 : WORKDIR /app
     ...
     Successfully built <image-id>
     ```

3. **Health Check Validation**
   - Railway performs automatic health checks at `/health`
   - Health check must succeed within **30 seconds** or deployment fails
   - Monitor health check status in deployment logs:
     ```
     Health check passed: /health returned 200 OK
     Deployment successful
     ```

4. **Access Public URL**
   - Once deployed, Railway provides a public URL:
     ```
     https://<project-name>.railway.app
     ```
   - Click "Open App" in Railway dashboard or navigate to the URL

### Step 5: Verify Deployment

Test your deployment with these commands:

**1. Test Health Endpoint**
```bash
curl https://<project-name>.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "production",
  "demo_mode": true,
  "timestamp": "2026-01-08T18:00:00Z"
}
```

**2. Test Demo API**
```bash
curl https://<project-name>.railway.app/api/demo/experiments
```

Expected response:
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 3,
    "page": 1,
    "page_size": 20
  }
}
```

**3. Access Frontend (if deployed)**
```bash
# Open in browser
open https://<project-name>.railway.app
```

You should see the CEREBRO-RED v2 demo mode banner at the top:
```
🎯 Demo Mode — Explore pre-configured experiments (read-only)
```

### Railway-Specific Features

**1. Automatic Deployments**
- Enable automatic deployments on git push
- Navigate to **Settings** > **Deploys**
- Toggle "Auto-Deploy" for your branch

**2. Persistent Volumes**
- Railway provides persistent storage for database
- Database location: `/app/data/cerebro.db`
- Configured in `.env.railway`: `DATABASE_URL=sqlite+aiosqlite:////app/data/cerebro.db`

**3. Custom Domains**
- Railway supports custom domains (paid plans)
- Navigate to **Settings** > **Domains**
- Add your domain and configure DNS records

**4. Monitoring & Alerts**
- Railway provides built-in monitoring:
  - CPU and memory usage
  - Request logs
  - Health check history
- Set up alerts for deployment failures

**5. Restart Policies**
- Configured in `railway.json`:
  ```json
  "restartPolicyType": "ON_FAILURE",
  "restartPolicyMaxRetries": 3
  ```
- Automatically restarts failed deployments (max 3 retries)

---

## Troubleshooting

### Railway-Specific Issues

#### 1. Build Failures

**Symptom**: Railway build fails with Docker errors

**Solutions**:
- **Check Dockerfile Path**:
  ```bash
  # Verify railway.json points to correct Dockerfile
  cat railway.json | grep dockerfilePath
  # Expected: "dockerfilePath": "docker/Dockerfile.backend"
  ```

- **Verify COPY Paths**:
  - All `COPY` commands in `Dockerfile.backend` must use paths relative to repository root
  - Example: `COPY backend/ /app/` (not `COPY . /app/`)

- **Review Build Logs**:
  - Check Railway dashboard for specific error messages
  - Common issues: missing dependencies, syntax errors in Dockerfile

- **Test Locally**:
  ```bash
  # Build Docker image locally to identify issues
  docker build -f docker/Dockerfile.backend -t cerebro-red-test .
  ```

#### 2. Health Check Failures

**Symptom**: Deployment succeeds but health check fails, preventing public access

**Solutions**:
- **Verify $PORT Environment Variable**:
  ```bash
  # Check Railway dashboard: Settings > Environment
  # Ensure CEREBRO_PORT=${PORT} is set
  ```

- **Test Health Endpoint Locally**:
  ```bash
  # Start application locally
  cd backend
  python3 -m uvicorn main:app --host 0.0.0.0 --port 9000

  # Test health endpoint
  curl http://localhost:9000/health
  ```

- **Increase Health Check Timeout**:
  - Edit `railway.json`:
    ```json
    "healthcheckTimeout": 60  // Increase from 30 to 60 seconds
    ```
  - Commit and push changes

- **Check Application Logs**:
  - Railway dashboard > **Deployments** > Select deployment > **Logs**
  - Look for startup errors or database initialization issues

#### 3. Port Binding Errors

**Symptom**: Application fails to start with "Address already in use" or "Port binding failed"

**Solutions**:
- **Verify Start Command**:
  - Railway requires dynamic port binding via `$PORT` variable
  - Check `railway.json`:
    ```json
    "startCommand": "python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT"
    ```

- **Check Configuration Priority**:
  - Railway's `$PORT` overrides `CEREBRO_PORT`
  - Verify `backend/utils/config.py` reads `PORT` environment variable:
    ```python
    @field_validator("port", mode="before")
    @classmethod
    def get_port_from_env(cls, v):
        import os
        railway_port = os.getenv("PORT")
        if railway_port:
            return int(railway_port)
        return v
    ```

- **Test Port Binding**:
  ```bash
  # Set PORT environment variable locally
  export PORT=8080
  python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

#### 4. Demo Mode Not Working

**Symptom**: Demo mode banner not visible, demo endpoints return 404

**Solutions**:
- **Verify CEREBRO_DEMO_MODE**:
  ```bash
  # Check Railway environment variables
  # Ensure: CEREBRO_DEMO_MODE=true (not "True" or "1")
  ```

- **Check Demo Router Registration**:
  - Verify `backend/main.py` registers demo router:
    ```python
    if settings.app.demo_mode:
        app.include_router(demo_router, prefix="/api/demo", tags=["demo"])
    ```

- **Test Demo Endpoints**:
  ```bash
  # Test demo experiments endpoint
  curl https://<project-name>.railway.app/api/demo/experiments

  # Should return mock data, not 404
  ```

- **Review Startup Logs**:
  ```bash
  # Look for demo mode initialization message
  # Expected: "🎭 Demo mode enabled - mock data endpoints available at /api/demo/experiments"
  ```

#### 5. CORS Errors

**Symptom**: Frontend receives CORS errors in browser console

**Solutions**:
- **Add Railway Domain to CORS_ORIGINS**:
  ```bash
  # Railway environment variables
  CORS_ORIGINS=https://*.railway.app,https://your-custom-domain.com
  ```

- **Verify CORS Middleware**:
  - Check `backend/main.py` configures CORS middleware:
    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```

- **Test CORS Headers**:
  ```bash
  curl -H "Origin: https://your-app.railway.app" \
       -H "Access-Control-Request-Method: POST" \
       -H "Access-Control-Request-Headers: Content-Type" \
       -X OPTIONS \
       https://<project-name>.railway.app/api/demo/experiments
  ```

- **Check Browser Console**:
  - Open browser DevTools > Console
  - Look for specific CORS error messages
  - Example: "Access to fetch at '...' has been blocked by CORS policy"

#### 6. Resource Limits (Free Tier)

**Symptom**: Application crashes or becomes unresponsive due to resource constraints

**Railway Free Tier Limits**:
- **RAM**: 512MB
- **CPU**: 1 vCPU (shared)
- **Credits**: $5/month
- **Deployment Time**: Limited uptime

**Solutions**:
- **Reduce Logging Verbosity**:
  ```bash
  CEREBRO_VERBOSITY=1  # Minimal logging
  CEREBRO_LOG_LEVEL=WARNING  # Only warnings and errors
  ```

- **Disable Detailed Telemetry**:
  ```bash
  ENABLE_DETAILED_TELEMETRY=false
  ```

- **Optimize Database**:
  ```bash
  DATABASE_ECHO=false  # Disable SQL query logging
  ```

- **Use Cloud LLM Providers**:
  - Replace Ollama with OpenAI/Azure to offload compute
  ```bash
  DEFAULT_LLM_PROVIDER=openai
  OPENAI_API_KEY=sk-...
  ```

- **Upgrade to Paid Tier**:
  - Railway Pro: $20/month
  - Increased RAM (8GB), dedicated CPU, priority support

---

## Deployment Checklists

### Pre-Deployment Checklist

Before deploying to Railway, verify:

- [ ] `railway.json` exists at repository root
- [ ] `railway.json` points to correct Dockerfile: `docker/Dockerfile.backend`
- [ ] `.env.railway` template reviewed and customized
- [ ] Demo mode enabled: `CEREBRO_DEMO_MODE=true`
- [ ] API key auth disabled for public demo: `API_KEY_ENABLED=false`
- [ ] CORS origins include Railway domain: `CORS_ORIGINS=https://*.railway.app`
- [ ] Health check endpoint tested locally: `curl http://localhost:9000/health`
- [ ] Dockerfile builds successfully locally: `docker build -f docker/Dockerfile.backend .`
- [ ] Environment variables set in Railway dashboard (all required variables from `.env.railway`)
- [ ] LLM provider configured (Ollama service deployed or OpenAI API key set)

### Post-Deployment Checklist

After deployment completes, verify:

- [ ] Health check passes (green status in Railway dashboard)
- [ ] Public URL accessible: `https://<project-name>.railway.app`
- [ ] Health endpoint returns 200 OK: `/health`
- [ ] Demo API endpoints return mock data: `/api/demo/experiments`
- [ ] Frontend loads without errors (if deployed)
- [ ] Demo mode banner visible at top of page
- [ ] CORS headers present in API responses
- [ ] No errors in Railway deployment logs
- [ ] Database persists across restarts (test by restarting service)
- [ ] Write operations blocked with 403 response (demo mode enforcement)

---

## Best Practices

### Security

1. **Environment Variables**
   - Never commit secrets to repository (API keys, passwords)
   - Use Railway's environment variable storage
   - Rotate API keys regularly

2. **Demo Mode vs Production**
   - **Demo Mode**: `CEREBRO_DEMO_MODE=true`, `API_KEY_ENABLED=false`
   - **Production**: `CEREBRO_DEMO_MODE=false`, `API_KEY_ENABLED=true`, strong API keys

3. **CORS Configuration**
   - Restrict CORS origins to specific domains in production
   - Avoid wildcard `*` in production deployments

4. **HTTPS Enforcement**
   - Railway provides automatic HTTPS for all deployments
   - Ensure frontend uses HTTPS URLs for API calls

### Monitoring

1. **Health Checks**
   - Monitor health check history in Railway dashboard
   - Set up alerts for health check failures

2. **Application Logs**
   - Review logs regularly for errors and warnings
   - Use Railway's log search and filtering

3. **Resource Usage**
   - Monitor CPU and memory usage in Railway dashboard
   - Optimize application if approaching limits

### Deployment Automation

1. **Automatic Deployments**
   - Enable auto-deploy on git push for development branches
   - Use manual deploys for production branches

2. **CI/CD Integration**
   - Integrate with GitHub Actions for testing before deployment
   - Run tests, linting, and security scans in CI pipeline

3. **Rollback Strategy**
   - Railway provides one-click rollback to previous deployments
   - Test new features in staging environment before production

---

## Docker Deployment

For local Docker deployments or custom container orchestration:

### Build Docker Image

```bash
# Navigate to repository root
cd cerebro-red-v2

# Build backend image
docker build -f docker/Dockerfile.backend -t cerebro-red-backend:latest .

# Build frontend image (if applicable)
docker build -f docker/Dockerfile.frontend -t cerebro-red-frontend:latest ./frontend
```

### Run Docker Container

```bash
# Run backend container
docker run -d \
  --name cerebro-red-backend \
  -p 9000:9000 \
  -e CEREBRO_DEMO_MODE=true \
  -e CEREBRO_HOST=0.0.0.0 \
  -e CEREBRO_PORT=9000 \
  -v $(pwd)/data:/app/data \
  cerebro-red-backend:latest

# Check container logs
docker logs -f cerebro-red-backend

# Test health endpoint
curl http://localhost:9000/health
```

---

## Local Development

For local development and testing:

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Ollama or OpenAI API key (for LLM providers)

### Backend Setup

```bash
# Navigate to backend directory
cd cerebro-red-v2/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp ../.env.example .env

# Edit .env and configure settings
nano .env

# Run backend server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 9000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd cerebro-red-v2/frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env and configure settings
nano .env

# Run development server
npm run dev
```

### Access Application

- **Backend API**: http://localhost:9000
- **API Documentation**: http://localhost:9000/docs
- **Frontend**: http://localhost:5173
- **Health Check**: http://localhost:9000/health

---

## Support

For additional help:

- **Documentation**: [CEREBRO-RED v2 Docs](https://github.com/your-org/cerebro-red-v2/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/your-org/cerebro-red-v2/issues)
- **Railway Docs**: [railway.app/docs](https://docs.railway.app/)
- **Community**: Join our Discord/Slack for support

---

**Last Updated**: 2026-01-08
**Version**: 2.0.0
