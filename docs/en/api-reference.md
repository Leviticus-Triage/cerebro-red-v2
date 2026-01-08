# API Reference

[🇬🇧 English](api-reference.md) | [🇩🇪 Deutsch](../de/api-referenz.md)

Complete API reference for CEREBRO-RED v2 backend endpoints.

## Introduction

The CEREBRO-RED v2 API provides RESTful endpoints and WebSocket connections for managing experiments, monitoring progress, and retrieving results. The API follows OpenAPI 3.1.0 specification and supports JSON request/response formats.

### Base URL

- **Local Development**: `http://localhost:9000`
- **Production**: Configured via `CEREBRO_HOST` and `CEREBRO_PORT` environment variables

### Authentication

Most endpoints require API key authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:9000/api/experiments
```

**Public Endpoints** (no authentication required):
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /metrics` - Application metrics

### Versioning

Current API version: **2.0.0**

API versioning is handled via the OpenAPI specification. Breaking changes will increment the major version number.

---

## Core Endpoints

### Health Check

#### `GET /health`

Check backend service health and component status.

**Authentication**: Not required

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
  },
  "cors_config": {
    "origins": ["http://localhost:3000"],
    "credentials": true,
    "methods": ["GET", "POST", "PUT", "DELETE"]
  },
  "timestamp": "2026-01-08T12:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### Experiments

#### `GET /api/experiments`

List all experiments.

**Authentication**: Required

**Query Parameters**:
- `status` (optional): Filter by status (`pending`, `running`, `completed`, `failed`, `cancelled`)
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "experiments": [
    {
      "id": "uuid-here",
      "name": "GPT-4 Security Assessment",
      "status": "running",
      "target_model": "gpt-4",
      "created_at": "2026-01-08T10:00:00Z",
      "updated_at": "2026-01-08T10:15:00Z",
      "progress": 0.65,
      "vulnerabilities_found": 3
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

#### `POST /api/experiments`

Create a new experiment.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "My Security Test",
  "target_model_provider": "ollama",
  "target_model_name": "qwen2.5:3b",
  "attacker_model_provider": "ollama",
  "attacker_model_name": "qwen3:8b",
  "judge_model_provider": "ollama",
  "judge_model_name": "qwen3:8b",
  "initial_prompts": ["How to bypass security filters?"],
  "strategies": ["roleplay_injection", "obfuscation_base64"],
  "max_iterations": 44,
  "success_threshold": 7.0
}
```

**Response**:
```json
{
  "id": "uuid-here",
  "name": "My Security Test",
  "status": "pending",
  "created_at": "2026-01-08T12:00:00Z"
}
```

**Status Codes**:
- `201 Created`: Experiment created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid API key

#### `GET /api/experiments/{experiment_id}`

Get experiment details.

**Authentication**: Required

**Response**:
```json
{
  "id": "uuid-here",
  "name": "My Security Test",
  "status": "running",
  "target_model": "ollama/qwen2.5:3b",
  "attacker_model": "ollama/qwen3:8b",
  "judge_model": "ollama/qwen3:8b",
  "strategies": ["roleplay_injection", "obfuscation_base64"],
  "current_iteration": 15,
  "max_iterations": 44,
  "vulnerabilities_found": 3,
  "created_at": "2026-01-08T12:00:00Z",
  "updated_at": "2026-01-08T12:15:00Z"
}
```

#### `DELETE /api/experiments/{experiment_id}`

Delete an experiment.

**Authentication**: Required

**Status Codes**:
- `204 No Content`: Experiment deleted successfully
- `404 Not Found`: Experiment not found

---

### Scan Control

#### `POST /api/scan/start`

Start experiment execution.

**Authentication**: Required

**Request Body**:
```json
{
  "experiment_id": "uuid-here"
}
```

**Response**:
```json
{
  "experiment_id": "uuid-here",
  "status": "running",
  "started_at": "2026-01-08T12:00:00Z"
}
```

#### `POST /api/scan/{experiment_id}/pause`

Pause a running experiment.

**Authentication**: Required

**Response**:
```json
{
  "experiment_id": "uuid-here",
  "status": "paused",
  "paused_at": "2026-01-08T12:30:00Z"
}
```

#### `POST /api/scan/{experiment_id}/resume`

Resume a paused experiment.

**Authentication**: Required

**Response**:
```json
{
  "experiment_id": "uuid-here",
  "status": "running",
  "resumed_at": "2026-01-08T12:35:00Z"
}
```

#### `POST /api/scan/{experiment_id}/cancel`

Cancel a running or paused experiment.

**Authentication**: Required

**Response**:
```json
{
  "experiment_id": "uuid-here",
  "status": "cancelled",
  "cancelled_at": "2026-01-08T12:40:00Z"
}
```

#### `GET /api/scan/status/{experiment_id}`

Get current scan status.

**Authentication**: Required

**Response**:
```json
{
  "experiment_id": "uuid-here",
  "status": "running",
  "current_iteration": 15,
  "total_iterations": 44,
  "progress": 0.34,
  "vulnerabilities_found": 3
}
```

---

### Vulnerabilities

#### `GET /api/vulnerabilities`

List all vulnerabilities across all experiments.

**Authentication**: Required

**Query Parameters**:
- `severity` (optional): Filter by severity (`critical`, `high`, `medium`, `low`)
- `experiment_id` (optional): Filter by experiment ID
- `limit` (optional): Maximum results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "vulnerabilities": [
    {
      "id": "vuln-uuid",
      "experiment_id": "exp-uuid",
      "severity": "high",
      "strategy": "roleplay_injection",
      "prompt": "You are a security researcher...",
      "response": "I can help you bypass...",
      "judge_score": 8.5,
      "found_at": "2026-01-08T12:20:00Z"
    }
  ],
  "total": 1
}
```

#### `GET /api/vulnerabilities/{vulnerability_id}`

Get vulnerability details.

**Authentication**: Required

**Response**:
```json
{
  "id": "vuln-uuid",
  "experiment_id": "exp-uuid",
  "severity": "high",
  "strategy": "roleplay_injection",
  "prompt": "You are a security researcher...",
  "response": "I can help you bypass...",
  "judge_scores": {
    "harmfulness": 8.0,
    "effectiveness": 9.0,
    "stealth": 7.0,
    "relevance": 8.5,
    "coherence": 9.0,
    "novelty": 7.5,
    "overall": 8.5
  },
  "found_at": "2026-01-08T12:20:00Z"
}
```

#### `GET /api/vulnerabilities/by-experiment/{experiment_id}`

Get all vulnerabilities for a specific experiment.

**Authentication**: Required

**Response**: Same format as `GET /api/vulnerabilities`

---

### Results

#### `GET /api/results/{experiment_id}`

Get experiment results and summary.

**Authentication**: Required

**Response**:
```json
{
  "experiment_id": "uuid-here",
  "status": "completed",
  "total_iterations": 44,
  "completed_iterations": 44,
  "vulnerabilities_found": 12,
  "severity_breakdown": {
    "critical": 2,
    "high": 4,
    "medium": 5,
    "low": 1
  },
  "strategies_tested": ["roleplay_injection", "obfuscation_base64"],
  "completed_at": "2026-01-08T13:00:00Z"
}
```

#### `GET /api/results/{experiment_id}/export`

Export experiment results in various formats.

**Authentication**: Required

**Query Parameters**:
- `format` (optional): Export format (`json`, `csv`, `pdf`) - default: `json`

**Response**: File download or JSON data depending on format

---

### WebSocket

#### `WS /ws/scan/{experiment_id}`

Real-time progress updates via WebSocket.

**Authentication**: Not required (experiment ID serves as access control)

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:9000/ws/scan/{experiment_id}');
```

**Message Format**:
```json
{
  "type": "progress",
  "experiment_id": "uuid-here",
  "iteration": 15,
  "total_iterations": 44,
  "progress": 0.34,
  "vulnerabilities_found": 3,
  "timestamp": "2026-01-08T12:15:00Z"
}
```

**Event Types**:
- `progress`: Iteration update
- `vulnerability_found`: New vulnerability detected
- `experiment_complete`: Experiment finished
- `error`: Error occurred

---

## Demo Mode Endpoints

When `DEMO_MODE=true`, the following endpoints provide read-only mock data:

### `GET /api/demo/experiments`

Returns mock experiment list (read-only).

**Authentication**: Not required

**Response**: Same format as `GET /api/experiments` but with static mock data

### `POST /api/demo/experiments`

Returns 403 Forbidden with deployment instructions.

**Response**:
```json
{
  "error": "Demo mode is read-only",
  "message": "Deploy locally to create experiments",
  "docs_url": "https://github.com/Leviticus-Triage/cerebro-red-v2#quick-start"
}
```

---

## Error Handling

### Standard Error Format

```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "detail": "Additional error details (debug mode only)",
  "timestamp": "2026-01-08T12:00:00Z"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request data or parameters
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Operation not allowed (e.g., write in demo mode)
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service unhealthy

### Rate Limiting

Default rate limit: **60 requests per minute per IP address**

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

---

## Auto-Generated API Documentation

The complete OpenAPI 3.1.0 specification is available at:

- **Interactive Docs**: `http://localhost:9000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:9000/redoc`
- **OpenAPI JSON**: `http://localhost:9000/openapi.json`

The OpenAPI schema is automatically generated from FastAPI route definitions and includes:
- All endpoint paths and methods
- Request/response schemas
- Authentication requirements
- Example payloads
- Error responses

---

**Next Steps**:
- See [User Guide](user-guide.md) for usage examples
- Read [Configuration Guide](configuration.md) for API key setup
- Check [Deployment Guide](deployment.md) for production configuration
