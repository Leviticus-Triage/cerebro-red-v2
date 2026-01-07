# 🔬 CEREBRO-RED v2 - Live Monitoring Guide

## 📊 Neue Live-Monitoring-Funktionen

Das Frontend wurde um ein umfassendes Live-Monitoring-Dashboard erweitert, das dir ermöglicht:

### ✅ Was du jetzt sehen kannst:

| Feature | Beschreibung |
|---------|--------------|
| **📜 Live Logs** | Echtzeit-Stream aller LLM-Anfragen und -Antworten |
| **📊 Iteration Results** | Detaillierte Ergebnisse jeder Iteration mit Prompt, Response, Score |
| **📋 Task Queue** | Übersicht über laufende, wartende und abgeschlossene Tasks |
| **🎯 Progress Overview** | Fortschrittsbalken, Laufzeit, geschätzte Restzeit |
| **⚖️ Judge Evaluations** | Scoring, Reasoning und Success-Status |
| **⚔️ Attack Mutations** | Strategie und mutierter Prompt |
| **❌ Errors** | Fehlermeldungen in Echtzeit |

---

## 🚀 Zugriff auf Live Monitor

### Option 1: Über das Web-Interface

1. Öffne http://localhost:3000
2. Gehe zu **Experiments** → Wähle ein Experiment
3. Klicke auf **"Live Monitor"** Button (cyan)

### Option 2: Direkter URL-Zugriff

```
http://localhost:3000/experiments/{experiment_id}/monitor
```

---

## 🎮 Bedienung des Live Monitors

### Tabs

| Tab | Inhalt |
|-----|--------|
| **📜 Live Logs** | Streaming-Logs mit Farbcodierung nach Typ |
| **📊 Iterations** | Karten- oder Tabellenansicht der Ergebnisse |
| **📋 Task Queue** | Aktuelle und abgeschlossene Tasks |

### Log-Filter

- **All**: Alle Log-Einträge
- **LLM**: Nur LLM-Anfragen und -Antworten
- **Judge**: Nur Judge-Evaluierungen
- **Attack**: Nur Attack-Mutationen
- **Error**: Nur Fehlermeldungen

### Farbcodierung

| Farbe | Bedeutung |
|-------|-----------|
| 🔴 Rot | Attacker-Modell |
| 🔵 Blau | Target-Modell |
| 🟡 Amber | Judge-Modell |
| 🟢 Grün | Erfolgreiche Antwort |
| 🔴 Rose | Fehler |

---

## 📡 WebSocket-Events

Das Backend sendet folgende Events über WebSocket:

```typescript
// Verbindung
{ type: 'connected', experiment_id: '...' }

// Fortschritt
{ type: 'progress', iteration: 1, total_iterations: 5, progress_percent: 20.0 }

// Iteration Start
{ type: 'iteration_start', iteration: 1, strategy_used: 'roleplay_injection' }

// LLM Request
{ type: 'llm_request', role: 'attacker', provider: 'ollama', model: 'qwen3:8b', prompt: '...' }

// LLM Response
{ type: 'llm_response', role: 'target', response: '...', latency_ms: 1234, tokens: 500 }

// Judge Evaluation
{ type: 'judge_evaluation', judge_score: 3.5, success: false, reasoning: '...' }

// Iteration Complete
{ type: 'iteration_complete', iteration: 1, judge_score: 3.5, success: false }

// Experiment Complete
{ type: 'experiment_complete', status: 'completed', vulnerabilities_found: 0 }
```

---

## 🔧 Konfiguration

### Verbosity Level (docker-compose.yml)

```yaml
environment:
  - CEREBRO_VERBOSITY=3  # 0=Errors, 1=Warnings, 2=LLM Details, 3=Full
```

### Debug-Modus aktivieren

```bash
docker compose -f docker-compose.yml -f docker-compose.debug.yml up -d
```

---

## 🧪 Schnelltest

```bash
# 1. Backend-Status prüfen
curl http://localhost:9000/health | jq .

# 2. Experiment erstellen
EXPERIMENT_ID=$(uuidgen)
curl -X POST http://localhost:9000/api/experiments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d "{
    \"experiment_id\": \"$EXPERIMENT_ID\",
    \"name\": \"Live Monitor Test\",
    \"target_model_provider\": \"ollama\",
    \"target_model_name\": \"qwen2.5:3b\",
    \"attacker_model_provider\": \"ollama\",
    \"attacker_model_name\": \"qwen3:8b\",
    \"judge_model_provider\": \"ollama\",
    \"judge_model_name\": \"qwen3:8b\",
    \"initial_prompts\": [\"Test prompt\"],
    \"strategies\": [\"roleplay_injection\"],
    \"max_iterations\": 2
  }"

# 3. Scan starten
curl -X POST "http://localhost:9000/api/scan/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d "{\"experiment_id\": \"$EXPERIMENT_ID\"}"

# 4. Live Monitor öffnen
echo "Öffne: http://localhost:3000/experiments/$EXPERIMENT_ID/monitor"
```

---

## 📁 Neue Dateien

```
frontend/src/
├── components/monitor/
│   ├── index.ts                    # Barrel export
│   ├── LiveLogPanel.tsx            # Echtzeit-Log-Viewer
│   ├── TaskQueuePanel.tsx          # Task-Queue-Anzeige
│   ├── IterationResultsPanel.tsx   # Iterations-Ergebnisse
│   └── ProgressOverview.tsx        # Fortschritts-Übersicht
├── pages/
│   └── ExperimentMonitor.tsx       # Haupt-Monitor-Seite
└── types/api.ts                    # Erweiterte WebSocket-Types

backend/api/
└── websocket.py                    # Erweiterte WebSocket-Events
```

---

## 🎯 Nächste Schritte

1. **Experiment starten** und Live Monitor öffnen
2. **Logs beobachten** während der Ausführung
3. **Iterations-Details** analysieren
4. **Ergebnisse exportieren** (JSON/CSV/PDF)

---

*CEREBRO-RED v2 - AI Red Team Framework*
*Live Monitoring implementiert am 2025-12-25*
