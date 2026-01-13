# CEREBRO-RED v2 API

**Version:** 2.0.0


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
    

**Last Updated:** 2026-01-13

---

## Table of Contents

- [Templates](#templates)
  - [`POST /api/v1/templates`](#templates-post--api-v1-templates)
  - [`GET /api/v1/templates`](#templates-get--api-v1-templates)
  - [`GET /api/v1/templates/jailbreak`](#templates-get--api-v1-templates-jailbreak)
  - [`GET /api/v1/templates/jailbreak/backups`](#templates-get--api-v1-templates-jailbreak-backups)
  - [`GET /api/v1/templates/jailbreak/categories`](#templates-get--api-v1-templates-jailbreak-categories)
  - [`GET /api/v1/templates/jailbreak/export`](#templates-get--api-v1-templates-jailbreak-export)
  - [`POST /api/v1/templates/jailbreak/import`](#templates-post--api-v1-templates-jailbreak-import)
  - [`GET /api/v1/templates/jailbreak/repositories`](#templates-get--api-v1-templates-jailbreak-repositories)
  - [`POST /api/v1/templates/jailbreak/repositories`](#templates-post--api-v1-templates-jailbreak-repositories)
  - [`GET /api/v1/templates/jailbreak/repositories/{repo_name}`](#templates-get--api-v1-templates-jailbreak-repositories-repo_name)
  - [`PUT /api/v1/templates/jailbreak/repositories/{repo_name}`](#templates-put--api-v1-templates-jailbreak-repositories-repo_name)
  - [`DELETE /api/v1/templates/jailbreak/repositories/{repo_name}`](#templates-delete--api-v1-templates-jailbreak-repositories-repo_name)
  - [`GET /api/v1/templates/jailbreak/repositories/{repo_name}/history`](#templates-get--api-v1-templates-jailbreak-repositories-repo_name-history)
  - [`POST /api/v1/templates/jailbreak/restore`](#templates-post--api-v1-templates-jailbreak-restore)
  - [`GET /api/v1/templates/jailbreak/status`](#templates-get--api-v1-templates-jailbreak-status)
  - [`POST /api/v1/templates/jailbreak/update`](#templates-post--api-v1-templates-jailbreak-update)
  - [`GET /api/v1/templates/jailbreak/{category}`](#templates-get--api-v1-templates-jailbreak-category)
  - [`POST /api/v1/templates/jailbreak/{category}`](#templates-post--api-v1-templates-jailbreak-category)
  - [`DELETE /api/v1/templates/jailbreak/{category}`](#templates-delete--api-v1-templates-jailbreak-category)
  - [`PUT /api/v1/templates/jailbreak/{category}/{template_index}`](#templates-put--api-v1-templates-jailbreak-category-template_index)
  - [`DELETE /api/v1/templates/jailbreak/{category}/{template_index}`](#templates-delete--api-v1-templates-jailbreak-category-template_index)
  - [`GET /api/v1/templates/{template_id}`](#templates-get--api-v1-templates-template_id)
  - [`PUT /api/v1/templates/{template_id}`](#templates-put--api-v1-templates-template_id)
  - [`DELETE /api/v1/templates/{template_id}`](#templates-delete--api-v1-templates-template_id)
  - [`POST /api/v1/templates/{template_id}/use`](#templates-post--api-v1-templates-template_id-use)
- [debug](#debug)
  - [`POST /api/v1/debug/force-error`](#debug-post--api-v1-debug-force-error)
  - [`GET /api/v1/debug/test-logging`](#debug-get--api-v1-debug-test-logging)
- [experiments](#experiments)
  - [`POST /api/v1/experiments`](#experiments-post--api-v1-experiments)
  - [`GET /api/v1/experiments`](#experiments-get--api-v1-experiments)
  - [`GET /api/v1/experiments/{experiment_id}`](#experiments-get--api-v1-experiments-experiment_id)
  - [`PUT /api/v1/experiments/{experiment_id}`](#experiments-put--api-v1-experiments-experiment_id)
  - [`DELETE /api/v1/experiments/{experiment_id}`](#experiments-delete--api-v1-experiments-experiment_id)
  - [`GET /api/v1/experiments/{experiment_id}/iterations`](#experiments-get--api-v1-experiments-experiment_id-iterations)
  - [`POST /api/v1/experiments/{experiment_id}/repeat`](#experiments-post--api-v1-experiments-experiment_id-repeat)
  - [`GET /api/v1/experiments/{experiment_id}/statistics`](#experiments-get--api-v1-experiments-experiment_id-statistics)
- [other](#other)
  - [`GET /`](#other-get--)
  - [`GET /health`](#other-get--health)
  - [`GET /health/circuit-breakers`](#other-get--health-circuit-breakers)
  - [`GET /metrics`](#other-get--metrics)
- [results](#results)
  - [`GET /api/v1/results/{experiment_id}`](#results-get--api-v1-results-experiment_id)
  - [`GET /api/v1/results/{experiment_id}/export`](#results-get--api-v1-results-experiment_id-export)
  - [`GET /api/v1/results/{experiment_id}/iterations/{iteration_id}`](#results-get--api-v1-results-experiment_id-iterations-iteration_id)
  - [`GET /api/v1/results/{experiment_id}/summary`](#results-get--api-v1-results-experiment_id-summary)
- [scans](#scans)
  - [`POST /api/v1/scan/batch`](#scans-post--api-v1-scan-batch)
  - [`POST /api/v1/scan/start`](#scans-post--api-v1-scan-start)
  - [`GET /api/v1/scan/status/{experiment_id}`](#scans-get--api-v1-scan-status-experiment_id)
  - [`POST /api/v1/scan/{experiment_id}/cancel`](#scans-post--api-v1-scan-experiment_id-cancel)
  - [`POST /api/v1/scan/{experiment_id}/pause`](#scans-post--api-v1-scan-experiment_id-pause)
  - [`POST /api/v1/scan/{experiment_id}/resume`](#scans-post--api-v1-scan-experiment_id-resume)
- [telemetry](#telemetry)
  - [`GET /api/v1/telemetry/logs/{experiment_id}`](#telemetry-get--api-v1-telemetry-logs-experiment_id)
  - [`GET /api/v1/telemetry/stats`](#telemetry-get--api-v1-telemetry-stats)
  - [`GET /api/v1/telemetry/stats/{experiment_id}`](#telemetry-get--api-v1-telemetry-stats-experiment_id)
- [vulnerabilities](#vulnerabilities)
  - [`GET /api/v1/vulnerabilities`](#vulnerabilities-get--api-v1-vulnerabilities)
  - [`GET /api/v1/vulnerabilities/by-experiment/{experiment_id}`](#vulnerabilities-get--api-v1-vulnerabilities-by-experiment-experiment_id)
  - [`GET /api/v1/vulnerabilities/by-severity/{severity}`](#vulnerabilities-get--api-v1-vulnerabilities-by-severity-severity)
  - [`GET /api/v1/vulnerabilities/statistics`](#vulnerabilities-get--api-v1-vulnerabilities-statistics)
  - [`GET /api/v1/vulnerabilities/{vulnerability_id}`](#vulnerabilities-get--api-v1-vulnerabilities-vulnerability_id)
- [{provider}](#{provider})
  - [`POST /health/circuit-breakers/{provider}/reset`](#{provider}-post--health-circuit-breakers-provider-reset)

---

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

---

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

---

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

---

---

## Templates

### `POST /api/v1/templates`

**Create Template**

Create a new experiment template.

Saves the complete ExperimentConfig as a reusable template.

 **Authentication Required:** API Key

**Request Body:** See schema [`ExperimentTemplateCreate`](#schema-experimenttemplatecreate)

**Responses:**

**201** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/templates" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
data = {
}
response = requests.post(url, headers=headers, json=data)
print(response.json())
```
</details>

---

### `GET /api/v1/templates`

**List Templates**

List all experiment templates with pagination and filters.

 **Authentication Required:** API Key

**Query Parameters:**
- `page` (integer) (default: `1`): Page number
- `page_size` (integer) (default: `20`): Items per page
- `is_public` (string): Filter by public/private
- `created_by` (string): Filter by creator
- `tags` (string): Comma-separated tags to filter

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "page": 1,
    "page_size": 20,
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak`

**List Jailbreak Templates**

List all jailbreak templates from advanced_payloads.json.

Returns:
    Dictionary with categories and their templates

 **Authentication Required:** API Key

**Query Parameters:**
- `category` (string): Filter by category
- `search` (string): Search in template content

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  http://localhost:9000/api/v1/templates/jailbreak?category=value&search=value" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "category": "value",
    "search": "value",
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/backups`

**List Jailbreak Backups**

List all available backup files.

Returns:
    List of backup files with metadata

 **Authentication Required:** API Key

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates/jailbreak/backups" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/backups"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/categories`

**List Jailbreak Categories**

List all jailbreak template categories.

Returns:
    List of category names with metadata

 **Authentication Required:** API Key

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates/jailbreak/categories" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/categories"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/export`

**Export Jailbreak Templates**

Export jailbreak templates as JSON.

Returns:
    JSON string of all templates or specific category

 **Authentication Required:** API Key

**Query Parameters:**
- `category` (string): Export specific category only

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  http://localhost:9000/api/v1/templates/jailbreak/export?category=value" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/export"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "category": "value",
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `POST /api/v1/templates/jailbreak/import`

**Import Jailbreak Templates**

Import jailbreak templates from JSON.

Args:
    file_content: JSON string containing templates
    merge: If True, merge with existing. If False, replace.

 **Authentication Required:** API Key

**Query Parameters:**
- `file_content` (string) *(required)*: JSON content to import
- `merge` (boolean) (default: `True`): Merge with existing templates instead of replacing

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  http://localhost:9000/api/v1/templates/jailbreak/import?file_content=value&merge=True" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/import"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "file_content": "value",
    "merge": True,
}
response = requests.post(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/repositories`

**List Template Repositories**

List all configured template repositories.

Returns:
    Dictionary with all repository configurations

 **Authentication Required:** API Key

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates/jailbreak/repositories" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/repositories"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/templates/jailbreak/repositories`

**Add Template Repository**

Add a new repository configuration.

Args:
    repo_config: Repository configuration with:
        - name: str (required)
        - url: str (required)
        - path: str (required)
        - extraction_script: Optional[str]
        - categories: List[str]
        - license: str
        - source: str
        
Returns:
    Success status and repository name

 **Authentication Required:** API Key

**Request Body (application/json):**

```json
{}
```

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/templates/jailbreak/repositories" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/repositories"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
data = {
}
response = requests.post(url, headers=headers, json=data)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/repositories/{repo_name}`

**Get Template Repository**

Get a specific repository configuration.

Args:
    repo_name: Name of repository
    
Returns:
    Repository configuration

 **Authentication Required:** API Key

**Path Parameters:**
- `repo_name` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates/jailbreak/repositories/example-repo_name" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

repo_name = "example_repo_name"
url = f"http://localhost:9000/api/v1/templates/jailbreak/repositories/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `PUT /api/v1/templates/jailbreak/repositories/{repo_name}`

**Update Template Repository**

Update an existing repository configuration.

Args:
    repo_name: Name of repository to update
    repo_config: Updated repository configuration
    
Returns:
    Success status

 **Authentication Required:** API Key

**Path Parameters:**
- `repo_name` (string) *(required)*: No description

**Request Body (application/json):**

```json
{}
```

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X PUT \
  "http://localhost:9000/api/v1/templates/jailbreak/repositories/example-repo_name" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

repo_name = "example_repo_name"
url = f"http://localhost:9000/api/v1/templates/jailbreak/repositories/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
data = {
}
response = requests.put(url, headers=headers, json=data)
print(response.json())
```
</details>

---

### `DELETE /api/v1/templates/jailbreak/repositories/{repo_name}`

**Delete Template Repository**

Delete a repository configuration.

Args:
    repo_name: Name of repository to delete
    
Returns:
    Success status

 **Authentication Required:** API Key

**Path Parameters:**
- `repo_name` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X DELETE \
  "http://localhost:9000/api/v1/templates/jailbreak/repositories/example-repo_name" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

repo_name = "example_repo_name"
url = f"http://localhost:9000/api/v1/templates/jailbreak/repositories/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.delete(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/repositories/{repo_name}/history`

**Get Repository Update History**

Get update history for a specific repository.

Args:
    repo_name: Name of repository
    limit: Maximum number of entries to return
    
Returns:
    List of update history entries

 **Authentication Required:** API Key

**Path Parameters:**
- `repo_name` (string) *(required)*: No description

**Query Parameters:**
- `limit` (integer) (default: `100`): No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  http://localhost:9000/api/v1/templates/jailbreak/repositories/example-repo_name/history?limit=100" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

repo_name = "example_repo_name"
url = f"http://localhost:9000/api/v1/templates/jailbreak/repositories/{param_name}/history"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "limit": 100,
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `POST /api/v1/templates/jailbreak/restore`

**Restore Jailbreak Templates**

Restore jailbreak templates from a backup file.

Args:
    backup_path: Path to backup file (relative to data directory or absolute)

 **Authentication Required:** API Key

**Query Parameters:**
- `backup_path` (string) *(required)*: Path to backup file to restore from

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  http://localhost:9000/api/v1/templates/jailbreak/restore?backup_path=value" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/restore"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "backup_path": "value",
}
response = requests.post(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/status`

**Get Jailbreak Template Status**

Get status of external repositories (last update, commit hash, etc.).

Returns:
    Repository status information including:
    - Repository existence
    - Last commit hash
    - Last commit date
    - Current branch

 **Authentication Required:** API Key

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates/jailbreak/status" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/status"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/templates/jailbreak/update`

**Update Jailbreak Templates**

Update jailbreak templates from external repositories.

This endpoint:
- Updates specified repository (or all repositories if none specified)
- Extracts templates from updated repositories
- Merges templates into advanced_payloads.json
- Creates backup before update (if create_backup=True)

Args:
    repository: Optional repository name to update. If None, updates all.
    create_backup: Whether to create backup before update
    
Returns:
    Update results with templates added/updated counts

 **Authentication Required:** API Key

**Query Parameters:**
- `repository` (string): Specific repository to update (PyRIT, L1B3RT4S, LLAMATOR, Model-Inversion-Attack-ToolBox). If None, updates all.
- `create_backup` (boolean) (default: `True`): Create backup before update

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  http://localhost:9000/api/v1/templates/jailbreak/update?repository=value&create_backup=True" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/templates/jailbreak/update"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "repository": "value",
    "create_backup": True,
}
response = requests.post(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/jailbreak/{category}`

**Get Jailbreak Category**

Get all templates for a specific category.

Returns:
    Category data with all templates

 **Authentication Required:** API Key

**Path Parameters:**
- `category` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates/jailbreak/example-category" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

category = "example_category"
url = f"http://localhost:9000/api/v1/templates/jailbreak/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/templates/jailbreak/{category}`

**Add Jailbreak Template**

Add a new template to a category.

Creates category if it doesn't exist.

 **Authentication Required:** API Key

**Path Parameters:**
- `category` (string) *(required)*: No description

**Query Parameters:**
- `template` (string) *(required)*: Template string to add

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  http://localhost:9000/api/v1/templates/jailbreak/example-category?template=value" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

category = "example_category"
url = f"http://localhost:9000/api/v1/templates/jailbreak/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "template": "value",
}
response = requests.post(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `DELETE /api/v1/templates/jailbreak/{category}`

**Delete Jailbreak Category**

Delete an entire category.

 **Authentication Required:** API Key

**Path Parameters:**
- `category` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X DELETE \
  "http://localhost:9000/api/v1/templates/jailbreak/example-category" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

category = "example_category"
url = f"http://localhost:9000/api/v1/templates/jailbreak/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.delete(url, headers=headers)
print(response.json())
```
</details>

---

### `PUT /api/v1/templates/jailbreak/{category}/{template_index}`

**Update Jailbreak Template**

Update a template at a specific index in a category.

 **Authentication Required:** API Key

**Path Parameters:**
- `category` (string) *(required)*: No description
- `template_index` (integer) *(required)*: No description

**Query Parameters:**
- `template` (string) *(required)*: Updated template string

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X PUT \
  http://localhost:9000/api/v1/templates/jailbreak/example-category/example-template_index?template=value" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

category = "example_category"
template_index = "example_template_index"
url = f"http://localhost:9000/api/v1/templates/jailbreak/{param_name}/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "template": "value",
}
response = requests.put(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `DELETE /api/v1/templates/jailbreak/{category}/{template_index}`

**Delete Jailbreak Template**

Delete a template from a category.

 **Authentication Required:** API Key

**Path Parameters:**
- `category` (string) *(required)*: No description
- `template_index` (integer) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X DELETE \
  "http://localhost:9000/api/v1/templates/jailbreak/example-category/example-template_index" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

category = "example_category"
template_index = "example_template_index"
url = f"http://localhost:9000/api/v1/templates/jailbreak/{param_name}/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.delete(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/templates/{template_id}`

**Get Template**

Get template by ID.

 **Authentication Required:** API Key

**Path Parameters:**
- `template_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/templates/example-template_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

template_id = "example_template_id"
url = f"http://localhost:9000/api/v1/templates/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `PUT /api/v1/templates/{template_id}`

**Update Template**

Update template.

 **Authentication Required:** API Key

**Path Parameters:**
- `template_id` (string) *(required)*: No description

**Request Body:** See schema [`ExperimentTemplateUpdate`](#schema-experimenttemplateupdate)

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X PUT \
  "http://localhost:9000/api/v1/templates/example-template_id" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

template_id = "example_template_id"
url = f"http://localhost:9000/api/v1/templates/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
data = {
}
response = requests.put(url, headers=headers, json=data)
print(response.json())
```
</details>

---

### `DELETE /api/v1/templates/{template_id}`

**Delete Template**

Delete template.

 **Authentication Required:** API Key

**Path Parameters:**
- `template_id` (string) *(required)*: No description

**Responses:**

**204** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X DELETE \
  "http://localhost:9000/api/v1/templates/example-template_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

template_id = "example_template_id"
url = f"http://localhost:9000/api/v1/templates/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.delete(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/templates/{template_id}/use`

**Use Template**

Increment usage count and return template config.

This endpoint is called when a user loads a template into the experiment form.

 **Authentication Required:** API Key

**Path Parameters:**
- `template_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/templates/example-template_id/use" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

template_id = "example_template_id"
url = f"http://localhost:9000/api/v1/templates/{param_name}/use"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.post(url, headers=headers)
print(response.json())
```
</details>

---

## debug

### `POST /api/v1/debug/force-error`

**Force Error**

Force an error for testing traceback logging.

Args:
    error_type: Type of error to raise (generic, value, key, type, zero_division)
    
Available in all environments for testing purposes.

**Query Parameters:**
- `error_type` (string) (default: `generic`): No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  http://localhost:9000/api/v1/debug/force-error?error_type=generic"
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/debug/force-error"
params = {
    "error_type": "generic",
}
response = requests.post(url, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/debug/test-logging`

**Test Logging**

Test all logging levels to verify configuration.

Available in all environments for testing purposes.

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/debug/test-logging"
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/debug/test-logging"
response = requests.get(url)
print(response.json())
```
</details>

---

## experiments

### `POST /api/v1/experiments`

**Create Experiment**

Create a new experiment with enhanced error logging.

 **Authentication Required:** API Key

**Request Body:** See schema [`ExperimentConfig`](#schema-experimentconfig)

**Responses:**

**201** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/experiments" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/experiments"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
data = {
}
response = requests.post(url, headers=headers, json=data)
print(response.json())
```
</details>

---

### `GET /api/v1/experiments`

**List Experiments**

List all experiments with pagination.

 **Authentication Required:** API Key

**Query Parameters:**
- `page` (integer) (default: `1`): Page number
- `page_size` (integer) (default: `20`): Items per page

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  http://localhost:9000/api/v1/experiments?page=1&page_size=20" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/experiments"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "page": 1,
    "page_size": 20,
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/experiments/{experiment_id}`

**Get Experiment**

Get experiment details by ID.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/experiments/example-experiment_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/experiments/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `PUT /api/v1/experiments/{experiment_id}`

**Update Experiment**

Update experiment (only status and metadata allowed).

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Query Parameters:**
- `status_update` (string): No description

**Request Body (application/json):**

```json
{}
```

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X PUT \
  http://localhost:9000/api/v1/experiments/example-experiment_id?status_update=value" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/experiments/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
params = {
    "status_update": "value",
}
data = {
}
response = requests.put(url, headers=headers, params=params, json=data)
print(response.json())
```
</details>

---

### `DELETE /api/v1/experiments/{experiment_id}`

**Delete Experiment**

Delete an experiment.

First cancels any running task, then deletes the experiment from database.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**204** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X DELETE \
  "http://localhost:9000/api/v1/experiments/example-experiment_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/experiments/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.delete(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/experiments/{experiment_id}/iterations`

**Get Experiment Iterations**

Get all iterations for an experiment with FULL details.

Returns complete iteration data including:
- Original and mutated prompts
- Target response
- Judge score and reasoning
- Latency and metadata

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/experiments/example-experiment_id/iterations" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/experiments/{param_name}/iterations"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/experiments/{experiment_id}/repeat`

**Repeat Experiment**

Repeat (duplicate) an existing experiment with the same configuration.

Creates a new experiment with:
- Same configuration (models, prompts, strategies, etc.)
- New experiment_id
- Name appended with " (Repeat)" or timestamp
- Status set to "pending"

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**201** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/experiments/example-experiment_id/repeat" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/experiments/{param_name}/repeat"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.post(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/experiments/{experiment_id}/statistics`

**Get Experiment Statistics**

Get experiment statistics.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/experiments/example-experiment_id/statistics" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/experiments/{param_name}/statistics"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

## other

### `GET /`

**Root**

Root endpoint.

Returns:
    dict: API information (automatically wrapped by middleware)

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/"
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/"
response = requests.get(url)
print(response.json())
```
</details>

---

### `GET /health`

**Health Check**

Comprehensive health check endpoint.

Returns:
    - status: "healthy" | "degraded" | "unhealthy"
    - components: Status of each component (database, LLM providers, telemetry)
    - version: API version
    - timestamp: Current timestamp
    
Note: Response is automatically wrapped in {data: ...} by middleware.

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/health"
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/health"
response = requests.get(url)
print(response.json())
```
</details>

---

### `GET /health/circuit-breakers`

**Get Circuit Breaker Stats**

Get circuit breaker statistics for all providers.

Returns:
    Dictionary with circuit breaker stats per provider including:
    - State (closed/open/half_open)
    - Failure/success counts
    - Error type distribution (transient/permanent)
    - Failure rate
    - Circuit breaker configuration

 **Authentication Required:** API Key

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/health/circuit-breakers" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/health/circuit-breakers"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /metrics`

**Prometheus Metrics**

Prometheus-compatible metrics endpoint.

Returns metrics in Prometheus text format.
No authentication required for monitoring systems.

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/metrics"
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/metrics"
response = requests.get(url)
print(response.json())
```
</details>

---

## results

### `GET /api/v1/results/{experiment_id}`

**Get Experiment Results**

Get complete experiment results including all iterations and vulnerabilities.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/results/example-experiment_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/results/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/results/{experiment_id}/export`

**Export Experiment Results**

Export experiment results in specified format (JSON, CSV, or PDF).

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Query Parameters:**
- `format` (string) (default: `json`): No description
- `include_prompts` (boolean) (default: `True`): No description
- `include_responses` (boolean) (default: `True`): No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/results/example-experiment_id/export" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/results/{param_name}/export"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "format": "json",
    "include_prompts": True,
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/results/{experiment_id}/iterations/{iteration_id}`

**Get Iteration Details**

Get detailed information for a specific iteration.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description
- `iteration_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/results/example-experiment_id/iterations/example-iteration_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
iteration_id = "example_iteration_id"
url = f"http://localhost:9000/api/v1/results/{param_name}/iterations/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/results/{experiment_id}/summary`

**Get Experiment Summary**

Get compact experiment result summary.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/results/example-experiment_id/summary" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/results/{param_name}/summary"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

## scans

### `POST /api/v1/scan/batch`

**Start Batch Scan**

Start batch scan (multiple experiments in parallel).

Each experiment in the request is executed independently with its own config and prompts.
Experiments run concurrently using asyncio.create_task within a single background task.

 **Authentication Required:** API Key

**Request Body:** See schema [`BatchScanRequest`](#schema-batchscanrequest)

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/scan/batch" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/scan/batch"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
data = {
}
response = requests.post(url, headers=headers, json=data)
print(response.json())
```
</details>

---

### `POST /api/v1/scan/start`

**Start Scan**

Start a new scan (experiment execution).

Runs experiment in background and returns immediately with experiment_id.
Use WebSocket endpoint or status endpoint to track progress.

 **Authentication Required:** API Key

**Request Body:** See schema [`ScanStartRequest`](#schema-scanstartrequest)

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/scan/start" \
  -H 'X-API-Key: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{}'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/scan/start"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
}
data = {
}
response = requests.post(url, headers=headers, json=data)
print(response.json())
```
</details>

---

### `GET /api/v1/scan/status/{experiment_id}`

**Get Scan Status**

Get current scan status and progress.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/scan/status/example-experiment_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/scan/status/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/scan/{experiment_id}/cancel`

**Cancel Scan**

Cancel a running scan.

Immediately cancels the running task and updates status to FAILED.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/scan/example-experiment_id/cancel" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/scan/{param_name}/cancel"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.post(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/scan/{experiment_id}/pause`

**Pause Scan**

Pause a running scan.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/scan/example-experiment_id/pause" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/scan/{param_name}/pause"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.post(url, headers=headers)
print(response.json())
```
</details>

---

### `POST /api/v1/scan/{experiment_id}/resume`

**Resume Scan**

Resume a paused scan.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/api/v1/scan/example-experiment_id/resume" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/scan/{param_name}/resume"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.post(url, headers=headers)
print(response.json())
```
</details>

---

## telemetry

### `GET /api/v1/telemetry/logs/{experiment_id}`

**Get Experiment Logs**

Get audit logs for a specific experiment.

Returns JSONL-formatted log entries.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/telemetry/logs/example-experiment_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/telemetry/logs/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/telemetry/stats`

**Get Telemetry Stats**

Get aggregate telemetry statistics.

 **Authentication Required:** API Key

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/telemetry/stats" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/telemetry/stats"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/telemetry/stats/{experiment_id}`

**Get Experiment Telemetry Stats**

Get experiment-specific telemetry statistics.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/telemetry/stats/example-experiment_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/telemetry/stats/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

## vulnerabilities

### `GET /api/v1/vulnerabilities`

**List Vulnerabilities**

List all vulnerabilities with optional filtering.

 **Authentication Required:** API Key

**Query Parameters:**
- `severity` (string): Filter by severity
- `experiment_id` (string): Filter by experiment
- `strategy` (string): Filter by attack strategy
- `limit` (integer) (default: `100`): Maximum results
- `offset` (integer) (default: `0`): Offset for pagination

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/vulnerabilities" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/vulnerabilities"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "severity": "value",
    "experiment_id": "value",
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/vulnerabilities/by-experiment/{experiment_id}`

**Get Vulnerabilities By Experiment**

Get all vulnerabilities for a specific experiment.

 **Authentication Required:** API Key

**Path Parameters:**
- `experiment_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/vulnerabilities/by-experiment/example-experiment_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

experiment_id = "example_experiment_id"
url = f"http://localhost:9000/api/v1/vulnerabilities/by-experiment/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/vulnerabilities/by-severity/{severity}`

**Get Vulnerabilities By Severity**

Get vulnerabilities filtered by severity level.

 **Authentication Required:** API Key

**Path Parameters:**
- `severity` (string) *(required)*: No description

**Query Parameters:**
- `limit` (integer) (default: `100`): No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  http://localhost:9000/api/v1/vulnerabilities/by-severity/example-severity?limit=100" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

severity = "example_severity"
url = f"http://localhost:9000/api/v1/vulnerabilities/by-severity/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
params = {
    "limit": 100,
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```
</details>

---

### `GET /api/v1/vulnerabilities/statistics`

**Get Vulnerability Statistics**

Get aggregated vulnerability statistics.

 **Authentication Required:** API Key

**Responses:**

**200** - Successful Response

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/vulnerabilities/statistics" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

url = "http://localhost:9000/api/v1/vulnerabilities/statistics"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

### `GET /api/v1/vulnerabilities/{vulnerability_id}`

**Get Vulnerability**

Get detailed vulnerability information.

 **Authentication Required:** API Key

**Path Parameters:**
- `vulnerability_id` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X GET \
  "http://localhost:9000/api/v1/vulnerabilities/example-vulnerability_id" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

vulnerability_id = "example_vulnerability_id"
url = f"http://localhost:9000/api/v1/vulnerabilities/{param_name}"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.get(url, headers=headers)
print(response.json())
```
</details>

---

## {provider}

### `POST /health/circuit-breakers/{provider}/reset`

**Reset Circuit Breaker Endpoint**

Reset circuit breaker for a specific provider.

Args:
    provider: LLM provider name (e.g., "ollama", "openai", "azure")
    
Returns:
    Success message

 **Authentication Required:** API Key

**Path Parameters:**
- `provider` (string) *(required)*: No description

**Responses:**

**200** - Successful Response

**422** - Validation Error

Response schema: [`HTTPValidationError`](#schema-httpvalidationerror)

**Examples:**

<details>
<summary>cURL</summary>

```bash
curl -X POST \
  "http://localhost:9000/health/circuit-breakers/example-provider/reset" \
  -H 'X-API-Key: your-api-key'
```
</details>

<details>
<summary>Python</summary>

```python
import requests

provider = "example_provider"
url = f"http://localhost:9000/health/circuit-breakers/{param_name}/reset"
headers = {
    "X-API-Key": "your-api-key",
}
response = requests.post(url, headers=headers)
print(response.json())
```
</details>

---

## Data Schemas

Common data schemas used across endpoints:

### `AttackStrategyType` {#schema-attackstrategytype}

Attack strategy types for prompt mutation.

Based on OWASP Top 10 for LLM Applications 2025, Microsoft AI Red Team,
NVIDIA garak, PyRIT, and latest research papers.

```json
"string"
```

### `BatchScanRequest` {#schema-batchscanrequest}

Request to start batch scans.

```json
{
  "experiments": [
    {}
  ]
}
```

### `ExperimentConfig` {#schema-experimentconfig}

Experiment configuration model.

```json
{
  "experiment_id": "string",
  "name": "string",
  "description": {},
  "target_model_provider": {},
  "target_model_name": "string",
  "attacker_model_provider": {},
  "attacker_model_name": "string",
  "judge_model_provider": {},
  "judge_model_name": "string",
  "initial_prompts": [
    "string"
  ],
  "strategies": [
    {}
  ],
  "max_iterations": 0,
  "max_concurrent_attacks": 0,
  "success_threshold": 0.0,
  "timeout_seconds": 0,
  "created_at": "string",
  "metadata": {}
}
```

### `ExperimentTemplateCreate` {#schema-experimenttemplatecreate}

Model for creating experiment templates.

```json
{
  "name": "string",
  "description": {},
  "config": {},
  "tags": [
    "string"
  ],
  "is_public": false,
  "created_by": {}
}
```

### `ExperimentTemplateUpdate` {#schema-experimenttemplateupdate}

Model for updating experiment templates.

```json
{
  "name": {},
  "description": {},
  "config": {},
  "tags": {},
  "is_public": {}
}
```

### `HTTPValidationError` {#schema-httpvalidationerror}

```json
{
  "detail": [
    {}
  ]
}
```

### `LLMProvider` {#schema-llmprovider}

LLM provider types.

```json
"string"
```

### `ScanStartRequest` {#schema-scanstartrequest}

Request to start a new scan.

```json
{
  "experiment_config": {}
}
```

### `ValidationError` {#schema-validationerror}

```json
{
  "loc": [
    {}
  ],
  "msg": "string",
  "type": "string"
}
```

### `VulnerabilitySeverity` {#schema-vulnerabilityseverity}

Vulnerability severity levels.

```json
"string"
```

