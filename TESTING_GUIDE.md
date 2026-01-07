# 🧪 Testing & Logging Guide - Phase 4 Features

## 🚀 System Start

### Container Status prüfen
```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2
docker compose ps
```

### Alle Services neu starten
```bash
docker compose down
docker compose build --no-cache cerebro-frontend  # Frontend neu bauen
docker compose up -d
```

### Einzelne Services neu starten
```bash
docker compose restart cerebro-backend
docker compose restart cerebro-frontend
```

---

## 📊 Logging

### Backend Logs (Live)
```bash
# Alle Backend-Logs
docker compose logs -f cerebro-backend

# Nur WebSocket/Verbosity-Logs (mit Debug-Level)
docker compose logs -f cerebro-backend | grep -i "verbosity\|websocket\|broadcast\|filtered"

# Nur Errors
docker compose logs -f cerebro-backend | grep -i "error\|exception\|traceback"
```

### Frontend Logs
```bash
# Frontend-Logs
docker compose logs -f cerebro-frontend

# Build-Logs
docker compose logs cerebro-frontend | grep -i "build\|vite\|error"
```

### Database Logs
```bash
# Die Datenbank ist SQLite und läuft im Backend-Container
# Datenbank-Logs sind Teil der Backend-Logs:
docker compose logs -f cerebro-backend | grep -i "database\|sqlite\|db"
# Datenbank-Datei befindet sich im Volume: cerebro-data
```

### Alle Logs gleichzeitig
```bash
docker compose logs -f
```

---

## 🧪 Testing - Phase 4 Features

### 1. VerbositySelector Komponente testen

**Wo:** Frontend - Experiment Monitor Page
**URL:** http://localhost:3000/monitor/{experiment_id}

**Test-Schritte:**
1. Navigiere zu einem laufenden Experiment
2. **Verbosity-Dropdown prüfen:**
   - Dropdown sollte 4 Optionen zeigen (🔇 Silent, 🔊 Basic, 📊 Detailed, 🐛 Debug)
   - Aktuelles Level sollte mit Badge angezeigt werden
   - Dropdown sollte disabled sein, wenn nicht verbunden

**Browser Console prüfen:**
```javascript
// Öffne Browser DevTools (F12)
// Console Tab
// Prüfe auf Fehler:
// - "VerbositySelector is not defined" → Import-Problem
// - "Cannot read property 'value' of undefined" → Props-Problem
```

**Logs prüfen:**
```bash
# Frontend-Logs für React-Fehler
docker compose logs cerebro-frontend | grep -i "error\|warning"
```

---

### 2. Verbosity-Filterung testen

**Wo:** Backend WebSocket + Frontend Live Logs

**Test-Schritte:**

#### A) Verbosity Level 0 (Silent)
1. Setze Verbosity auf **0** im Dropdown
2. **Erwartung:**
   - Nur **Errors**-Tab sollte Events zeigen
   - Requests/Responses/Judge-Tabs sollten leer sein
   - Code Flow-Tab sollte leer sein

**Backend-Logs prüfen:**
```bash
docker compose logs -f cerebro-backend | grep -i "WS Filtered\|WS Broadcast"
# Sollte zeigen: "WS Filtered: llm_request for connection (verbosity 0 < 2)"
```

#### B) Verbosity Level 2 (Detailed)
1. Setze Verbosity auf **2** im Dropdown
2. **Erwartung:**
   - **Requests**-Tab sollte LLM-Requests zeigen
   - **Responses**-Tab sollte LLM-Responses zeigen
   - **Judge**-Tab sollte Judge-Evaluations zeigen
   - **Code Flow**-Tab sollte leer sein (benötigt Level 3)

**Backend-Logs prüfen:**
```bash
docker compose logs -f cerebro-backend | grep -i "WS Broadcast.*llm_request"
# Sollte zeigen: "WS Broadcast: llm_request to connection (verbosity 2 >= 2)"
```

#### C) Verbosity Level 3 (Debug)
1. Setze Verbosity auf **3** im Dropdown
2. **Erwartung:**
   - **Code Flow**-Tab sollte Events zeigen
   - Alle anderen Tabs sollten auch Events zeigen

**Backend-Logs prüfen:**
```bash
docker compose logs -f cerebro-backend | grep -i "WS Broadcast.*code_flow"
# Sollte zeigen: "WS Broadcast: code_flow to connection (verbosity 3 >= 3)"
```

---

### 3. Expand All / Collapse All testen

**Wo:** Frontend - Live Logs Panel

**Test-Schritte:**
1. Navigiere zu Live Logs Tab
2. Klicke auf **"📤 Expand All"** Button
3. **Erwartung:**
   - Alle sichtbaren Rows sollten expandiert sein
   - Button sollte zu **"📥 Collapse All"** wechseln
   - Syntax-Highlighting sollte sichtbar sein

4. Klicke auf **"📥 Collapse All"**
5. **Erwartung:**
   - Alle Rows sollten kollabiert sein
   - Button sollte zu **"📤 Expand All"** wechseln

**Browser Console prüfen:**
```javascript
// Prüfe auf Performance-Warnungen
// Sollte keine "Maximum update depth exceeded" Fehler geben
```

---

### 4. Keyboard-Navigation testen

**Wo:** Frontend - Live Logs Tabellen

**Test-Schritte:**
1. Navigiere zu einem Tab mit Logs (z.B. Requests)
2. **Tab**-Taste drücken, um erste Row zu fokussieren
3. **Enter**-Taste drücken
4. **Erwartung:**
   - Row sollte expandieren
   - Syntax-Highlighting sollte erscheinen

5. **Enter**-Taste erneut drücken
6. **Erwartung:**
   - Row sollte kollabieren

**Browser Console prüfen:**
```javascript
// Prüfe auf Keyboard-Event-Fehler
// Sollte keine "Cannot read property 'preventDefault'" Fehler geben
```

---

### 5. Copy-to-Clipboard testen

**Wo:** Frontend - Expandierte Rows

**Test-Schritte:**
1. Expandiere eine Row (z.B. Request oder Response)
2. Klicke auf **"📋 Copy"** Button
3. **Erwartung:**
   - Vollständiger Inhalt sollte in Clipboard kopiert sein
   - Keine Fehler in Console

4. Paste in Editor (Strg+V)
5. **Erwartung:**
   - Vollständiger Prompt/Response sollte sichtbar sein

**Browser Console prüfen:**
```javascript
// Prüfe auf Clipboard-API-Fehler
// Sollte keine "Failed to copy" Fehler geben
```

**Hinweis:** Clipboard-API benötigt HTTPS oder localhost. Funktioniert auf http://localhost:3000.

---

### 6. Backend Verbosity Clamping testen

**Wo:** Backend WebSocket

**Test-Schritte:**

#### A) Via WebSocket Control Message
```javascript
// Im Browser Console (wenn WebSocket verbunden):
// Verbosity auf ungültigen Wert setzen
websocket.send("set_verbosity:5");  // Sollte auf 3 geclammpt werden
websocket.send("set_verbosity:-1"); // Sollte auf 0 geclammpt werden
```

**Backend-Logs prüfen:**
```bash
docker compose logs -f cerebro-backend | grep -i "set_verbosity"
# Sollte keine ValueError zeigen
```

#### B) Via Query Parameter
```bash
# WebSocket mit ungültigem Verbosity-Level verbinden
# Sollte automatisch geclammpt werden
```

---

## 🐛 Debugging

### Frontend-Fehler finden

**Browser DevTools:**
1. Öffne DevTools (F12)
2. **Console Tab:**
   - Prüfe auf rote Fehler
   - Prüfe auf gelbe Warnungen
3. **Network Tab:**
   - Prüfe WebSocket-Verbindung (ws://localhost:9000/ws/scan/...)
   - Prüfe API-Calls auf 404/500 Errors
4. **React DevTools:**
   - Installiere React DevTools Extension
   - Prüfe Component Props und State

**Frontend-Logs:**
```bash
docker compose logs cerebro-frontend | tail -100
```

---

### Backend-Fehler finden

**Backend-Logs:**
```bash
# Alle Logs
docker compose logs cerebro-backend | tail -100

# Nur Errors
docker compose logs cerebro-backend | grep -i "error\|exception\|traceback" | tail -50

# WebSocket-spezifische Logs
docker compose logs cerebro-backend | grep -i "websocket\|verbosity" | tail -50

# Debug-Logs (wenn DEBUG=True in .env)
docker compose logs cerebro-backend | grep -i "DEBUG" | tail -50
```

**Backend-Health prüfen:**
```bash
curl http://localhost:9000/health
# Sollte {"status": "healthy", ...} zurückgeben
```

---

### WebSocket-Verbindung testen

**Browser Console:**
```javascript
// WebSocket-Status prüfen
// In ExperimentMonitor.tsx sollte WebSocket automatisch verbinden
// Prüfe in Browser Console:
console.log(wsClient);  // Sollte WebSocket-Client-Objekt zeigen

// Manuell verbinden (falls nötig):
const ws = new WebSocket('ws://localhost:9000/ws/scan/{experiment_id}?verbosity=2');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.onerror = (e) => console.error('Error:', e);
```

**Backend-Logs:**
```bash
docker compose logs -f cerebro-backend | grep -i "websocket\|connected\|disconnected"
```

---

## 📝 Test-Checkliste

### VerbositySelector
- [ ] Dropdown zeigt alle 4 Levels
- [ ] Badge zeigt aktuelles Level
- [ ] Disabled wenn nicht verbunden
- [ ] onChange wird aufgerufen bei Änderung

### Verbosity-Filterung
- [ ] Level 0: Nur Errors sichtbar
- [ ] Level 1: + Events sichtbar
- [ ] Level 2: + LLM I/O sichtbar
- [ ] Level 3: + Code Flow sichtbar
- [ ] Backend-Logs zeigen Filterungs-Entscheidungen

### Expand All / Collapse All
- [ ] Expand All expandiert alle Rows
- [ ] Collapse All kollabiert alle Rows
- [ ] Button-Text ändert sich korrekt
- [ ] Performance ist akzeptabel (max 50 Rows)

### Keyboard-Navigation
- [ ] Tab-Taste fokussiert Rows
- [ ] Enter-Taste expandiert/kollabiert
- [ ] Focus-Styles sind sichtbar
- [ ] Keine Console-Errors

### Copy-to-Clipboard
- [ ] Copy-Button erscheint bei expandierten Rows
- [ ] Inhalt wird korrekt kopiert
- [ ] Keine Clipboard-API-Fehler

### Backend Clamping
- [ ] set_verbosity(5) clammpt auf 3
- [ ] set_verbosity(-1) clammpt auf 0
- [ ] Keine ValueError-Exceptions

---

## 🔍 Häufige Probleme

### Problem: VerbositySelector wird nicht angezeigt
**Lösung:**
```bash
# Frontend neu bauen
docker compose build --no-cache cerebro-frontend
docker compose restart cerebro-frontend

# Browser Cache leeren (Strg+Shift+R)
```

### Problem: WebSocket verbindet nicht
**Lösung:**
```bash
# Backend-Logs prüfen
docker compose logs cerebro-backend | grep -i "websocket\|error"

# Backend neu starten
docker compose restart cerebro-backend

# Port prüfen
curl http://localhost:9000/health
```

### Problem: Verbosity-Filterung funktioniert nicht
**Lösung:**
```bash
# Backend-Logs mit Debug-Level prüfen
docker compose logs -f cerebro-backend | grep -i "WS Broadcast\|WS Filtered"

# Prüfe ob Debug-Logging aktiviert ist
# In websocket.py sollte logger.isEnabledFor(logging.DEBUG) True sein
```

### Problem: Expand All ist langsam
**Lösung:**
- Performance-Limit ist auf 50 Rows gesetzt
- Prüfe Browser Console auf Performance-Warnungen
- Reduziere maxLogs in LiveLogPanel falls nötig

---

## 📊 Performance-Monitoring

### Frontend Performance
```javascript
// Browser DevTools → Performance Tab
// Recording starten → Aktionen ausführen → Recording stoppen
// Prüfe auf:
// - Lange JavaScript-Execution
// - Viele Re-Renders
// - Memory-Leaks
```

### Backend Performance
```bash
# Response-Zeiten prüfen
docker compose logs cerebro-backend | grep -i "latency\|duration" | tail -20

# WebSocket-Broadcast-Zeiten
docker compose logs cerebro-backend | grep -i "broadcast" | tail -20
```

---

## ✅ Erfolgskriterien

- ✅ VerbositySelector funktioniert ohne Fehler
- ✅ Alle 4 Verbosity-Levels funktionieren korrekt
- ✅ Expand All/Collapse All funktioniert
- ✅ Keyboard-Navigation funktioniert
- ✅ Copy-to-Clipboard funktioniert
- ✅ Backend-Logs zeigen Verbosity-Filterung
- ✅ Keine Console-Errors im Browser
- ✅ Keine Backend-Exceptions
- ✅ Performance ist akzeptabel

---

## 📞 Support

Bei Problemen:
1. Prüfe Logs (siehe oben)
2. Prüfe Browser Console
3. Prüfe Network Tab (WebSocket-Verbindung)
4. Prüfe Backend Health-Endpoint
5. Prüfe Docker Container Status
