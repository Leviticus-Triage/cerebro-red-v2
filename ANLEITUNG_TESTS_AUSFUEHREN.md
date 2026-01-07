# 🧪 CEREBRO-RED v2 - Komplette Test-Anleitung

## ⚠️ WICHTIG: Alle Befehle aus dem `backend/` Verzeichnis ausführen!

---

## 📍 Schritt 1: Verzeichnis wechseln

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
```

**Verifizieren:**
```bash
pwd
# Sollte ausgeben: /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
```

---

## 📦 Schritt 2: Dependencies installieren

### 2.1: Prüfen ob pip verfügbar ist

```bash
pip3 --version
# Oder
python3 -m pip --version
```

### 2.2: Dependencies installieren

```bash
# Aus backend/ Verzeichnis:
pip3 install -r requirements.txt

# Oder mit python3 -m pip:
python3 -m pip install -r requirements.txt
```

**Erwartete Ausgabe:**
```
Collecting fastapi>=0.115.0
  Downloading fastapi-0.115.0-py3-none-any.whl
...
Successfully installed fastapi-0.115.0 uvicorn-0.32.0 pydantic-2.10.0 ...
```

### 2.3: Installation verifizieren

```bash
python3 -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python3 -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python3 -c "import pydantic; print('✅ Pydantic:', pydantic.__version__)"
python3 -c "import litellm; print('✅ LiteLLM installiert')"
python3 -c "import pytest; print('✅ Pytest:', pytest.__version__)"
```

**Alle sollten ohne Fehler ausgeben.**

---

## ⚙️ Schritt 3: Environment konfigurieren

### 3.1: .env Datei erstellen

```bash
# Vom backend/ Verzeichnis aus:
cd ..
cp .env.example .env
```

### 3.2: .env bearbeiten

```bash
nano .env
```

**Wichtige Einstellungen setzen:**
```bash
# LLM Provider
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_ATTACKER=qwen3:8b
OLLAMA_MODEL_TARGET=qwen3:8b
OLLAMA_MODEL_JUDGE=qwen3:14b

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/experiments/cerebro.db

# API Key
API_KEY=your-secret-api-key-change-this
API_KEY_ENABLED=true
```

**Speichern:** `Ctrl+O`, `Enter`, `Ctrl+X`

### 3.3: Zurück ins Backend-Verzeichnis

```bash
cd backend
```

---

## 🗄️ Schritt 4: Database Setup

### 4.1: Verzeichnisse erstellen

```bash
# Aus backend/ Verzeichnis:
mkdir -p ../data/experiments
mkdir -p ../data/audit_logs
mkdir -p ../data/results
```

### 4.2: Alembic Migrations ausführen

```bash
# Aus backend/ Verzeichnis:
alembic upgrade head
```

**Erwartete Ausgabe:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial schema
INFO  [alembic.runtime.migration] Running upgrade 001_initial -> 002_add_judge_score_fields, Add missing judge score fields
```

### 4.3: Database-Verbindung testen

```bash
python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from core.database import init_db

async def test():
    await init_db()
    print('✅ Database initialized successfully')

asyncio.run(test())
"
```

---

## 🔍 Schritt 5: Ollama Setup prüfen

### 5.1: Ollama Status

```bash
ollama list
```

**Erwartete Ausgabe:**
```
NAME        ID              SIZE      MODIFIED
qwen3:8b    500a1f067a9f    5.2 GB    2 weeks ago
```

### 5.2: Fehlende Modelle installieren

```bash
# Falls qwen3:14b fehlt (für Judge):
ollama pull qwen3:14b
```

### 5.3: Ollama Connectivity testen

```bash
curl http://localhost:11434/api/tags
```

**Erwartete Ausgabe:** JSON mit verfügbaren Modellen

**Falls Fehler:**
```bash
# Ollama neu starten (in neuem Terminal)
pkill ollama
ollama serve

# Dann erneut testen:
curl http://localhost:11434/api/tags
```

---

## 🧪 Schritt 6: Tests ausführen

### ⚠️ WICHTIG: Immer aus `backend/` Verzeichnis!

```bash
# Verifizieren Sie Ihr Verzeichnis:
pwd
# Muss sein: /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
```

### 6.1: Ollama Connectivity Test (Phase 9)

```bash
# Aus backend/ Verzeichnis:
pytest tests/test_ollama_connectivity.py -v -s
```

**Erwartete Ausgabe:**
```
========================= test session starts ==========================
collected 3 items

tests/test_ollama_connectivity.py::test_ollama_connection PASSED [ 33%]
✅ Ollama connection successful: qwen3:8b
tests/test_ollama_connectivity.py::test_ollama_all_roles PASSED [ 66%]
✅ Attacker role working: qwen3:8b
✅ Target role working: qwen3:8b
✅ Judge role working: qwen3:14b
tests/test_ollama_connectivity.py::test_ollama_latency PASSED [100%]
✅ Ollama latency: 1234ms

========================= 3 passed in 5.23s ==========================
```

### 6.2: Unit Tests (Phase 11)

```bash
# Alle Unit Tests (ohne E2E und Benchmarks)
pytest tests/ -v --tb=short -k "not e2e and not benchmark"

# Oder einzelne Test-Suites:
pytest tests/test_config.py -v
pytest tests/test_models.py -v
pytest tests/test_database.py -v
pytest tests/test_telemetry.py -v
```

### 6.3: E2E Tests - Single Prompt (Phase 12)

```bash
# Dauert 2-5 Minuten
pytest tests/e2e/test_e2e_ollama_single.py -v -s -m e2e
```

### 6.4: E2E Tests - Batch (Phase 12)

```bash
# Dauert 5-10 Minuten
pytest tests/e2e/test_e2e_ollama_batch.py -v -s -m e2e
```

### 6.5: E2E Tests - All Strategies (Phase 12)

```bash
# Dauert 10-15 Minuten
pytest tests/e2e/test_e2e_ollama_all_strategies.py -v -s -m e2e
```

### 6.6: Benchmark Tests (Phase 14)

```bash
# Throughput
pytest tests/benchmark/test_throughput.py -v -s -m benchmark

# Latency
pytest tests/benchmark/test_latency.py -v -s -m benchmark

# Memory (erfordert psutil)
pip3 install psutil
pytest tests/benchmark/test_memory_usage.py -v -s -m benchmark
```

### 6.7: Security Tests (Phase 15)

```bash
# API Authentication
pytest tests/test_api_auth.py -v

# Input Validation
pytest tests/test_input_validation.py -v

# Secrets Management
pytest tests/test_secrets_management.py -v
```

---

## 🔧 Häufige Probleme und Lösungen

### Problem 1: "ModuleNotFoundError: No module named 'core'"

**Ursache:** Falsches Verzeichnis oder Python-Path nicht gesetzt

**Lösung:**
```bash
# 1. In backend/ Verzeichnis wechseln
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 2. Mit explizitem Python-Path ausführen
PYTHONPATH=. pytest tests/test_ollama_connectivity.py -v -s

# Oder:
python3 -m pytest tests/test_ollama_connectivity.py -v -s
```

### Problem 2: "ModuleNotFoundError: No module named 'fastapi'"

**Ursache:** Dependencies nicht installiert

**Lösung:**
```bash
# Aus backend/ Verzeichnis:
pip3 install -r requirements.txt

# Verifizieren:
python3 -c "import fastapi; print('OK')"
```

### Problem 3: "Connection refused" zu Ollama

**Ursache:** Ollama läuft nicht oder falscher Port

**Lösung:**
```bash
# 1. Ollama Status prüfen
ollama list

# 2. Falls nicht erreichbar, Ollama starten (in neuem Terminal)
ollama serve

# 3. Connectivity testen
curl http://localhost:11434/api/tags

# 4. Falls Port anders, .env anpassen:
# OLLAMA_BASE_URL=http://localhost:11434
```

### Problem 4: "Database locked"

**Ursache:** SQLite-Lock-Dateien vorhanden

**Lösung:**
```bash
# Aus backend/ Verzeichnis:
rm -f ../data/experiments/cerebro.db-shm ../data/experiments/cerebro.db-wal

# Database neu initialisieren
alembic downgrade base
alembic upgrade head
```

### Problem 5: "pytest: command not found"

**Ursache:** pytest nicht installiert

**Lösung:**
```bash
pip3 install pytest pytest-asyncio
```

---

## ✅ Vor jedem Test: Checkliste

Führen Sie diese Befehle aus, bevor Sie Tests starten:

```bash
# 1. Verzeichnis prüfen
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
pwd

# 2. Dependencies prüfen
python3 -c "import fastapi, sqlalchemy, pydantic, litellm, pytest; print('✅ Alle Dependencies OK')"

# 3. Ollama prüfen
ollama list

# 4. .env prüfen
cat ../.env | grep -E "OLLAMA|DATABASE"

# 5. Database prüfen
ls -la ../data/experiments/
```

**Alle sollten erfolgreich sein!**

---

## 🎯 Quick Start (Kopieren & Einfügen)

```bash
# ============================================
# KOMPLETTE SETUP-ANLEITUNG
# ============================================

# 1. Backend-Verzeichnis
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 2. Dependencies installieren
pip3 install -r requirements.txt

# 3. Environment setup
cd ..
cp .env.example .env
# .env bearbeiten: DEFAULT_LLM_PROVIDER=ollama, OLLAMA_BASE_URL=http://localhost:11434
cd backend

# 4. Verzeichnisse erstellen
mkdir -p ../data/experiments ../data/audit_logs ../data/results

# 5. Database initialisieren
alembic upgrade head

# 6. Ollama prüfen
ollama list
# Falls qwen3:14b fehlt: ollama pull qwen3:14b

# 7. Erster Test
pytest tests/test_ollama_connectivity.py -v -s
```

---

## 📊 Erwartete Test-Ergebnisse

### Erfolgreicher Test:

```
========================= test session starts ==========================
platform linux -- Python 3.12.3, pytest-7.4.4
collected 3 items

tests/test_ollama_connectivity.py::test_ollama_connection PASSED [ 33%]
tests/test_ollama_connectivity.py::test_ollama_all_roles PASSED [ 66%]
tests/test_ollama_connectivity.py::test_ollama_latency PASSED [100%]

========================= 3 passed in 5.23s ==========================
```

### Fehlgeschlagener Test:

```
FAILED tests/test_ollama_connectivity.py::test_ollama_connection
AssertionError: assert response is not None
```

**Aktion:** Prüfen Sie Ollama-Connectivity und .env Konfiguration.

---

## 🆘 Support-Checkliste

Wenn Tests fehlschlagen, prüfen Sie:

1. ✅ **Verzeichnis:** `pwd` zeigt `.../backend`
2. ✅ **Dependencies:** `pip3 list | grep fastapi` zeigt FastAPI
3. ✅ **Ollama:** `ollama list` zeigt Modelle
4. ✅ **.env:** `cat ../.env | grep OLLAMA` zeigt Konfiguration
5. ✅ **Database:** `ls ../data/experiments/` zeigt Verzeichnis
6. ✅ **Python-Path:** `PYTHONPATH=. pytest ...` funktioniert

---

## 📝 Zusammenfassung: Wo was ausführen?

| Befehl | Verzeichnis | Zweck |
|--------|-------------|-------|
| `pip3 install -r requirements.txt` | `backend/` | Dependencies installieren |
| `cp .env.example .env` | `cerebro-red-v2/` (Root) | Environment erstellen |
| `alembic upgrade head` | `backend/` | Database initialisieren |
| `ollama list` | Überall | Ollama Status prüfen |
| `pytest tests/...` | `backend/` | Tests ausführen |
| `mkdir -p ../data/...` | `backend/` | Verzeichnisse erstellen |

**Wichtig:** Alle `pytest` Befehle MÜSSEN aus `backend/` ausgeführt werden!

