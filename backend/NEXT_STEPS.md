#  Nächste Schritte - CEREBRO-RED v2

##  Status: Zirkuläre Imports behoben!

Alle kritischen Import-Probleme wurden behoben. Sie können jetzt mit den Tests fortfahren.

---

##  Schritt-für-Schritt Anleitung

### 1⃣ **Venv aktivieren** (wichtig!)

```bash
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate
```

**Verifizieren:**
```bash
which python3
# Sollte zeigen: .../venv/bin/python3
```

---

### 2⃣ **In Backend-Verzeichnis wechseln**

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
```

---

### 3⃣ **Quick Import Test**

```bash
python3 -c "from core.models import ExperimentConfig; from core.mutator import PromptMutator; from core.judge import SecurityJudge; print(' Alle Imports OK')"
```

**Erwartete Ausgabe:** ` Alle Imports OK`

---

### 4⃣ **Tests ausführen**

#### A) Einzelner Test (empfohlen zum Start)

```bash
# Provider Comparison Test (sollte jetzt funktionieren)
pytest tests/test_provider_comparison.py -v
```

#### B) Alle Unit Tests

```bash
# Alle Tests außer E2E und Benchmark
pytest tests/ -v --ignore=tests/e2e --ignore=tests/benchmark
```

#### C) Spezifische Test-Suites

```bash
# Config Tests
pytest tests/test_config.py -v

# Models Tests
pytest tests/test_models.py -v

# Database Tests
pytest tests/test_database.py -v

# Mutator Tests
pytest tests/test_mutator_pair.py -v
```

---

### 5⃣ **E2E Tests (mit Ollama)**

**Voraussetzung:** Ollama muss laufen und Modelle müssen verfügbar sein.

```bash
# Ollama Status prüfen
ollama list

# Falls Modelle fehlen:
ollama pull qwen3:8b
ollama pull qwen3:14b

# E2E Test ausführen (dauert 2-5 Minuten)
pytest tests/e2e/test_e2e_ollama_single.py -v -s
```

---

##  Bekannte Probleme & Lösungen

### Problem: "ModuleNotFoundError: No module named 'core'"

**Lösung:** Stellen Sie sicher, dass Sie im `backend/` Verzeichnis sind:
```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
pytest tests/...
```

### Problem: "ImportError: cannot import name 'ExperimentDB'"

**Lösung:** `ExperimentDB` ist in `core.database`, nicht `core.models`:
```python
from core.database import ExperimentDB  #  Richtig
from core.models import ExperimentDB    #  Falsch
```

### Problem: "ModuleNotFoundError: No module named 'pydantic'"

**Lösung:** Venv ist nicht aktiviert oder Dependencies fehlen:
```bash
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate
pip install -r requirements.txt
```

---

##  Wichtige Hinweise

### Import-Änderungen

Nach den Fixes für zirkuläre Imports müssen Sie folgende Imports verwenden:

```python
#  Richtig:
from core.mutator import PromptMutator
from core.judge import SecurityJudge
from core.database import ExperimentDB, AttackIterationDB, etc.

#  Falsch (funktioniert nicht mehr):
from core import PromptMutator  # Nicht mehr in __init__.py
from core import SecurityJudge  # Nicht mehr in __init__.py
```

### Type Hints

Alle Type-Hints verwenden jetzt `from __future__ import annotations`, daher funktionieren String-Annotations automatisch.

---

##  Erfolgs-Checkliste

- [ ] Venv aktiviert
- [ ] Im `backend/` Verzeichnis
- [ ] Quick Import Test erfolgreich
- [ ] `test_provider_comparison.py` läuft durch
- [ ] Unit Tests laufen durch
- [ ] (Optional) E2E Tests mit Ollama

---

##  Nächste Schritte nach erfolgreichen Tests

1. **Database initialisieren:**
   ```bash
   alembic upgrade head
   ```

2. **Backend starten:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **API testen:**
   ```bash
   curl http://localhost:8000/health
   ```

---

**Viel Erfolg! **

