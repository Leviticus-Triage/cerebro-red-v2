# CEREBRO-RED v2 Troubleshooting Guide

## Common Issues and Solutions

### CORS Errors

**Symptom**: Browser console shows "CORS policy" errors

**Solutions**:
1. Verify `.env` has correct `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

2. Check backend logs for CORS configuration:
   ```bash
   docker-compose logs backend | grep CORS
   ```

3. Test CORS with curl:
   ```bash
   curl -X OPTIONS http://localhost:8889/api/experiments \
     -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```

### 500 Internal Server Error

**Symptom**: Experiment creation fails with 500 error

**Solutions**:
1. Check backend logs:
   ```bash
   docker-compose logs backend --tail=100
   ```

2. Verify database is initialized:
   ```bash
   docker-compose exec backend alembic current
   ```

3. Test with minimal payload:
   ```bash
   curl -X POST http://localhost:8889/api/experiments \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-api-key-change-this" \
     -d '{"name":"Test","initial_prompts":["test"],"strategies":["obfuscation_base64"],...}'
   ```

### 422 Unprocessable Entity

**Symptom**: `/api/vulnerabilities/statistics` returns 422

**Solutions**:
1. Verify route order in `backend/api/vulnerabilities.py`:
   - `/statistics` should be before `/{vulnerability_id}`

2. Check FastAPI route registration order in logs

3. Test endpoint directly:
   ```bash
   curl -X GET http://localhost:8889/api/vulnerabilities/statistics \
     -H "X-API-Key: your-secret-api-key-change-this"
   ```

### API Key Authentication Issues

**Symptom**: 401 Unauthorized errors

**Solutions**:
1. Check if API key authentication is enabled:
   ```bash
   grep API_KEY_ENABLED .env
   ```

2. Verify API key matches:
   ```bash
   grep API_KEY .env
   ```

3. Disable authentication for testing:
   ```
   API_KEY_ENABLED=false
   ```

### WebSocket Connection Failures

**Symptom**: Real-time updates not working

**Solutions**:
1. Verify WebSocket endpoint is accessible:
   ```bash
   wscat -c ws://localhost:8889/ws/scan/{experiment_id}
   ```

2. Check browser console for WebSocket errors

3. Verify experiment ID is valid

### Frontend Build Errors

**Symptom**: `npm run build` fails

**Solutions**:
1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Check TypeScript errors:
   ```bash
   npm run type-check
   ```

3. Verify all imports are correct

## Debug Mode

Enable debug mode for detailed logging:

```env
CEREBRO_DEBUG=true
CEREBRO_LOG_LEVEL=DEBUG
```

## Health Check

Verify system health:

```bash
curl http://localhost:8889/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "llm_providers": {"ollama": "healthy"},
    "telemetry": "healthy",
    "cors": "configured"
  }
}
```

## Getting Help

1. Check logs: `docker-compose logs backend frontend`
2. Review this troubleshooting guide
3. Check GitHub issues
4. Enable debug mode for detailed error messages

