# 🚀 Backend Start-Anleitung

## Problem: Backend antwortet nicht (404/400)

**Das Backend läuft nicht auf Port 8000!**

## Lösung

### Schritt 1: Prüfe Port 8000

```bash
# Prüfe ob Port 8000 belegt ist
lsof -i :8000
# oder
ss -tlnp | grep :8000

# Falls ein anderer Service läuft:
# - Stoppe ihn, ODER
# - Ändere Port in .env: CEREBRO_PORT=8001
```

### Schritt 2: Starte Backend

**Option A: Automatisch (empfohlen)**
```bash
./START_BACKEND.sh
```

**Option B: Docker**
```bash
docker compose up -d cerebro-backend
docker compose logs -f cerebro-backend
```

**Option C: Lokal**
```bash
cd backend
source ../venv/bin/activate  # oder Ihr venv
uvicorn main:app --reload --port 8000
```

### Schritt 3: Prüfe Backend läuft

```bash
curl http://localhost:8000/health
# Sollte zurückgeben: {"status": "healthy", ...}
```

### Schritt 4: Teste API

```bash
./QUICK_TEST_EXAMPLES.sh
```

## Vollständige Troubleshooting-Anleitung

Siehe: [TROUBLESHOOTING_BACKEND.md](./TROUBLESHOOTING_BACKEND.md)
