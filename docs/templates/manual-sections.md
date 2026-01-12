# Manual API Documentation Sections

This file contains manual documentation sections that are merged into the auto-generated API reference.
Sections are identified by Markdown headers and inserted at appropriate locations.

## Authentication

Cerebro-Red v2 API uses API key authentication. Include your API key in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

To obtain an API key:
1. Configure `API_KEY` in your [.env](.env) file
2. Or contact your system administrator for production keys

**Example Request:**

```bash
curl -X GET http://localhost:9000/api/v1/experiments \
  -H "X-API-Key: your-api-key-here"
```

**Python Example:**

```python
import requests

headers = {
    "X-API-Key": "your-api-key-here"
}

response = requests.get(
    "http://localhost:9000/api/v1/experiments",
    headers=headers
)
print(response.json())
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:9000/api/v1/experiments', {
  headers: {
    'X-API-Key': 'your-api-key-here'
  }
});

const data = await response.json();
console.log(data);
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Default:** 100 requests per minute per API key
- **Burst:** Up to 20 requests in a 10-second window

**Rate Limit Headers:**

All responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**Rate Limit Exceeded:**

When you exceed the rate limit, you'll receive a `429` response:

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 60 seconds."
  }
}
```

Headers:
```
Retry-After: 60
X-RateLimit-Remaining: 0
```

---

## Error Responses

All error responses follow a consistent format:

**Error Schema:**

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

**Common Error Codes:**

- `400` - Bad Request: Invalid input parameters
- `401` - Unauthorized: Missing or invalid API key
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource does not exist
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server-side error
- `503` - Service Unavailable: Server is temporarily unavailable

**Error Response Example:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid experiment configuration",
    "details": {
      "field": "target_model",
      "reason": "Model not found"
    }
  }
}
```

---

## WebSocket

Cerebro-Red v2 provides real-time progress updates via WebSocket connections.

**Connection URL:**

```
ws://localhost:9000/ws/experiments/{experiment_id}
```

**Message Types:**

### Progress Update

Sent when experiment progress changes:

```json
{
  "type": "progress",
  "experiment_id": "exp_123",
  "current_iteration": 5,
  "total_iterations": 20,
  "progress_percent": 25,
  "status": "running"
}
```

### Iteration Complete

Sent when an iteration completes:

```json
{
  "type": "iteration_complete",
  "experiment_id": "exp_123",
  "iteration": 5,
  "result": {
    "success": true,
    "score": 7.5,
    "vulnerability_detected": true
  }
}
```

### Experiment Complete

Sent when experiment finishes:

```json
{
  "type": "experiment_complete",
  "experiment_id": "exp_123",
  "status": "completed",
  "summary": {
    "total_iterations": 20,
    "successful": 18,
    "vulnerabilities_found": 3
  }
}
```

**JavaScript Example:**

```javascript
const experimentId = 'exp_123';
const ws = new WebSocket(`ws://localhost:9000/ws/experiments/${experimentId}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'progress':
      console.log(`Progress: ${message.progress_percent}%`);
      break;
    case 'iteration_complete':
      console.log(`Iteration ${message.iteration} complete`);
      break;
    case 'experiment_complete':
      console.log('Experiment finished!', message.summary);
      ws.close();
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
};
```

**Python Example:**

```python
import asyncio
import websockets
import json

async def monitor_experiment(experiment_id: str):
    uri = f"ws://localhost:9000/ws/experiments/{experiment_id}"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'progress':
                print(f"Progress: {data['progress_percent']}%")
            elif data['type'] == 'iteration_complete':
                print(f"Iteration {data['iteration']} complete")
            elif data['type'] == 'experiment_complete':
                print('Experiment finished!', data['summary'])
                break

# Run
asyncio.run(monitor_experiment('exp_123'))
```

---

## Use Cases

### Creating and Monitoring an Experiment

**Step 1: Create Experiment**

```bash
curl -X POST http://localhost:9000/api/v1/experiments \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-llama2",
    "target_model": "llama2",
    "target_provider": "ollama",
    "strategies": ["aim_jailbreak", "few_shot_hijacking"],
    "payload_count": 20
  }'
```

**Step 2: Connect WebSocket for Real-Time Updates**

```javascript
const ws = new WebSocket('ws://localhost:9000/ws/experiments/exp_123');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Update:', update);
};
```

**Step 3: Retrieve Results**

```bash
curl http://localhost:9000/api/v1/experiments/exp_123/results \
  -H "X-API-Key: your-api-key"
```

### Exporting Results

**Export as JSON:**

```bash
curl http://localhost:9000/api/v1/experiments/exp_123/results?format=json \
  -H "X-API-Key: your-api-key" \
  -o results.json
```

**Export as CSV:**

```bash
curl http://localhost:9000/api/v1/experiments/exp_123/results?format=csv \
  -H "X-API-Key: your-api-key" \
  -o results.csv
```

### Using Templates

**List Available Templates:**

```bash
curl http://localhost:9000/api/v1/templates \
  -H "X-API-Key: your-api-key"
```

**Create Experiment from Template:**

```bash
curl -X POST http://localhost:9000/api/v1/experiments/from-template \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "tpl_abc123",
    "name": "my-experiment",
    "target_model": "gpt-4"
  }'
```

---
