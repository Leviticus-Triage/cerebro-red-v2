# Template API Documentation

**Version**: 1.0  
**Last Updated**: 2024-12-29  
**Base URL**: `http://localhost:8000/api/templates`

---

## Overview

The Template API allows you to save, load, and manage experiment configurations as reusable templates. This enables quick replication of successful attack patterns and sharing of configurations across experiments.

---

## Authentication

All template endpoints require API key authentication via the `X-API-Key` header:

```bash
-H "X-API-Key: your-api-key-here"
```

**Default Test Key**: `test-api-key` (configured in `.env`)

---

## Endpoints

### 1. List Templates

**GET** `/api/templates`

Retrieve a paginated list of experiment templates with optional tag filtering.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | integer | No | 0 | Number of templates to skip (pagination offset) |
| `limit` | integer | No | 100 | Maximum number of templates to return |
| `tags` | string | No | - | Comma-separated list of tags to filter by |

#### Request Example

```bash
# List all templates
curl http://localhost:8000/api/templates \
  -H "X-API-Key: test-api-key"

# List templates with pagination
curl "http://localhost:8000/api/templates?skip=0&limit=10" \
  -H "X-API-Key: test-api-key"

# Filter by tags
curl "http://localhost:8000/api/templates?tags=jailbreak,advanced" \
  -H "X-API-Key: test-api-key"
```

#### Response Schema

```json
{
  "templates": [
    {
      "template_id": "uuid",
      "name": "string",
      "description": "string",
      "config": {
        "strategies": ["string"],
        "max_iterations": 0,
        "success_threshold": 0.0
      },
      "tags": ["string"],
      "is_public": true,
      "created_by": "string",
      "created_at": "2024-12-29T12:00:00Z",
      "updated_at": "2024-12-29T12:00:00Z",
      "usage_count": 0
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 100
}
```

#### Response Codes

- `200 OK`: Templates retrieved successfully
- `401 Unauthorized`: Missing or invalid API key
- `500 Internal Server Error`: Server error

---

### 2. Get Template by ID

**GET** `/api/templates/{template_id}`

Retrieve a specific template by its UUID.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_id` | UUID | Yes | Unique identifier of the template |

#### Request Example

```bash
curl http://localhost:8000/api/templates/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: test-api-key"
```

#### Response Schema

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Advanced Jailbreak Suite",
  "description": "Comprehensive jailbreak testing with 10 strategies",
  "config": {
    "strategies": [
      "jailbreak_dan",
      "jailbreak_aim",
      "crescendo_attack"
    ],
    "max_iterations": 20,
    "success_threshold": 7.0,
    "max_concurrent_attacks": 2,
    "timeout_seconds": 600
  },
  "tags": ["jailbreak", "advanced", "comprehensive"],
  "is_public": true,
  "created_by": "user@example.com",
  "created_at": "2024-12-29T12:00:00Z",
  "updated_at": "2024-12-29T12:00:00Z",
  "usage_count": 5
}
```

#### Response Codes

- `200 OK`: Template retrieved successfully
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

---

### 3. Create Template

**POST** `/api/templates`

Create a new experiment template.

#### Request Body Schema

```json
{
  "name": "string (required, max 255 chars)",
  "description": "string (optional)",
  "config": {
    "strategies": ["string (required, array of strategy enum values)"],
    "max_iterations": "integer (optional, default: 10)",
    "success_threshold": "float (optional, default: 7.0)",
    "max_concurrent_attacks": "integer (optional, default: 1)",
    "timeout_seconds": "integer (optional, default: 600)",
    "target_model_provider": "string (optional)",
    "target_model_name": "string (optional)",
    "attacker_model_provider": "string (optional)",
    "attacker_model_name": "string (optional)",
    "judge_model_provider": "string (optional)",
    "judge_model_name": "string (optional)"
  },
  "tags": ["string (optional, array of tags)"],
  "is_public": "boolean (optional, default: false)"
}
```

#### Request Example

```bash
curl -X POST http://localhost:8000/api/templates \
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
      "success_threshold": 7.0,
      "max_concurrent_attacks": 2,
      "timeout_seconds": 600
    },
    "tags": ["jailbreak", "advanced", "comprehensive"],
    "is_public": false
  }'
```

#### Response Schema

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Advanced Jailbreak Suite",
  "description": "Comprehensive jailbreak testing with 10 strategies",
  "config": { ... },
  "tags": ["jailbreak", "advanced", "comprehensive"],
  "is_public": false,
  "created_by": "user@example.com",
  "created_at": "2024-12-29T12:00:00Z",
  "updated_at": "2024-12-29T12:00:00Z",
  "usage_count": 0
}
```

#### Response Codes

- `201 Created`: Template created successfully
- `400 Bad Request`: Invalid request body or validation error
- `401 Unauthorized`: Missing or invalid API key
- `422 Unprocessable Entity`: Invalid strategy enum values
- `500 Internal Server Error`: Server error

---

### 4. Update Template

**PUT** `/api/templates/{template_id}`

Update an existing template. Only provided fields will be updated.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_id` | UUID | Yes | Unique identifier of the template |

#### Request Body Schema

```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "config": "object (optional)",
  "tags": ["string (optional)"],
  "is_public": "boolean (optional)"
}
```

#### Request Example

```bash
curl -X PUT http://localhost:8000/api/templates/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "name": "Updated Template Name",
    "description": "Updated description with more details",
    "tags": ["jailbreak", "updated", "production"]
  }'
```

#### Response Schema

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Template Name",
  "description": "Updated description with more details",
  "config": { ... },
  "tags": ["jailbreak", "updated", "production"],
  "is_public": false,
  "created_by": "user@example.com",
  "created_at": "2024-12-29T12:00:00Z",
  "updated_at": "2024-12-29T13:00:00Z",
  "usage_count": 5
}
```

#### Response Codes

- `200 OK`: Template updated successfully
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

---

### 5. Delete Template

**DELETE** `/api/templates/{template_id}`

Delete a template permanently.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_id` | UUID | Yes | Unique identifier of the template |

#### Request Example

```bash
curl -X DELETE http://localhost:8000/api/templates/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: test-api-key"
```

#### Response Schema

```json
{
  "message": "Template deleted successfully",
  "template_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response Codes

- `200 OK`: Template deleted successfully
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

---

### 6. Use Template (Increment Usage Count)

**POST** `/api/templates/{template_id}/use`

Increment the usage count of a template. Call this endpoint when loading a template to track its usage.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_id` | UUID | Yes | Unique identifier of the template |

#### Request Example

```bash
curl -X POST http://localhost:8000/api/templates/550e8400-e29b-41d4-a716-446655440000/use \
  -H "X-API-Key: test-api-key"
```

#### Response Schema

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Advanced Jailbreak Suite",
  "description": "Comprehensive jailbreak testing with 10 strategies",
  "config": { ... },
  "tags": ["jailbreak", "advanced", "comprehensive"],
  "is_public": false,
  "created_by": "user@example.com",
  "created_at": "2024-12-29T12:00:00Z",
  "updated_at": "2024-12-29T12:00:00Z",
  "usage_count": 6
}
```

#### Response Codes

- `200 OK`: Usage count incremented successfully
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

---

## Data Models

### ExperimentTemplateCreate

```typescript
{
  name: string;                    // Required, max 255 chars
  description?: string;            // Optional
  config: {                        // Required
    strategies: string[];          // Required, array of AttackStrategyType enum values
    max_iterations?: number;       // Optional, default: 10
    success_threshold?: number;    // Optional, default: 7.0
    max_concurrent_attacks?: number; // Optional, default: 1
    timeout_seconds?: number;      // Optional, default: 600
    target_model_provider?: string;
    target_model_name?: string;
    attacker_model_provider?: string;
    attacker_model_name?: string;
    judge_model_provider?: string;
    judge_model_name?: string;
  };
  tags?: string[];                 // Optional
  is_public?: boolean;             // Optional, default: false
}
```

### ExperimentTemplateResponse

```typescript
{
  template_id: string;             // UUID
  name: string;
  description: string;
  config: object;                  // Experiment configuration
  tags: string[];
  is_public: boolean;
  created_by: string;
  created_at: string;              // ISO 8601 datetime
  updated_at: string;              // ISO 8601 datetime
  usage_count: number;
}
```

### ExperimentTemplateListResponse

```typescript
{
  templates: ExperimentTemplateResponse[];
  total: number;                   // Total count (after filtering)
  skip: number;                    // Pagination offset
  limit: number;                   // Pagination limit
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Invalid request body or validation error"
}
```

### 401 Unauthorized

```json
{
  "detail": "Missing or invalid API key"
}
```

### 404 Not Found

```json
{
  "detail": "Template not found"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "config", "strategies", 0],
      "msg": "Invalid strategy enum value",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Usage Examples

### Example 1: Create and Use Template

```bash
# 1. Create template
TEMPLATE_ID=$(curl -X POST http://localhost:8000/api/templates \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "name": "Quick Jailbreak Test",
    "config": {
      "strategies": ["jailbreak_dan", "obfuscation_base64"],
      "max_iterations": 5
    },
    "tags": ["quick", "jailbreak"]
  }' | jq -r '.template_id')

# 2. Use template (increment usage count)
curl -X POST http://localhost:8000/api/templates/$TEMPLATE_ID/use \
  -H "X-API-Key: test-api-key"

# 3. Get template config
curl http://localhost:8000/api/templates/$TEMPLATE_ID \
  -H "X-API-Key: test-api-key" | jq '.config'
```

### Example 2: List and Filter Templates

```bash
# List all templates
curl http://localhost:8000/api/templates \
  -H "X-API-Key: test-api-key" | jq '.templates[] | {name, usage_count, tags}'

# Filter by tags
curl "http://localhost:8000/api/templates?tags=jailbreak" \
  -H "X-API-Key: test-api-key" | jq '.templates[] | .name'

# Paginate results
curl "http://localhost:8000/api/templates?skip=10&limit=5" \
  -H "X-API-Key: test-api-key"
```

### Example 3: Update and Delete Template

```bash
# Update template
curl -X PUT http://localhost:8000/api/templates/$TEMPLATE_ID \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "description": "Updated description",
    "tags": ["updated", "production"]
  }'

# Delete template
curl -X DELETE http://localhost:8000/api/templates/$TEMPLATE_ID \
  -H "X-API-Key: test-api-key"
```

---

## Frontend Integration

### React Query Hooks

```typescript
import { useTemplates, useCreateTemplate, useTemplate } from '@/hooks/useTemplates';

// List templates
const { data: templates, isLoading } = useTemplates();

// Get specific template
const { data: template } = useTemplate(templateId);

// Create template
const createMutation = useCreateTemplate();
createMutation.mutate({
  name: "My Template",
  config: { strategies: ["jailbreak_dan"] }
});
```

### Template Selector Component

```typescript
import { TemplateSelector } from '@/components/experiments/TemplateSelector';

<TemplateSelector
  onTemplateSelect={(template) => {
    // Load template config into form
    setFormData({ ...formData, ...template.config });
  }}
/>
```

---

## Database Schema

Templates are stored in the `experiment_templates` table:

```sql
CREATE TABLE experiment_templates (
  template_id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  config_json TEXT NOT NULL,
  tags TEXT,
  is_public BOOLEAN DEFAULT FALSE,
  created_by VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usage_count INTEGER DEFAULT 0
);

CREATE INDEX idx_templates_tags ON experiment_templates(tags);
CREATE INDEX idx_templates_created_at ON experiment_templates(created_at DESC);
CREATE INDEX idx_templates_usage_count ON experiment_templates(usage_count DESC);
```

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider:
- Rate limiting by API key (e.g., 100 requests/minute)
- Template creation limits (e.g., 10 templates/hour per user)
- Usage tracking for billing/analytics

---

## Security Considerations

1. **API Key Authentication**: Always use HTTPS in production and rotate API keys regularly
2. **Input Validation**: All strategy enum values are validated against the backend enum
3. **SQL Injection**: Parameterized queries prevent SQL injection
4. **XSS Prevention**: Template names and descriptions are sanitized
5. **Access Control**: Consider implementing user-based access control for private templates

---

## Troubleshooting

### Common Issues

1. **422 Unprocessable Entity**: Invalid strategy enum value
   - **Solution**: Verify strategy names match backend enum values (see [docs/STRATEGY_FULL_MAPPING.md](./STRATEGY_FULL_MAPPING.md))

2. **404 Not Found**: Template not found
   - **Solution**: Verify template ID is correct and template exists

3. **401 Unauthorized**: Missing or invalid API key
   - **Solution**: Check `X-API-Key` header matches `.env` configuration

4. **Tag Filtering Returns No Results**: Tags don't match
   - **Solution**: Tags are case-sensitive, ensure exact match

---

## Related Documentation

- **Strategy Mapping**: [docs/STRATEGY_FULL_MAPPING.md](./STRATEGY_FULL_MAPPING.md)
- **Attack Strategies**: [docs/ATTACK_STRATEGIES.md](./ATTACK_STRATEGIES.md)
- **Main README**: [README.md](../README.md)
- **OpenAPI Schema**: [docs/openapi.json](./openapi.json)

---

**Last Updated**: 2024-12-29  
**API Version**: 1.0  
**Maintainer**: CEREBRO-RED Development Team
