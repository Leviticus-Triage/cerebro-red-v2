# Test-Fixes Zusammenfassung

## ✅ Behobene Probleme

### 1. JudgeScore Model erweitert
- ✅ `logical_consistency_score` hinzugefügt
- ✅ `sycophancy_score` hinzugefügt
- **Datei:** `backend/core/models.py`

### 2. SecurityJudge experiment_id optional
- ✅ `experiment_id` ist jetzt optional mit Default `uuid4()`
- **Datei:** `backend/core/judge.py`
- **Grund:** Viele Tests rufen `SecurityJudge()` ohne `experiment_id` auf

### 3. test_mutator_pair.py Fixes
- ✅ `test_analyze_feedback_custom_thresholds`: `threshold_used` korrigiert (tau_2 → tau_1 für mittleren Bereich)
- ✅ `test_missing_feedback_keys`: Error-Message korrigiert (singular → plural)
- ✅ `test_feedback_validation_in_mutate`: Validierung VOR try-except Block verschoben
- **Datei:** `backend/core/mutator.py`

### 4. Database-Verzeichnis erstellt
- ✅ `data/experiments/` erstellt
- ✅ `data/audit_logs/` erstellt
- ✅ `data/results/` erstellt

### 5. Scoring-Definitionen korrigiert
- ✅ `score_to_likert(2.0)`: Grenzen korrigiert (`<` → `<=`)
- ✅ `detect_refusal_patterns`: Reihenfolge der Checks korrigiert (partial vor standard)
- **Datei:** `backend/core/scoring.py`

## ⚠️ Bekannte Probleme (nicht behoben)

### 1. Ollama-URL
- **Problem:** Tests verwenden `host.docker.internal:11434`, aber lokal sollte es `localhost:11434` sein
- **Lösung:** In `.env` Datei konfigurieren: `OLLAMA_BASE_URL=http://localhost:11434`
- **Status:** Konfigurierbar, kein Code-Fix nötig

### 2. Weitere Test-Fehler
- Einige Tests schlagen noch fehl (z.B. `test_orchestrator_phase_5_5_compliance`, `test_integration_mock`)
- Diese benötigen weitere Untersuchung

## 📝 Nächste Schritte

1. **Ollama-URL konfigurieren:**
   ```bash
   cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2
   echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
   ```

2. **Database initialisieren:**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Tests erneut ausführen:**
   ```bash
   pytest tests/test_mutator_pair.py -v
   pytest tests/test_scoring_definitions.py -v
   ```

