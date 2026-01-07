# CEREBRO-RED v2 - Kritische Bug-Analyse und TRAYCER Fix-Prompt

## Datum: 2026-01-03
## Status: KRITISCH - Experimente starten nicht mehr

---

## 🔴 HAUPTPROBLEM

**Experimente werden sofort als FAILED markiert, ohne dass eine einzige Iteration ausgeführt wird.**

Vor den TRAYCER-Fixes hat das System noch teilweise funktioniert. Nach mehreren Debugging-Versuchen und Code-Änderungen ist das System nun komplett defekt.

---

## 🐛 IDENTIFIZIERTE FEHLER

### 1. **`run_experiment()` wird NIE aufgerufen**
**Symptom:**
- POST /api/scan/start gibt 200 OK zurück
- Experiment wird in DB erstellt mit Status PENDING
- Sofort danach wird Status auf FAILED gesetzt
- KEINE DEBUG-Logs aus `run_experiment()` erscheinen
- Meldung: "Experiment marked as FAILED: no successful iterations found"

**Root Cause:**
```python
# In backend/api/scans.py, Zeile 167:
asyncio.create_task(_run_experiment_with_error_handling(experiment_config))
```

**Problem:** 
- `asyncio.create_task()` erstellt eine Task, aber ohne Referenz wird sie vom Garbage Collector gelöscht
- Die Task wird NIEMALS ausgeführt
- Das Experiment bleibt in PENDING und wird dann als FAILED markiert

**Versuchter Fix:**
```python
# Hinzugefügt:
background_tasks_set = set()

# Geändert:
task = asyncio.create_task(_run_experiment_with_error_handling(experiment_config))
background_tasks_set.add(task)
task.add_done_callback(background_tasks_set.discard)
```

**Status:** UNGETESTET - Muss verifiziert werden!

---

### 2. **AttackStrategyType Enum-Verwirrung**
**Symptom:**
- CRITICAL-Logs: "Strategies are strings, not AttackStrategyType enums!"
- Aber die Logs zeigen Enums: `<AttackStrategyType.RESEARCH_PRE_JAILBREAK: 'research_pre_jailbreak'>`

**Root Cause:**
```python
# AttackStrategyType erbt von str UND Enum:
class AttackStrategyType(str, Enum):
    RESEARCH_PRE_JAILBREAK = "research_pre_jailbreak"
    # ...

# Deshalb gibt isinstance(enum_value, str) TRUE zurück!
```

**Versuchter Fix:**
```python
# Statt:
if isinstance(first_strategy, str):
    # Convert...

# Jetzt:
if not isinstance(first_strategy, AttackStrategyType):
    # Convert...
```

**Status:** GEFIXT - Keine CRITICAL-Meldungen mehr

---

### 3. **Fehlende Volume-Mounts für Live-Code-Updates**
**Symptom:**
- Code-Änderungen werden nicht im Container reflektiert
- Nach `docker compose restart` läuft immer noch alte Version
- Python-Cache-Clearing hilft nicht

**Root Cause:**
```yaml
# docker-compose.yml hat KEINE Volume-Mounts für Backend-Code:
volumes:
  - cerebro-data:/app/data
  - cerebro-experiments:/app/data/experiments
  # FEHLT: - ./backend:/app
```

**Konsequenz:**
- Jede Code-Änderung erfordert vollständigen Image-Rebuild
- `docker compose build cerebro-backend --no-cache` dauert ~2-3 Minuten
- Entwicklung extrem langsam

**Empfohlener Fix:**
```yaml
volumes:
  - ./backend:/app  # Live-Code-Mounting für Entwicklung
  - cerebro-data:/app/data
  - cerebro-experiments:/app/data/experiments
```

---

### 4. **Keine Fehlerbehandlung für Task-Failures**
**Symptom:**
- Wenn `_run_experiment_with_error_handling()` fehlschlägt, gibt es keine Logs
- Exception wird in `try/except` gefangen, aber nur Status auf FAILED gesetzt
- Keine Details über WARUM es fehlgeschlagen ist

**Code:**
```python
async def _run_experiment_with_error_handling(config: ExperimentConfig):
    try:
        await orchestrator.run_experiment(config)
    except Exception as e:
        # Update status to FAILED
        async with AsyncSessionLocal() as error_session:
            error_repo = ExperimentRepository(error_session)
            await error_repo.update_status(config.experiment_id, ExperimentStatus.FAILED.value)
            await error_session.commit()
        logger.error(f"Experiment {config.experiment_id} failed with exception: {type(e).__name__}: {str(e)}")
        # FEHLT: Traceback, Stack-Trace, detaillierte Fehleranalyse
```

**Empfohlener Fix:**
```python
import traceback

logger.error(f"Experiment {config.experiment_id} failed with exception: {type(e).__name__}: {str(e)}")
logger.error(f"Traceback:\n{traceback.format_exc()}")
```

---

### 5. **DEBUG-Logs erscheinen nicht**
**Symptom:**
- Viele `logger.info(f"[DEBUG] ...")` Statements im Code
- KEINE dieser Logs erscheinen in `docker compose logs`
- Nur CRITICAL, ERROR, und INFO-Logs ohne [DEBUG]-Prefix erscheinen

**Mögliche Ursachen:**
1. Log-Level falsch konfiguriert (trotz `CEREBRO_LOG_LEVEL=DEBUG`)
2. Logger-Name stimmt nicht (verschiedene Logger in verschiedenen Modulen)
3. Logs werden gepuffert und nie geflusht
4. Code wird gar nicht ausgeführt (siehe Fehler #1)

**Zu prüfen:**
```python
# In main.py oder logging-Konfiguration:
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

---

## 📊 ZEITLICHER ABLAUF DER VERSCHLECHTERUNG

### **VORHER (funktionierte teilweise):**
- Experimente starteten
- Iterationen wurden ausgeführt
- Einige Strategien funktionierten
- Probleme: Fehlende Templates, Enum-Konvertierung

### **NACH TRAYCER-FIXES:**
1. ✅ Templates für alle Strategien hinzugefügt
2. ✅ Enum-Konvertierung in API-Layer
3. ❌ **ABER:** `run_experiment()` wird nicht mehr aufgerufen
4. ❌ Experimente schlagen sofort fehl
5. ❌ Keine Iterationen werden ausgeführt

### **VERMUTUNG:**
- Eine der Änderungen hat die Task-Ausführung unterbrochen
- Möglicherweise Änderungen an `scans.py` oder `orchestrator.py`
- Oder Änderungen an der Async-Execution-Logik

---

## 🎯 TRAYCER FIX-PROMPT

```
# TRAYCER MISSION: Repariere CEREBRO-RED v2 Experiment-Execution

## KONTEXT
Das CEREBRO-RED v2 System ist nach mehreren Debugging-Versuchen defekt. Experimente werden sofort als FAILED markiert, ohne dass eine einzige Iteration ausgeführt wird. Vor den Fixes hat das System noch teilweise funktioniert.

## HAUPTPROBLEM
`run_experiment()` in `backend/core/orchestrator.py` wird NIE aufgerufen, obwohl der API-Endpoint `/api/scan/start` erfolgreich antwortet.

## AUFGABE
Analysiere und repariere das System in strukturierten Phasen:

---

### PHASE 1: DIAGNOSE - Verstehe den aktuellen Zustand

**Ziele:**
1. Prüfe, ob `asyncio.create_task()` die Task korrekt erstellt
2. Verifiziere, ob die Task-Referenz behalten wird (Garbage Collection)
3. Prüfe Event-Loop-Status und Task-Scheduling
4. Identifiziere, wo genau die Execution abbricht

**Aktionen:**
- Füge umfassende Logging in `backend/api/scans.py` hinzu:
  - Vor `asyncio.create_task()`
  - Nach `asyncio.create_task()`
  - Am Anfang von `_run_experiment_with_error_handling()`
  - Am Anfang von `run_experiment()` (erste Zeile!)
- Prüfe, ob Tasks im Event-Loop registriert werden
- Verifiziere, dass keine Exceptions die Task-Erstellung verhindern

**Erfolgskriterium:**
- Wir sehen GENAU, wo die Execution stoppt
- Wir verstehen, WARUM `run_experiment()` nicht aufgerufen wird

---

### PHASE 2: TASK-EXECUTION-FIX

**Ziele:**
1. Stelle sicher, dass Background-Tasks ausgeführt werden
2. Verhindere Garbage Collection von Tasks
3. Implementiere robustes Task-Management

**Aktionen:**
- Implementiere Task-Set für Referenzen (bereits versucht, muss getestet werden)
- Alternative: Verwende `BackgroundTasks` von FastAPI statt `asyncio.create_task()`
- Oder: Verwende `asyncio.ensure_future()` mit expliziter Referenz
- Füge Task-Monitoring hinzu (wie viele Tasks laufen, welche sind pending)

**Code-Beispiel:**
```python
# Option A: FastAPI BackgroundTasks (empfohlen)
@router.post("/start")
async def start_scan(
    request: ScanStartRequest,
    background_tasks: BackgroundTasks,  # FastAPI's BackgroundTasks
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator)
):
    background_tasks.add_task(orchestrator.run_experiment, request.experiment_config)
    return {"status": "started"}

# Option B: Task-Set (bereits implementiert, muss getestet werden)
background_tasks_set = set()
task = asyncio.create_task(...)
background_tasks_set.add(task)
task.add_done_callback(background_tasks_set.discard)

# Option C: Explizite Task-Referenz in Orchestrator
class RedTeamOrchestrator:
    def __init__(self):
        self._running_tasks = {}
    
    def start_experiment(self, config):
        task = asyncio.create_task(self.run_experiment(config))
        self._running_tasks[config.experiment_id] = task
        task.add_done_callback(lambda t: self._running_tasks.pop(config.experiment_id, None))
```

**Erfolgskriterium:**
- `run_experiment()` wird aufgerufen
- DEBUG-Logs erscheinen: "[DEBUG] ========== run_experiment CALLED =========="

---

### PHASE 3: VOLUME-MOUNTING FÜR ENTWICKLUNG

**Ziele:**
1. Ermögliche Live-Code-Updates ohne Image-Rebuild
2. Beschleunige Entwicklungs-Iteration

**Aktionen:**
- Füge Volume-Mount in `docker-compose.yml` hinzu:
```yaml
services:
  cerebro-backend:
    volumes:
      - ./backend:/app  # Live-Code-Mounting
      - cerebro-data:/app/data
      - cerebro-experiments:/app/data/experiments
```
- Füge `.dockerignore` hinzu, um `__pycache__` und `.pyc` auszuschließen
- Dokumentiere, wann Rebuild nötig ist (Dependencies-Änderungen)

**Erfolgskriterium:**
- Code-Änderungen werden sofort im Container reflektiert
- `docker compose restart` reicht für Code-Updates

---

### PHASE 4: LOGGING-VERBESSERUNG

**Ziele:**
1. Stelle sicher, dass alle DEBUG-Logs erscheinen
2. Füge strukturiertes Logging hinzu
3. Implementiere Request-Tracing

**Aktionen:**
- Prüfe Logging-Konfiguration in `main.py`
- Stelle sicher, dass alle Logger auf DEBUG-Level sind
- Füge Request-ID zu allen Logs hinzu
- Implementiere Flush-Mechanismus für Logs

**Code:**
```python
# In main.py:
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Force flush after each log:
for handler in logging.root.handlers:
    handler.flush = lambda: sys.stdout.flush()
```

**Erfolgskriterium:**
- Alle DEBUG-Logs erscheinen in `docker compose logs`
- Logs sind chronologisch und vollständig

---

### PHASE 5: ERROR-HANDLING-VERBESSERUNG

**Ziele:**
1. Fange alle Exceptions mit vollständigem Traceback
2. Logge detaillierte Fehlerinformationen
3. Sende Fehler über WebSocket an Frontend

**Aktionen:**
- Füge `traceback.format_exc()` zu allen Exception-Handlern hinzu
- Implementiere Fehler-Aggregation
- Sende Fehler-Events über WebSocket

**Code:**
```python
import traceback

async def _run_experiment_with_error_handling(config: ExperimentConfig):
    try:
        logger.info(f"[TASK] Starting experiment {config.experiment_id}")
        await orchestrator.run_experiment(config)
        logger.info(f"[TASK] Completed experiment {config.experiment_id}")
    except Exception as e:
        logger.error(f"[TASK] Experiment {config.experiment_id} FAILED")
        logger.error(f"[TASK] Exception type: {type(e).__name__}")
        logger.error(f"[TASK] Exception message: {str(e)}")
        logger.error(f"[TASK] Full traceback:\n{traceback.format_exc()}")
        
        # Update status
        async with AsyncSessionLocal() as error_session:
            error_repo = ExperimentRepository(error_session)
            await error_repo.update_status(config.experiment_id, ExperimentStatus.FAILED.value)
            await error_session.commit()
        
        # Send error to frontend
        try:
            from api.websocket import send_error
            await send_error(
                experiment_id=config.experiment_id,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=traceback.format_exc()
            )
        except:
            pass
```

**Erfolgskriterium:**
- Alle Fehler werden mit vollständigem Traceback geloggt
- Frontend erhält Fehler-Notifications

---

### PHASE 6: INTEGRATION-TEST

**Ziele:**
1. Verifiziere, dass Experimente wieder starten
2. Prüfe, dass Iterationen ausgeführt werden
3. Validiere End-to-End-Flow

**Aktionen:**
- Starte ein Test-Experiment mit 1 Prompt, 2 Iterationen
- Verifiziere Logs:
  - "run_experiment CALLED"
  - "Starting _run_pair_loop"
  - "Iteration 1 started"
  - "Mutation successful"
  - "Target LLM response received"
  - "Judge evaluation complete"
- Prüfe Datenbank:
  - Experiment Status = COMPLETED oder RUNNING
  - AttackIterations werden erstellt
  - JudgeScores werden gespeichert

**Erfolgskriterium:**
- Mindestens 1 Iteration wird erfolgreich ausgeführt
- Experiment-Status ist NICHT sofort FAILED

---

### PHASE 7: ROLLBACK-STRATEGIE (Falls nötig)

**Falls alle Fixes fehlschlagen:**

1. **Git-History prüfen:**
   - Finde letzten funktionierenden Commit
   - Identifiziere problematische Änderungen
   - Selektives Rollback

2. **Minimale Wiederherstellung:**
   - Stelle nur `backend/api/scans.py` wieder her
   - Behalte Template-Fixes
   - Behalte Enum-Konvertierung

3. **Dokumentiere Lessons Learned:**
   - Was hat das System kaputt gemacht?
   - Wie können wir solche Regressionen verhindern?

---

## ERFOLGSKRITERIEN FÜR GESAMTE MISSION

✅ **Primär:**
- Experimente starten und führen Iterationen aus
- `run_experiment()` wird aufgerufen
- Mindestens 1 erfolgreiche Iteration pro Experiment

✅ **Sekundär:**
- Alle DEBUG-Logs erscheinen
- Fehler werden mit Traceback geloggt
- Live-Code-Updates funktionieren

✅ **Tertiär:**
- System ist stabiler als vor den Fixes
- Dokumentation ist aktualisiert
- Tests sind hinzugefügt

---

## WICHTIGE HINWEISE

1. **Nicht überstürzen:** Jede Phase einzeln durchführen und testen
2. **Logging ist König:** Mehr Logs = schnellere Diagnose
3. **Kleine Schritte:** Lieber 10 kleine Commits als 1 großer
4. **Testen nach jedem Schritt:** Nicht mehrere Änderungen auf einmal
5. **Dokumentieren:** Jede Änderung in PHASE_REPORTS festhalten

---

## DATEIEN ZUM PRÜFEN

**Kritisch:**
- `backend/api/scans.py` (Task-Erstellung)
- `backend/core/orchestrator.py` (run_experiment)
- `docker-compose.yml` (Volume-Mounts)
- `backend/main.py` (Logging-Konfiguration)

**Wichtig:**
- `backend/core/models.py` (AttackStrategyType Enum)
- `backend/api/websocket.py` (Error-Broadcasting)
- `backend/utils/logging.py` (Logger-Setup)

---

## DEBUGGING-BEFEHLE

```bash
# Logs in Echtzeit verfolgen
docker compose logs cerebro-backend --tail=100 --follow

# Nach spezifischen Logs suchen
docker compose logs cerebro-backend | grep -E "(run_experiment|TASK|DEBUG)"

# Container-Status prüfen
docker compose ps

# In Container einloggen
docker compose exec cerebro-backend bash

# Python-Cache löschen (falls nötig)
docker compose exec cerebro-backend find /app -name "*.pyc" -delete
docker compose exec cerebro-backend find /app -name "__pycache__" -type d -exec rm -rf {} +

# Image neu bauen (nur wenn Volume-Mount nicht funktioniert)
docker compose build cerebro-backend --no-cache
docker compose up -d cerebro-backend
```

---

## ERWARTETES ERGEBNIS

Nach erfolgreicher Durchführung aller Phasen:

1. **Experiment startet:**
   ```
   INFO: POST /api/scan/start HTTP/1.1 200 OK
   [TASK] Starting experiment abc-123
   [DEBUG] ========== run_experiment CALLED ==========
   [DEBUG] experiment_id: abc-123
   ```

2. **Iterationen laufen:**
   ```
   [DEBUG] Starting _run_pair_loop for prompt: ...
   [Iteration 1] Strategy: DIRECT_INJECTION
   [Mutation] Generated prompt with template
   [Target] Response received (250 tokens)
   [Judge] Score: 7/10
   ```

3. **Experiment endet:**
   ```
   Experiment abc-123 marked as COMPLETED: 2 successful attacks
   [Strategy Summary] Selected=16, Used=5, Skipped=11
   ```

---

## KONTAKT BEI PROBLEMEN

Falls TRAYCER nicht weiterkommt:
1. Dokumentiere alle durchgeführten Schritte
2. Sammle alle relevanten Logs
3. Erstelle einen detaillierten Bug-Report
4. Erwäge Rollback zu letztem funktionierenden Stand

---

**VIEL ERFOLG, TRAYCER! 🚀**
```

---

## 📝 ZUSÄTZLICHE NOTIZEN

### Was funktioniert noch:
- ✅ Frontend lädt und zeigt UI
- ✅ API-Endpoints antworten
- ✅ Datenbank-Operationen funktionieren
- ✅ WebSocket-Verbindungen werden aufgebaut
- ✅ Template-System ist vollständig

### Was defekt ist:
- ❌ Experiment-Execution
- ❌ Background-Task-Scheduling
- ❌ Iteration-Loop
- ❌ LLM-Calls (werden nie erreicht)
- ❌ Vulnerability-Detection (keine Iterationen = keine Vulnerabilities)

### Kritischer Pfad zur Reparatur:
1. **Sofort:** Fix Task-Scheduling (Phase 2)
2. **Dann:** Verbessere Logging (Phase 4)
3. **Danach:** Volume-Mounting (Phase 3)
4. **Zuletzt:** Error-Handling (Phase 5)

---

**ENDE DES REPORTS**
