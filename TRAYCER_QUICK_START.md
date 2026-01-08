# 🚀 TRAYCER QUICK START - CEREBRO-RED v2 Reparatur

## 🎯 MISSION
Repariere das CEREBRO-RED v2 System, das nach Debugging-Versuchen komplett defekt ist.

## 🔴 HAUPTPROBLEM
**Experimente starten nicht mehr!**
- API gibt 200 OK zurück
- Experiment wird in DB erstellt
- Sofort als FAILED markiert
- KEINE Iterationen werden ausgeführt
- `run_experiment()` wird NIE aufgerufen

## 🐛 ROOT CAUSE
```python
# backend/api/scans.py, Zeile 167:
asyncio.create_task(_run_experiment_with_error_handling(experiment_config))
```

**Problem:** Task wird erstellt, aber ohne Referenz vom Garbage Collector gelöscht!

## ✅ VERSUCHTER FIX (UNGETESTET!)
```python
# Hinzugefügt:
background_tasks_set = set()

# Geändert zu:
task = asyncio.create_task(_run_experiment_with_error_handling(experiment_config))
background_tasks_set.add(task)
task.add_done_callback(background_tasks_set.discard)
logger.info(f"[start_scan] Created background task for experiment {experiment_id}")
```

## 🔧 SOFORT-AKTION

### 1. TESTE DEN FIX
```bash
cd cerebro-red-v2

# Image wurde bereits neu gebaut und gestartet
# Starte ein Test-Experiment im Browser

# Prüfe Logs:
docker compose logs cerebro-backend --tail=100 --follow | grep -E "(start_scan|run_experiment|TASK)"
```

**Erwartete Logs wenn FIX funktioniert:**
```
[start_scan] Created background task for experiment abc-123
[TASK] Starting experiment abc-123
[DEBUG] ========== run_experiment CALLED ==========
```

**Wenn NICHT funktioniert (keine Logs):**
→ Gehe zu Alternative Fixes unten

---

## 🔄 ALTERNATIVE FIXES (Falls Task-Set nicht funktioniert)

### Option A: FastAPI BackgroundTasks (EMPFOHLEN)
```python
# backend/api/scans.py

@router.post("/start", dependencies=[Depends(verify_api_key)])
async def start_scan(
    request: ScanStartRequest,
    background_tasks: BackgroundTasks,  # FastAPI's BackgroundTasks
    orchestrator: RedTeamOrchestrator = Depends(get_orchestrator),
    session: AsyncSession = Depends(get_session)
):
    experiment_config = request.experiment_config
    experiment_id = experiment_config.experiment_id
    
    # ... validation code ...
    
    # Use FastAPI's BackgroundTasks (handles lifecycle automatically)
    background_tasks.add_task(
        orchestrator.run_experiment,
        experiment_config
    )
    
    return api_response({
        "experiment_id": experiment_id,
        "status": "started",
        "message": "Experiment started in background."
    })
```

**Vorteil:** FastAPI managed Task-Lifecycle automatisch!

### Option B: Task-Manager im Orchestrator
```python
# backend/core/orchestrator.py

class RedTeamOrchestrator:
    def __init__(self, ...):
        # ... existing code ...
        self._running_tasks: Dict[UUID, asyncio.Task] = {}
    
    def start_experiment_background(self, config: ExperimentConfig):
        """Start experiment as background task with proper reference."""
        task = asyncio.create_task(self.run_experiment(config))
        self._running_tasks[config.experiment_id] = task
        
        # Cleanup when done
        def cleanup(t):
            self._running_tasks.pop(config.experiment_id, None)
            if t.exception():
                logger.error(f"Task failed: {t.exception()}")
        
        task.add_done_callback(cleanup)
        return task

# backend/api/scans.py

@router.post("/start", ...)
async def start_scan(...):
    # ... validation ...
    
    # Use orchestrator's task manager
    orchestrator.start_experiment_background(experiment_config)
    
    return api_response(...)
```

**Vorteil:** Zentrales Task-Management, besseres Monitoring!

### Option C: Synchrones Warten (NICHT EMPFOHLEN, nur für Testing)
```python
# backend/api/scans.py

@router.post("/start", ...)
async def start_scan(...):
    # ... validation ...
    
    # Run synchronously (blocks API, nur für Testing!)
    try:
        result = await orchestrator.run_experiment(experiment_config)
        return api_response({
            "experiment_id": experiment_id,
            "status": "completed",
            "result": result
        })
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Vorteil:** Garantiert Ausführung, einfach zu debuggen
**Nachteil:** API blockiert, nicht produktionsreif!

---

## 📊 DEBUGGING-STRATEGIE

### Schritt 1: Verifiziere Task-Erstellung
```python
# In backend/api/scans.py, nach asyncio.create_task():

logger.info(f"[DEBUG] Task created: {task}")
logger.info(f"[DEBUG] Task done: {task.done()}")
logger.info(f"[DEBUG] Task cancelled: {task.cancelled()}")
logger.info(f"[DEBUG] Current event loop: {asyncio.get_event_loop()}")
logger.info(f"[DEBUG] All tasks: {len(asyncio.all_tasks())}")
```

### Schritt 2: Verifiziere Task-Ausführung
```python
# In _run_experiment_with_error_handling(), ERSTE ZEILE:

async def _run_experiment_with_error_handling(config: ExperimentConfig):
    logger.info(f"[TASK-START] ===== WRAPPER CALLED for {config.experiment_id} =====")
    logger.info(f"[TASK-START] Thread: {threading.current_thread().name}")
    logger.info(f"[TASK-START] Event loop: {asyncio.get_event_loop()}")
    
    try:
        logger.info(f"[TASK-START] About to call run_experiment...")
        await orchestrator.run_experiment(config)
        logger.info(f"[TASK-END] run_experiment completed successfully")
    except Exception as e:
        logger.error(f"[TASK-ERROR] Exception: {type(e).__name__}: {str(e)}")
        logger.error(f"[TASK-ERROR] Traceback:\n{traceback.format_exc()}")
        # ... rest of error handling ...
```

### Schritt 3: Prüfe Event-Loop-Status
```python
# In backend/main.py oder startup:

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    logger.info(f"[STARTUP] Event loop: {loop}")
    logger.info(f"[STARTUP] Loop running: {loop.is_running()}")
    logger.info(f"[STARTUP] Loop closed: {loop.is_closed()}")
```

---

## 🎯 ERFOLGSKRITERIEN

### Minimum (MUSS funktionieren):
- ✅ `run_experiment()` wird aufgerufen
- ✅ Mindestens 1 Iteration wird ausgeführt
- ✅ Experiment-Status ist NICHT sofort FAILED

### Optimal (SOLLTE funktionieren):
- ✅ Alle Iterationen werden ausgeführt
- ✅ Vulnerabilities werden gefunden
- ✅ Statistiken sind korrekt

---

## 📝 NÄCHSTE SCHRITTE

1. **TESTE aktuellen Fix:**
   - Starte Experiment im Browser
   - Prüfe Logs nach "[start_scan] Created background task"
   - Prüfe Logs nach "[DEBUG] run_experiment CALLED"

2. **WENN NICHT funktioniert:**
   - Implementiere Option A (FastAPI BackgroundTasks)
   - Teste erneut

3. **WENN FUNKTIONIERT:**
   - Dokumentiere in Phase-Report
   - Fahre fort mit Logging-Verbesserungen
   - Implementiere Volume-Mounting

---

## 🔗 VOLLSTÄNDIGE DOKUMENTATION

Siehe `BUG_REPORT_AND_TRAYCER_PROMPT.md` für:
- Detaillierte Fehleranalyse
- 7 Phasen-Plan
- Alle alternativen Lösungen
- Rollback-Strategie

---

## ⚡ QUICK COMMANDS

```bash
# Logs verfolgen
docker compose logs cerebro-backend --tail=100 --follow

# Nach spezifischen Logs suchen
docker compose logs cerebro-backend | grep -E "(TASK|run_experiment|start_scan)"

# Image neu bauen (falls Code geändert)
docker compose build cerebro-backend --no-cache
docker compose up -d cerebro-backend

# In Container einloggen
docker compose exec cerebro-backend bash

# Python-Cache löschen
docker compose exec cerebro-backend find /app -name "*.pyc" -delete
```

---

**VIEL ERFOLG! 🚀**

Bei Fragen oder Problemen: Siehe vollständige Dokumentation in `BUG_REPORT_AND_TRAYCER_PROMPT.md`
