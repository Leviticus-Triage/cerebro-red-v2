# 🔧 Backend Troubleshooting Guide

## Problem: Backend antwortet nicht (404/400 Fehler)

### Symptome
- `curl http://localhost:8000/health` gibt 404 zurück
- API-Anfragen schlagen mit 400/404 fehl
- `./QUICK_TEST_EXAMPLES.sh` zeigt "Backend nicht erreichbar"

### Lösung

#### 1. Prüfe ob Backend läuft

```bash
# Prüfe Port 8000
netstat -tlnp | grep :8000
# oder
ss -tlnp | grep :8000

# Prüfe Docker Container
docker compose ps

# Prüfe Backend-Logs
docker compose logs cerebro-backend
```

#### 2. Starte Backend

**Option A: Automatisch (empfohlen)**
```bash
./START_BACKEND.sh
```

**Option B: Docker**
```bash
docker compose up -d cerebro-backend
docker compose logs -f cerebro-backend  # Logs anzeigen
```

**Option C: Lokal (für Entwicklung)**
```bash
cd backend
source ../venv/bin/activate  # oder Ihr venv
uvicorn main:app --reload --port 8000
```

#### 3. Prüfe Backend-Status

```bash
# Health Check
curl http://localhost:8000/health

# Sollte zurückgeben:
# {"status": "healthy", "database": "healthy", ...}
```

#### 4. Häufige Probleme

**Problem: Port 8000 bereits belegt**
```bash
# Finde Prozess auf Port 8000
lsof -i :8000
# oder
fuser 8000/tcp

# Stoppe den Prozess oder ändere Port in .env:
# CEREBRO_PORT=8001
```

**Problem: Docker läuft nicht**
```bash
# Starte Docker
sudo systemctl start docker

# Prüfe Docker-Status
docker ps
```

**Problem: Backend startet, aber Health-Check schlägt fehl**
```bash
# Prüfe Backend-Logs
docker compose logs cerebro-backend | tail -50

# Prüfe Datenbank-Verbindung
docker compose exec cerebro-backend python3 -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

**Problem: API-Key Fehler (401)**
```bash
# Prüfe .env Datei
cat .env | grep API_KEY

# Standard Test-Key sollte sein:
# API_KEY=test-api-key
```

#### 5. Vollständiger Neustart

```bash
# Stoppe alles
docker compose down

# Lösche alte Container (optional)
docker compose down -v

# Starte neu
docker compose up -d

# Prüfe Status
docker compose ps
curl http://localhost:8000/health
```

## Problem: 400 Bad Request bei API-Anfragen

### Mögliche Ursachen

1. **Fehlende required fields** in JSON-Payload
2. **Falsche Datentypen** (z.B. String statt Array)
3. **Ungültige Enum-Werte** (z.B. falsche strategy-Namen)

### Lösung

```bash
# Verwende vollständige Beispiele aus:
# - QUICK_TEST_EXAMPLES.sh
# - PROFESSIONAL_TESTING_GUIDE.md
# - README.md (Cloud OpenAI Section)

# Prüfe API-Dokumentation
curl http://localhost:8000/docs
# Öffne im Browser: http://localhost:8000/docs

# Teste mit minimalem Payload
curl -X POST http://localhost:8000/api/experiments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "experiment_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Test",
    "target_model_provider": "ollama",
    "target_model_name": "qwen2.5:3b",
    "attacker_model_provider": "ollama",
    "attacker_model_name": "qwen3:8b",
    "judge_model_provider": "ollama",
    "judge_model_name": "qwen3:8b",
    "initial_prompts": ["test"],
    "strategies": ["roleplay_injection"]
  }'
```

## Problem: Ollama Connection Error

### Symptome
- `Cannot connect to host host.docker.internal:11434`
- `Name or service not known`

### Lösung

```bash
# Prüfe Ollama läuft
curl http://localhost:11434/api/tags

# Für Docker: Verwende host.docker.internal
# Für lokal: Verwende localhost

# In .env setzen:
OLLAMA_BASE_URL=http://localhost:11434  # Lokal
# oder
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Docker
```

## Nützliche Befehle

```bash
# Backend-Status prüfen
curl http://localhost:8000/health | jq .

# Alle Experimente auflisten
curl -H "X-API-Key: test-api-key" http://localhost:8000/api/experiments | jq .

# Backend-Logs live anzeigen
docker compose logs -f cerebro-backend

# Backend neu starten
docker compose restart cerebro-backend

# Datenbank zurücksetzen (ACHTUNG: Löscht alle Daten!)
docker compose down -v
docker compose up -d
```
