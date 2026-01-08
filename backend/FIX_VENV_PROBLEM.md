# 🔧 Problem: Falsches Python/Pytest wird verwendet

## Problem

Das System verwendet `/usr/bin/python3` und `/usr/bin/pytest` statt der venv-Versionen.

**Symptome:**
- `ModuleNotFoundError: No module named 'pydantic'`
- Pytest findet keine installierten Packages

## Lösung

### Schritt 1: Venv richtig aktivieren

```bash
# Prüfen Sie, ob venv aktiviert ist
which python3
# Sollte zeigen: /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/python3

# Falls nicht, venv aktivieren:
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate

# Oder falls venv im Projekt ist:
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
source ../../venv/bin/activate
```

### Schritt 2: Verifizieren

```bash
# Prüfen Sie, ob jetzt das richtige Python verwendet wird
which python3
# Sollte zeigen: .../venv/bin/python3

which pytest
# Sollte zeigen: .../venv/bin/pytest

# Prüfen Sie, ob pydantic installiert ist
python3 -c "import pydantic; print('✅ Pydantic:', pydantic.__version__)"
```

### Schritt 3: Dependencies installieren (falls nötig)

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# Mit venv-Python installieren
python3 -m pip install -r requirements.txt

# Oder direkt pip (wenn venv aktiviert)
pip install -r requirements.txt
```

### Schritt 4: Tests ausführen

```bash
# Stellen Sie sicher, dass venv aktiviert ist
# (Sie sollten "(venv)" im Prompt sehen)

cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# Tests mit venv-pytest ausführen
pytest tests/test_provider_comparison.py -v

# Oder explizit mit venv-python
python3 -m pytest tests/test_provider_comparison.py -v
```

## Alternative: Explizit venv-Python verwenden

Falls venv-Aktivierung nicht funktioniert:

```bash
# Direkt venv-Python verwenden
/mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/python3 -m pytest tests/test_provider_comparison.py -v
```

## Quick Fix (Kopieren & Einfügen)

```bash
# 1. Venv aktivieren
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate

# 2. In Backend-Verzeichnis wechseln
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend

# 3. Verifizieren
which python3
python3 -c "import pydantic; print('OK')"

# 4. Tests ausführen
pytest tests/test_provider_comparison.py -v
```

