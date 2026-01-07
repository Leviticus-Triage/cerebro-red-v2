# Database Setup - CEREBRO-RED v2

## Problem: `unable to open database file`

Dieser Fehler tritt auf, wenn:
1. Das Verzeichnis für die Datenbank nicht existiert
2. Keine Schreibrechte auf das Verzeichnis bestehen
3. Der Pfad in der DATABASE_URL falsch ist

## Lösung

### 1. Verzeichnisse erstellen

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2
mkdir -p data/experiments data/audit_logs data/results
```

### 2. Database initialisieren

```bash
cd backend
alembic upgrade head
```

**Hinweis:** `alembic/env.py` wurde aktualisiert, um automatisch das Verzeichnis zu erstellen, falls es nicht existiert.

### 3. Verifizieren

```bash
ls -la ../data/experiments/
# Sollte zeigen: cerebro.db
```

## Konfiguration

Die DATABASE_URL ist standardmäßig:
```
sqlite+aiosqlite:///./data/experiments/cerebro.db
```

Dies kann in `.env` überschrieben werden:
```bash
DATABASE_URL=sqlite+aiosqlite:///./data/experiments/cerebro.db
```

## Automatische Verzeichnis-Erstellung

`alembic/env.py` wurde erweitert, um:
- Die DATABASE_URL aus Settings zu holen, falls nicht in `alembic.ini`
- Das Verzeichnis automatisch zu erstellen, falls es nicht existiert
- Sowohl für `run_migrations_offline()` als auch `run_async_migrations()`

## Troubleshooting

### Fehler: "unable to open database file"

1. **Prüfen Sie die Berechtigungen:**
   ```bash
   ls -la data/experiments/
   touch data/experiments/test.db && rm data/experiments/test.db
   ```

2. **Prüfen Sie den Pfad:**
   ```bash
   cat backend/alembic.ini | grep sqlalchemy.url
   ```

3. **Manuell erstellen:**
   ```bash
   mkdir -p data/experiments
   chmod 755 data/experiments
   ```

### Fehler: "ModuleNotFoundError: No module named 'alembic'"

```bash
# Venv aktivieren
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate

# Dependencies installieren
cd backend
pip install -r requirements.txt
```

