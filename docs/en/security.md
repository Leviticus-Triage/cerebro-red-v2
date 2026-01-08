# Security Guide

[🇬🇧 English](security.md) | [🇩🇪 Deutsch](../de/README.md)

Security considerations and best practices for CEREBRO-RED v2.

## Table of Contents

1. [API Key Management](#api-key-management)
2. [Rate Limiting](#rate-limiting)
3. [Demo Mode Security](#demo-mode-security)
4. [Data Protection](#data-protection)
5. [Production Hardening](#production-hardening)

## API Key Management

### Enabling API Authentication

```bash
# .env file
API_KEY=your-secret-api-key-here
API_KEY_ENABLED=true
```

### Usage

All API requests must include `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secret-api-key-here" \
  http://localhost:9000/api/experiments
```

### Best Practices

1. **Generate Strong Keys**: Use cryptographically secure random strings
   ```bash
   # Generate secure API key
   openssl rand -hex 32
   ```

2. **Rotate Regularly**: Change API keys periodically
3. **Never Commit Keys**: Always use `.env` file (gitignored)
4. **Use Different Keys**: Separate keys for development/production
5. **Monitor Usage**: Log API key usage for anomaly detection

### Disabling for Development

```bash
API_KEY_ENABLED=false
```

**Warning**: Only disable in isolated development environments.

## Rate Limiting

### Configuration

```bash
# Requests per minute per IP
RATE_LIMIT_PER_MINUTE=60
```

### Rate Limit Behavior

- **Default**: 60 requests/minute per IP address
- **Exceeded**: Returns `429 Too Many Requests`
- **Reset**: Automatic after time window expires
- **Bypass**: Not available (security feature)

### Adjusting Limits

**For Development**:
```bash
RATE_LIMIT_PER_MINUTE=1000  # Relaxed for testing
```

**For Production**:
```bash
RATE_LIMIT_PER_MINUTE=60  # Standard protection
```

**For High Traffic**:
```bash
RATE_LIMIT_PER_MINUTE=120  # Increased capacity
```

### Rate Limit Headers

Responses include rate limit information:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

## Demo Mode Security

### Demo Mode Configuration

```bash
DEMO_MODE=true
```

### Security Features

1. **Read-Only Operations**: GET requests return mock data
2. **Write Protection**: POST/PUT/DELETE return 403 Forbidden
3. **No Database Access**: Demo API serves static mock data
4. **No LLM Queries**: Prevents resource abuse
5. **Guided Tour**: Frontend shows interactive demo

### Demo Mode Endpoints

**Allowed** (Read-Only):
- `GET /api/demo/experiments` - List mock experiments
- `GET /api/demo/experiments/{id}` - Get mock experiment
- `GET /api/demo/vulnerabilities` - List mock vulnerabilities

**Blocked** (Write Operations):
- `POST /api/demo/experiments` - Returns 403
- `PUT /api/demo/experiments/{id}` - Returns 403
- `DELETE /api/demo/experiments/{id}` - Returns 403

### Production Deployment

For production, disable demo mode:

```bash
DEMO_MODE=false
# Or omit DEMO_MODE variable
```

## Data Protection

### Database Security

**SQLite** (Default):
- File permissions: Restrict access to backend user only
- Encryption: Consider SQLCipher for sensitive data
- Backup: Regular backups of database file

**PostgreSQL** (Production):
- Use SSL/TLS connections
- Implement connection pooling
- Use strong authentication
- Enable audit logging

### Audit Logs

- **Location**: `/app/data/audit_logs/` (container)
- **Permissions**: Restrict file access
- **Retention**: Implement log rotation
- **Sensitive Data**: Sanitize before logging

### Environment Variables

**Never commit**:
- API keys
- Database passwords
- LLM provider credentials
- Secret tokens

**Use `.env` file** (gitignored):
```bash
# .env.example documents structure
# .env contains actual secrets (never commit)
```

## Production Hardening

### Docker Security

**Enable Security Options** (docker-compose.yml):
```yaml
services:
  cerebro-backend:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
```

**Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
```

### Network Security

**CORS Configuration**:
```bash
# Restrict to your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_CREDENTIALS=true
```

**Firewall Rules**:
- Only expose necessary ports (9000 for backend)
- Use reverse proxy (nginx/traefik) for SSL/TLS
- Implement IP whitelisting if needed

### LLM Provider Security

**API Key Protection**:
- Store in secure environment variables
- Rotate keys regularly
- Monitor usage for anomalies
- Use separate keys per environment

**Rate Limiting**:
- Respect provider rate limits
- Implement circuit breakers
- Use exponential backoff

### Monitoring and Alerting

**Health Checks**:
```bash
# Automated health monitoring
curl http://localhost:9000/health
```

**Log Monitoring**:
- Monitor error logs for security events
- Alert on suspicious patterns
- Track API key usage

**Metrics**:
- Request rate
- Error rate
- Response times
- Circuit breaker state

## Security Checklist

### Pre-Production

- [ ] API key authentication enabled
- [ ] Strong API keys generated
- [ ] Rate limiting configured
- [ ] CORS origins restricted
- [ ] Demo mode disabled
- [ ] Database permissions secured
- [ ] Audit logs protected
- [ ] Environment variables secured
- [ ] Docker security options enabled
- [ ] Health checks configured
- [ ] Monitoring in place

### Ongoing

- [ ] Regular API key rotation
- [ ] Security updates applied
- [ ] Log review for anomalies
- [ ] Backup verification
- [ ] Access control audit

---

**Next Steps**:
- See [Configuration Guide](configuration.md) for security settings
- Read [Deployment Guide](deployment.md) for production setup
- Check [User Guide](user-guide.md) for secure usage
