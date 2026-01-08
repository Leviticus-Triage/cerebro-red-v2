# 🚀 CEREBRO-RED v2 - Quick Start Testing Guide

## ⚠️ WICHTIG: Immer aus dem `backend/` Verzeichnis ausführen!

Alle Befehle müssen aus `/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend` ausgeführt werden.

---

## 📋 Schritt 1: Dependencies installieren

```bash
# 1. In Backend-Verzeichnis wechseln
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Verifizieren
python3 -c "import fastapi; print('✅ FastAPI installiert')"
python3 -c "import sqlalchemy; print('✅ SQLAlchemy installiert')"
python3 -c "import litellm; print('✅ LiteLLM installiert')"
```

**Erwartete Ausgabe:**
```
✅ FastAPI installiert
✅ SQLAlchemy installiert
✅ LiteLLM installiert
```

---

## 📋 Schritt 2: Environment konfigurieren

```bash
# 1. Zurück zum Root-Verzeichnis
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2

# 2. .env erstellen (falls nicht vorhanden)
cp .env.example .env

# 3. .env bearbeiten
nano .env
```

**Wichtige Einstellungen in .env:**
```bash
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_ATTACKER=qwen3:8b
OLLAMA_MODEL_TARGET=qwen3:8b
OLLAMA_MODEL_JUDGE=qwen3:14b

DATABASE_URL=sqlite+aiosqlite:///./data/experiments/cerebro.db
API_KEY=your-secret-api-key-change-this
```

---

## 📋 Schritt 3: Ollama prüfen

```bash
# 1. Ollama Status prüfen
ollama list

# Erwartete Ausgabe:
# NAME        ID              SIZE      MODIFIED
# qwen3:8b    500a1f067a9f    5.2 GB    2 weeks ago

# 2. Falls qwen3:14b fehlt
ollama pull qwen3:14b

# 3. Ollama Connectivity testen
curl http://localhost:11434/api/tags
```

**Falls Ollama nicht läuft:**
```bash
# Ollama starten (in neuem Terminal)
ollama serve
```

---

## 📋 Schritt 4: Database initialisieren

```bash
# 1. Zurück ins Backend-Verzeichnis
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 2. Verzeichnisse erstellen
mkdir -p ../data/experiments ../data/audit_logs ../data/results

# 3. Alembic Migrations ausführen
alembic upgrade head

# Erwartete Ausgabe:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial
# INFO  [alembic.runtime.migration] Running upgrade 001_initial -> 002_add_judge_score_fields
```

---

## 📋 Schritt 5: Tests ausführen

### ⚠️ WICHTIG: Immer aus `backend/` Verzeichnis!

```bash
# Stellen Sie sicher, dass Sie hier sind:
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
pwd
# Sollte ausgeben: /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
```

### 5.1: Ollama Connectivity Test

```bash
# Aus backend/ Verzeichnis:
pytest tests/test_ollama_connectivity.py -v -s

# Erwartete Ausgabe:
# ✅ Ollama connection successful: qwen3:8b
# ✅ Attacker role working: qwen3:8b
# ✅ Target role working: qwen3:8b
# ✅ Judge role working: qwen3:14b
# ✅ Ollama latency: 1234ms
```

### 5.2: Unit Tests

```bash
# Alle Unit Tests (ohne E2E und Benchmarks)
pytest tests/ -v --tb=short -k "not e2e and not benchmark"

# Oder einzelne Test-Suites:
pytest tests/test_config.py -v
pytest tests/test_models.py -v
pytest tests/test_database.py -v
```

### 5.3: E2E Tests (Ollama)

```bash
# Single Prompt Test (dauert 2-5 Minuten)
pytest tests/e2e/test_e2e_ollama_single.py -v -s -m e2e

# Batch Test (dauert 5-10 Minuten)
pytest tests/e2e/test_e2e_ollama_batch.py -v -s -m e2e

# All Strategies Test (dauert 10-15 Minuten)
pytest tests/e2e/test_e2e_ollama_all_strategies.py -v -s -m e2e
```

### 5.4: Benchmark Tests

```bash
# Throughput Benchmark
pytest tests/benchmark/test_throughput.py -v -s -m benchmark

# Latency Benchmark
pytest tests/benchmark/test_latency.py -v -s -m benchmark

# Memory Usage (erfordert psutil)
pip install psutil
pytest tests/benchmark/test_memory_usage.py -v -s -m benchmark
```

### 5.5: Security Tests

```bash
# API Authentication
pytest tests/test_api_auth.py -v

# Input Validation
pytest tests/test_input_validation.py -v

# Secrets Management
pytest tests/test_secrets_management.py -v
```

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'core'"

**Lösung:**
```bash
# 1. Stellen Sie sicher, dass Sie im backend/ Verzeichnis sind
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
pwd

# 2. Mit explizitem Python-Path ausführen
PYTHONPATH=. pytest tests/test_ollama_connectivity.py -v -s
```

### Problem: "ModuleNotFoundError: No module named 'fastapi'"

**Lösung:**
```bash
# Dependencies installieren
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
pip install -r requirements.txt
```

### Problem: "Connection refused" zu Ollama

**Lösung:**
```bash
# Ollama Status prüfen
ollama list

# Falls nicht erreichbar:
pkill ollama
ollama serve

# In neuem Terminal testen:
curl http://localhost:11434/api/tags
```

### Problem: "Database locked"

**Lösung:**
```bash
# SQLite-Lock-Dateien entfernen
rm -f ../data/experiments/cerebro.db-shm ../data/experiments/cerebro.db-wal

# Database neu initialisieren
alembic downgrade base
alembic upgrade head
```

---

## ✅ Checkliste vor Test-Ausführung

- [ ] Im `backend/` Verzeichnis: `pwd` zeigt `/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend`
- [ ] Dependencies installiert: `pip list | grep fastapi` zeigt FastAPI
- [ ] .env Datei existiert und ist konfiguriert
- [ ] Ollama läuft: `ollama list` zeigt Modelle
- [ ] Database initialisiert: `alembic current` zeigt Migrationen
- [ ] Verzeichnisse existieren: `ls ../data/experiments` zeigt Verzeichnis

---

## 🎯 Quick Start (Alles in einem)

```bash
# 1. Backend-Verzeichnis
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Environment setup
cd ..
cp .env.example .env
# .env bearbeiten: DEFAULT_LLM_PROVIDER=ollama

# 4. Database setup
cd backend
mkdir -p ../data/experiments ../data/audit_logs
alembic upgrade head

# 5. Ollama prüfen
ollama list

# 6. Erster Test
pytest tests/test_ollama_connectivity.py -v -s
```

---

## 📞 Bei Problemen

1. **Prüfen Sie das Verzeichnis:** `pwd` muss `.../backend` sein
2. **Prüfen Sie Dependencies:** `pip list | grep -E "fastapi|sqlalchemy|litellm"`
3. **Prüfen Sie Ollama:** `ollama list` und `curl http://localhost:11434/api/tags`
4. **Prüfen Sie .env:** `cat ../.env | grep OLLAMA`

