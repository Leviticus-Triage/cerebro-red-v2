# Terminal Recording Guide

## Übersicht

Dieser Guide zeigt verschiedene Methoden, um Terminal-Sessions während Experiment-Ausführungen aufzuzeichnen.

## Methoden

### 1. `script` (Empfohlen - Einfach & Universell)

**Installation:**
```bash
# Meist bereits installiert auf Linux
which script
```

**Verwendung:**
```bash
# Starte Aufzeichnung
script experiment_session_$(date +%Y%m%d_%H%M%S).log

# Führe deine Befehle aus
cd cerebro-red-v2
docker compose logs -f cerebro-backend
# ... weitere Befehle ...

# Beende Aufzeichnung
exit
```

**Vorteile:**
- ✅ Meist bereits installiert
- ✅ Einfach zu verwenden
- ✅ Erfasst alle Eingaben und Ausgaben
- ✅ Timestamps möglich

**Erweiterte Optionen:**
```bash
# Mit Timestamps
script -t 2>timing.log experiment.log

# Nur Append (nicht überschreiben)
script -a experiment.log

# Flush nach jedem Befehl (für Live-Viewing)
script -f experiment.log
```

### 2. `asciinema` (Modern & Interaktiv)

**Installation:**
```bash
# Ubuntu/Debian
sudo apt-get install asciinema

# Oder via pip
pip install asciinema
```

**Verwendung:**
```bash
# Starte Aufzeichnung
asciinema rec experiment_$(date +%Y%m%d_%H%M%S).cast

# Führe Befehle aus
# ...

# Beende mit Ctrl+D oder 'exit'
```

**Wiedergabe:**
```bash
# Lokal abspielen
asciinema play experiment.cast

# Upload zu asciinema.org (optional)
asciinema upload experiment.cast
```

**Vorteile:**
- ✅ Sehr schöne Wiedergabe
- ✅ Kann online geteilt werden
- ✅ Unterstützt Pausen/Seeking
- ✅ Farben werden erhalten

### 3. `tmux` mit Logging

**Verwendung:**
```bash
# Starte tmux Session
tmux new -s experiment

# Aktiviere Logging
tmux pipe-pane -o "cat >> experiment_$(date +%Y%m%d_%H%M%S).log"

# Führe Befehle aus
# ...

# Beende Session
tmux kill-session -t experiment
```

**Vorteile:**
- ✅ Kann Session später wieder aufnehmen
- ✅ Split-Panes möglich
- ✅ Automatisches Logging

### 4. Einfache Output-Umleitung mit `tee`

**Verwendung:**
```bash
# Alle Ausgaben loggen
exec > >(tee -a experiment.log) 2>&1

# Oder für einzelne Befehle
docker compose logs -f cerebro-backend | tee experiment.log
```

**Vorteile:**
- ✅ Keine zusätzliche Installation
- ✅ Einfach für einzelne Befehle

### 5. Kombiniert: `script` + `tee` (Beste Lösung)

**Verwendung:**
```bash
# Starte script mit tee für Live-Viewing
script -f >(tee experiment.log) | cat
```

## Praktisches Beispiel für Experiment-Aufzeichnung

### Vollständiges Experiment-Recording

```bash
#!/bin/bash
# Vollständiges Experiment-Recording

EXPERIMENT_ID="973bfd76-2687-4c1f-872b-52ad38b22661"
LOG_FILE="experiment_${EXPERIMENT_ID}_$(date +%Y%m%d_%H%M%S).log"

echo "=== Experiment Recording Start ===" | tee "$LOG_FILE"
echo "Experiment ID: $EXPERIMENT_ID" | tee -a "$LOG_FILE"
echo "Start Time: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Starte script mit tee für Live-Viewing
script -f >(tee -a "$LOG_FILE") << 'SCRIPT_END'

# 1. Backend Logs überwachen
echo "=== Starting Backend Logs ==="
docker compose logs -f cerebro-backend &
BACKEND_LOG_PID=$!

# 2. Frontend Logs überwachen (optional)
echo "=== Starting Frontend Logs ==="
docker compose logs -f cerebro-frontend &
FRONTEND_LOG_PID=$!

# 3. Experiment Status abfragen
echo "=== Experiment Status ==="
curl -H "X-API-Key: test" http://localhost:9000/api/scan/status/$EXPERIMENT_ID | jq .

# 4. Warte auf Experiment-Ende (Ctrl+C zum Beenden)
echo "=== Monitoring Experiment (Press Ctrl+C to stop) ==="
wait

# Cleanup
kill $BACKEND_LOG_PID $FRONTEND_LOG_PID 2>/dev/null

SCRIPT_END

echo "" | tee -a "$LOG_FILE"
echo "=== Experiment Recording End ===" | tee -a "$LOG_FILE"
echo "End Time: $(date)" | tee -a "$LOG_FILE"
```

## Empfohlene Workflow

### Für Einzelne Experimente:

```bash
# 1. Starte Recording
script experiment_$(date +%Y%m%d_%H%M%S).log

# 2. Führe Experiment aus
cd cerebro-red-v2
docker compose logs -f cerebro-backend

# 3. In anderem Terminal: Experiment starten
# (im Frontend oder via API)

# 4. Beende Recording
exit
```

### Für Automatisiertes Monitoring:

```bash
# Verwende das bereitgestellte Script
./scripts/record_experiment.sh [experiment_id] [output_file]
```

## Tipps

1. **Timestamps hinzufügen:**
   ```bash
   script -t 2>timing.log experiment.log
   ```

2. **Kompression für große Logs:**
   ```bash
   script experiment.log
   # ... Befehle ...
   exit
   gzip experiment.log
   ```

3. **Live-Viewing während Recording:**
   ```bash
   script -f >(tee experiment.log) | cat
   ```

4. **Nur bestimmte Befehle loggen:**
   ```bash
   docker compose logs -f cerebro-backend | tee -a experiment.log
   ```

## Dateigrößen

- **script**: ~1-5 MB pro Stunde (je nach Output)
- **asciinema**: ~500 KB - 2 MB pro Stunde
- **tmux**: Ähnlich wie script

## Beispiel-Output-Struktur

```
experiments/
├── recordings/
│   ├── experiment_20251230_173000.log
│   ├── experiment_20251230_180000.cast
│   └── experiment_20251230_190000.log.gz
```

## Troubleshooting

**Problem: `script` nicht gefunden**
```bash
# Ubuntu/Debian
sudo apt-get install bsdutils

# Oder verwende asciinema
```

**Problem: Zu große Log-Dateien**
```bash
# Komprimiere nach Recording
gzip experiment.log

# Oder verwende Rotation
script -a experiment_$(date +%Y%m%d_%H%M%S).log
```

**Problem: Farben gehen verloren**
```bash
# Verwende asciinema für bessere Farbunterstützung
asciinema rec experiment.cast
```
