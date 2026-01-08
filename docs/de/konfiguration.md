# Konfigurationsanleitung

[🇬🇧 English](../en/configuration.md) | [🇩🇪 Deutsch](konfiguration.md)

Vollständige Referenz für die Konfiguration von CEREBRO-RED v2 Umgebungsvariablen und Einstellungen.

## Inhaltsverzeichnis

1. [Umgebungsvariablen](#umgebungsvariablen)
2. [LLM-Provider-Konfiguration](#llm-provider-konfiguration)
3. [Datenbankkonfiguration](#datenbankkonfiguration)
4. [Sicherheitseinstellungen](#sicherheitseinstellungen)
5. [Leistungsoptimierung](#leistungsoptimierung)

## Umgebungsvariablen

### Anwendungskonfiguration

| Variable | Standard | Beschreibung |
|----------|----------|-------------|
| `CEREBRO_HOST` | `0.0.0.0` | Host-Adresse zum Binden (verwenden Sie `0.0.0.0` für Docker, `127.0.0.1` für lokal) |
| `CEREBRO_PORT` | `9000` | Backend-Service-Port |
| `CEREBRO_ENV` | `production` | Umgebungsmodus: `development` oder `production` |
| `DEBUG_MODE` | `false` | Debug-Protokollierung und Endpunkte aktivieren |
| `CEREBRO_LOG_LEVEL` | `INFO` | Protokollierungsstufe: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `CEREBRO_VERBOSITY` | `1` | Ausführlichkeitsstufe (0-5, höher = ausführlicher) |

### Beispiel `.env` Datei

```bash
# Anwendung
CEREBRO_HOST=0.0.0.0
CEREBRO_PORT=9000
CEREBRO_ENV=production
DEBUG_MODE=false

# Protokollierung
CEREBRO_LOG_LEVEL=INFO
CEREBRO_VERBOSITY=1
```

## LLM-Provider-Konfiguration

CEREBRO-RED v2 unterstützt mehrere LLM-Provider über LiteLLM.

### Ollama (Lokal)

Am besten für: Datenschutz, Offline-Betrieb, keine API-Kosten

```bash
# Ollama-Konfiguration
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_HOST=http://host.docker.internal:11434

# Modellauswahl
OLLAMA_MODEL_ATTACKER=qwen3:8b
OLLAMA_MODEL_TARGET=qwen2.5:3b
OLLAMA_MODEL_JUDGE=qwen3:8b
```

**Einrichtung**:
1. Ollama installieren: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Modelle abrufen: `ollama pull qwen3:8b qwen2.5:3b`
3. Ollama starten: `ollama serve`

**Docker-Hinweis**: Verwenden Sie `host.docker.internal:11434`, um Host-Ollama vom Container aus zuzugreifen.

### Azure OpenAI

Am besten für: Unternehmensbereitstellungen, hochwertige Mutationen

```bash
# Azure OpenAI-Konfiguration
DEFAULT_LLM_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=ihr-api-schlüssel-hier
AZURE_OPENAI_ENDPOINT=https://ihre-ressource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Modellauswahl (verwenden Sie Deployment-Namen)
AZURE_OPENAI_MODEL_ATTACKER=gpt-4-deployment
AZURE_OPENAI_MODEL_TARGET=gpt-3.5-turbo-deployment
AZURE_OPENAI_MODEL_JUDGE=gpt-4-deployment
```

### OpenAI

Am besten für: Schnelle Antworten, Produktionstests

```bash
# OpenAI-Konfiguration
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-ihr-api-schlüssel-hier
OPENAI_ORG_ID=org-ihre-org-id  # Optional

# Modellauswahl
OPENAI_MODEL_ATTACKER=gpt-4
OPENAI_MODEL_TARGET=gpt-3.5-turbo
OPENAI_MODEL_JUDGE=gpt-4
```

## Datenbankkonfiguration

### SQLite (Standard)

```bash
DATABASE_URL=sqlite+aiosqlite:////app/data/cerebro.db
AUDIT_LOG_PATH=/app/data/audit_logs
```

**Pfade**:
- **Container**: `/app/data/cerebro.db` (über Docker-Volume persistent)
- **Lokal**: `data/experiments/cerebro.db` (relativ zum Backend-Verzeichnis)

## Sicherheitseinstellungen

### API-Authentifizierung

```bash
# API-Schlüssel-Authentifizierung
API_KEY=ihr-geheimer-api-schlüssel
API_KEY_ENABLED=true
```

**Verwendung**:
```bash
curl -H "X-API-Key: ihr-geheimer-api-schlüssel" http://localhost:9000/api/experiments
```

**Für Entwicklung deaktivieren**:
```bash
API_KEY_ENABLED=false
```

### CORS-Konfiguration

```bash
# Erlaubte Ursprünge (kommagetrennt)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000,http://localhost:9000

# Anmeldedaten aktivieren
CORS_CREDENTIALS=true
```

**Produktion**: Beschränken Sie auf Ihre Frontend-Domain:
```bash
CORS_ORIGINS=https://ihredomain.com,https://www.ihredomain.com
```

### Rate Limiting

```bash
# Anfragen pro Minute pro IP
RATE_LIMIT_PER_MINUTE=60
```

## Leistungsoptimierung

### Circuit Breaker-Konfiguration

```bash
# Fehlerschwelle vor Öffnen des Circuits
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5

# Timeout vor Wiederherstellungsversuch (Sekunden)
CIRCUIT_BREAKER_TIMEOUT=60
```

**Für lokales Ollama** (langsamere Antworten):
```bash
CIRCUIT_BREAKER_FAILURE_THRESHOLD=15
CIRCUIT_BREAKER_TIMEOUT=120
CIRCUIT_BREAKER_JITTER_ENABLED=true
```

---

**Nächste Schritte**:
- Siehe [Bereitstellungsanleitung](bereitstellung.md) für Produktionskonfiguration
- Lesen Sie [Sicherheitsanleitung](../en/security.md) für Best Practices
- Prüfen Sie [Benutzerhandbuch](benutzerhandbuch.md) für Verwendungsbeispiele
