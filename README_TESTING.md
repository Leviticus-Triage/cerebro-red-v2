# 🧪 CEREBRO-RED v2 - Test-Anleitung

## 🚀 Schnellstart (3 Schritte)

### Schritt 1: Setup prüfen

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
python3 check_setup.py
```

**Dieses Script prüft automatisch:**
- ✅ Richtiges Verzeichnis
- ✅ Dependencies installiert
- ✅ .env konfiguriert
- ✅ Ollama läuft
- ✅ Database initialisiert
- ✅ Module importierbar

### Schritt 2: Fehler beheben

Falls `check_setup.py` Fehler zeigt, befolgen Sie die angezeigten Lösungen.

**Häufigste Probleme:**

1. **Dependencies fehlen:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **.env fehlt:**
   ```bash
   cd ..
   cp .env.example .env
   nano .env  # DEFAULT_LLM_PROVIDER=ollama setzen
   cd backend
   ```

3. **Ollama läuft nicht:**
   ```bash
   ollama serve  # In neuem Terminal
   ```

4. **Database nicht initialisiert:**
   ```bash
   mkdir -p ../data/experiments ../data/audit_logs
   alembic upgrade head
   ```

### Schritt 3: Tests ausführen

```bash
# Aus backend/ Verzeichnis:
pytest tests/test_ollama_connectivity.py -v -s
```

---

## 📚 Detaillierte Anleitungen

- **`START_HIER.md`** - Schnelle Schritt-für-Schritt-Anleitung
- **`ANLEITUNG_TESTS_AUSFUEHREN.md`** - Komplette detaillierte Anleitung
- **`TESTING_GUIDE.md`** - Vollständiger Testing-Guide mit allen Phasen

---

## ⚠️ WICHTIG: Verzeichnis

**ALLE Befehle müssen aus diesem Verzeichnis ausgeführt werden:**
```bash
/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
```

**Prüfen Sie immer:**
```bash
pwd
# Muss sein: .../cerebro-red-v2/backend
```

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'core'"

```bash
# Lösung 1: Mit PYTHONPATH
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
PYTHONPATH=. pytest tests/test_ollama_connectivity.py -v -s

# Lösung 2: Mit python3 -m pytest
python3 -m pytest tests/test_ollama_connectivity.py -v -s
```

### "ModuleNotFoundError: No module named 'fastapi'"

```bash
pip3 install -r requirements.txt
```

### "Connection refused" zu Ollama

```bash
# Ollama starten
ollama serve

# In neuem Terminal testen
curl http://localhost:11434/api/tags
```

---

## 📋 Test-Befehle Übersicht

| Test | Befehl | Dauer |
|------|--------|-------|
| Ollama Connectivity | `pytest tests/test_ollama_connectivity.py -v -s` | 5s |
| Unit Tests | `pytest tests/ -v -k "not e2e and not benchmark"` | 30s |
| E2E Single | `pytest tests/e2e/test_e2e_ollama_single.py -v -s -m e2e` | 2-5 min |
| E2E Batch | `pytest tests/e2e/test_e2e_ollama_batch.py -v -s -m e2e` | 5-10 min |
| Benchmarks | `pytest tests/benchmark/ -v -s -m benchmark` | 5-15 min |

**Alle Befehle aus `backend/` Verzeichnis!**

