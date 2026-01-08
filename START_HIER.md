# 🚀 START HIER - CEREBRO-RED v2 Tests ausführen

## ⚠️ WICHTIG: Alle Befehle aus `backend/` Verzeichnis!

---

## 📋 SCHRITT 1: Dependencies installieren

```bash
# 1. In Backend-Verzeichnis wechseln
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 2. Dependencies installieren
pip3 install -r requirements.txt

# 3. Prüfen ob es funktioniert hat
python3 -c "import fastapi; print('✅ FastAPI OK')"
```

**Falls Fehler:** `pip3` durch `python3 -m pip` ersetzen.

---

## 📋 SCHRITT 2: Environment konfigurieren

```bash
# 1. Zurück zum Root (ein Verzeichnis hoch)
cd ..

# 2. .env erstellen
cp .env.example .env

# 3. .env bearbeiten
nano .env
```

**In .env setzen:**
```bash
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_ATTACKER=qwen3:8b
OLLAMA_MODEL_TARGET=qwen3:8b
OLLAMA_MODEL_JUDGE=qwen3:14b
```

**Speichern:** `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# 4. Zurück ins Backend
cd backend
```

---

## 📋 SCHRITT 3: Database initialisieren

```bash
# Aus backend/ Verzeichnis:
mkdir -p ../data/experiments ../data/audit_logs
alembic upgrade head
```

---

## 📋 SCHRITT 4: Ollama prüfen

```bash
# Ollama Status
ollama list

# Falls qwen3:14b fehlt:
ollama pull qwen3:14b

# Connectivity testen
curl http://localhost:11434/api/tags
```

**Falls Ollama nicht läuft:**
```bash
# In neuem Terminal:
ollama serve
```

---

## 📋 SCHRITT 5: Tests ausführen

### ⚠️ WICHTIG: Immer aus `backend/` Verzeichnis!

```bash
# Verifizieren Sie:
pwd
# Muss sein: /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
```

### Test 1: Ollama Connectivity

```bash
pytest tests/test_ollama_connectivity.py -v -s
```

### Test 2: Unit Tests

```bash
pytest tests/test_config.py -v
pytest tests/test_models.py -v
```

### Test 3: E2E Test (dauert 2-5 Minuten)

```bash
pytest tests/e2e/test_e2e_ollama_single.py -v -s -m e2e
```

---

## 🔧 Wenn Tests fehlschlagen

### Fehler: "ModuleNotFoundError: No module named 'core'"

```bash
# Lösung: Mit PYTHONPATH ausführen
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
PYTHONPATH=. pytest tests/test_ollama_connectivity.py -v -s
```

### Fehler: "ModuleNotFoundError: No module named 'fastapi'"

```bash
# Lösung: Dependencies installieren
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
pip3 install -r requirements.txt
```

### Fehler: "Connection refused" zu Ollama

```bash
# Lösung: Ollama starten
ollama serve
# In neuem Terminal testen:
curl http://localhost:11434/api/tags
```

---

## ✅ Quick Check vor Tests

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 1. Verzeichnis OK?
pwd

# 2. Dependencies OK?
python3 -c "import fastapi; print('OK')"

# 3. Ollama OK?
ollama list

# 4. .env OK?
cat ../.env | grep OLLAMA

# 5. Database OK?
ls ../data/experiments/
```

**Wenn alle OK sind, können Sie Tests ausführen!**

