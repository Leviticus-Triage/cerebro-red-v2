# Bereitstellungsanleitung

[🇬🇧 English](../en/deployment.md) | [🇩🇪 Deutsch](bereitstellung.md)

Vollständige Anleitung zur Bereitstellung von CEREBRO-RED v2 lokal und auf der Railway-Cloud-Plattform.

## Inhaltsverzeichnis

1. [Lokale Bereitstellung](#lokale-bereitstellung)
2. [Railway-Bereitstellung](#railway-bereitstellung)
3. [Health Checks](#health-checks)
4. [Demo-Modus](#demo-modus)
5. [Fehlerbehebung](#fehlerbehebung)

## Lokale Bereitstellung

### Voraussetzungen

- Docker 24.0+ und Docker Compose 2.20+
- Ollama installiert und laufend (für lokale LLM-Tests)
- 4GB+ RAM verfügbar
- Ports 9000 (Backend) und 3000 (Frontend) verfügbar

### Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/Leviticus-Triage/cerebro-red-v2.git
cd cerebro-red-v2

# 2. Umgebung konfigurieren
cp .env.example .env
# Bearbeiten Sie .env bei Bedarf (Standards funktionieren in den meisten Fällen)

# 3. Dienste starten
docker compose up -d

# 4. Bereitstellung überprüfen
curl http://localhost:9000/health
```

### Schritt-für-Schritt-Einrichtung

#### 1. Ollama installieren

```bash
# Ollama installieren
curl -fsSL https://ollama.ai/install.sh | sh

# Erforderliche Modelle abrufen
ollama pull qwen3:8b
ollama pull qwen2.5:3b

# Ollama-Dienst starten
ollama serve
```

#### 2. Umgebung konfigurieren

Erstellen Sie `.env` Datei:

```bash
# Anwendung
CEREBRO_HOST=0.0.0.0
CEREBRO_PORT=9000
CEREBRO_ENV=production

# Ollama
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434
OLLAMA_MODEL_ATTACKER=qwen3:8b
OLLAMA_MODEL_TARGET=qwen2.5:3b
OLLAMA_MODEL_JUDGE=qwen3:8b

# Datenbank
DATABASE_URL=sqlite+aiosqlite:////app/data/cerebro.db
AUDIT_LOG_PATH=/app/data/audit_logs
```

#### 3. Dienste starten

```bash
# Alle Dienste starten
docker compose up -d

# Oder nur Backend starten
docker compose up -d cerebro-backend

# Protokolle anzeigen
docker compose logs -f
```

#### 4. Bereitstellung überprüfen

```bash
# Dienststatus prüfen
docker compose ps

# Backend-Gesundheit testen
curl http://localhost:9000/health | jq

# Frontend testen (wenn läuft)
curl -I http://localhost:3000
```

### Zugriffspunkte

- **Backend API**: http://localhost:9000
- **API-Dokumentation**: http://localhost:9000/docs
- **Frontend UI**: http://localhost:3000
- **Health Check**: http://localhost:9000/health

## Railway-Bereitstellung

### Voraussetzungen

- Railway-Konto (kostenloser Tarif verfügbar)
- GitHub-Repository mit Railway verbunden
- Docker-Image erstellt und zu GitHub Container Registry gepusht (optional)

### Schritt 1: Railway-Projekt erstellen

1. Gehen Sie zu [railway.app](https://railway.app)
2. Klicken Sie auf "New Project"
3. Wählen Sie "Deploy from GitHub repo"
4. Wählen Sie `Leviticus-Triage/cerebro-red-v2`

### Schritt 2: Umgebungsvariablen konfigurieren

Im Railway-Dashboard Umgebungsvariablen setzen:

```bash
# Anwendung
CEREBRO_ENV=production
CEREBRO_HOST=0.0.0.0
CEREBRO_PORT=$PORT  # Railway stellt $PORT bereit

# Demo-Modus (für öffentliche Demo)
DEMO_MODE=true

# Ollama (wenn Railway Ollama-Dienst verwendet)
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_API_BASE=http://ollama-service:11434

# Oder Cloud-LLM verwenden
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Datenbank
DATABASE_URL=sqlite+aiosqlite:////app/data/cerebro.db
AUDIT_LOG_PATH=/app/data/audit_logs

# Sicherheit
API_KEY_ENABLED=false  # Für Demo deaktivieren
CORS_ORIGINS=https://ihre-railway-domain.railway.app
```

### Schritt 3: Railway-Einstellungen konfigurieren

Erstellen Sie `railway.json`:

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

### Schritt 4: Bereitstellen

Railway automatisch:
1. Erkennt `railway.json` Konfiguration
2. Baut Docker-Image aus `docker/Dockerfile.backend`
3. Stellt auf Railway-Infrastruktur bereit
4. Führt Health Checks aus
5. Stellt öffentliche URL bereit

## Health Checks

### Backend Health Endpunkt

```bash
curl http://localhost:9000/health
```

**Antwort**:
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

## Demo-Modus

### Konfiguration

Demo-Modus für schreibgeschützte öffentliche Instanzen aktivieren:

```bash
DEMO_MODE=true
```

### Demo-Modus-Verhalten

- **Lese-Operationen**: Erlaubt (GET-Anfragen geben Mock-Daten zurück)
- **Schreib-Operationen**: Blockiert (POST/PUT/DELETE geben 403 zurück)
- **Mock-Daten**: Vorkonfigurierte Experimente (laufend, fehlgeschlagen, abgeschlossen)
- **Geführte Tour**: Frontend zeigt automatisch interaktive Tour

### Demo-Modus deaktivieren

Für Produktionsbereitstellung:

```bash
DEMO_MODE=false
# Oder DEMO_MODE Variable ganz weglassen
```

## Fehlerbehebung

### Lokale Bereitstellungsprobleme

#### Dienste starten nicht

```bash
# Protokolle prüfen
docker compose logs cerebro-backend

# Docker läuft verifizieren
docker ps

# Portkonflikte prüfen
lsof -i :9000
lsof -i :3000
```

#### Ollama-Verbindung fehlgeschlagen

```bash
# Ollama läuft verifizieren
curl http://localhost:11434/api/tags

# host.docker.internal-Auflösung prüfen
docker compose exec cerebro-backend ping host.docker.internal

# Linux-Fix: Sicherstellen, dass extra_hosts in docker-compose.yml vorhanden ist
extra_hosts:
  - "host.docker.internal:host-gateway"
```

---

**Nächste Schritte**:
- Siehe [Konfigurationsanleitung](konfiguration.md) für detaillierte Einstellungen
- Lesen Sie [Architektur-Anleitung](../en/architecture.md) für Systemdesign
- Prüfen Sie [Sicherheitsanleitung](../en/security.md) für Produktionshärtung
