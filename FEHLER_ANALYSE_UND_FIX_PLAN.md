# 🔴 KRITISCHE FEHLER-ANALYSE - CEREBRO-RED v2

## ⚠️ AKTUELLER STATUS (2026-01-03)

**🚨 SYSTEM KOMPLETT DEFEKT - EXPERIMENTE STARTEN NICHT MEHR! 🚨**

Nach mehreren Debugging-Versuchen und Code-Änderungen ist das System nun in einem schlechteren Zustand als vorher:

### **KRITISCHES PROBLEM:**
- ❌ Experimente werden sofort als FAILED markiert
- ❌ `run_experiment()` wird NIE aufgerufen
- ❌ KEINE Iterationen werden ausgeführt
- ❌ Meldung: "Experiment marked as FAILED: no successful iterations found"

### **ROOT CAUSE:**
`asyncio.create_task()` in `backend/api/scans.py` erstellt Tasks, die sofort vom Garbage Collector gelöscht werden, BEVOR sie ausgeführt werden können.

### **VERSUCHTER FIX:**
Task-Referenzen in einem Set speichern - **NOCH NICHT GETESTET!**

### **EMPFEHLUNG:**
**Siehe detaillierten TRAYCER-Prompt in `BUG_REPORT_AND_TRAYCER_PROMPT.md`**

---

## 📋 ALLE GEMELDETEN FEHLER (Letzte 10 Prompts)

### 1. **Strategie-Rotation komplett defekt** ❌
- **Problem**: Nur 1 Strategie wird verwendet, obwohl 19 ausgewählt wurden
- **Symptom**: "Strategy Usage" zeigt "18 skipped, 1 used"
- **Erwartung**: Alle ausgewählten Strategien sollten gleichmäßig rotiert werden
- **Status**: Teilweise gefixt (Round-Robin implementiert), aber funktioniert noch nicht korrekt

### 2. **Vulnerabilities verschwinden aus Live Monitor** ❌
- **Problem**: Vulnerabilities werden im Live Monitor angezeigt, verschwinden aber beim Verlassen/Wiederkommen
- **Symptom**: Oben rechts "1 Vulnerability", aber in Live Logs "0 Vulnerabilities"
- **Erwartung**: Alle Vulnerabilities müssen persistent sein und immer angezeigt werden
- **Status**: Teilweise gefixt (historische Logs werden geladen), aber Filter funktioniert nicht korrekt

### 3. **Inkonsistente Progress-Anzeigen überall** ❌
- **Problem**: Unterschiedliche Werte an verschiedenen Stellen:
  - Experiment Overview: "0/0" (falsch)
  - Live Monitor: "12/15" (korrekt)
  - Attack Progress: "0/0" (falsch)
  - Statistics: "12" (korrekt)
- **Erwartung**: Überall sollte "12/15" (80%) angezeigt werden
- **Status**: Teilweise gefixt (API gibt korrekte Werte), aber Frontend-Komponenten zeigen falsche Werte

### 4. **Status-Inkonsistenzen** ❌
- **Problem**: Experiment zeigt "completed" obwohl es noch "running" ist
- **Symptom**: Live Monitor zeigt "Completed" bei 12/15 Iterationen (80%)
- **Erwartung**: Status sollte "running" sein bis alle 15 Iterationen fertig sind
- **Status**: Teilweise gefixt, aber Logik ist noch fehlerhaft

### 5. **AttackProgress zeigt 0/0 statt 12/15** ❌
- **Problem**: AttackProgress Komponente zeigt immer "Iteration 0/0" und "0.0%"
- **Symptom**: Experiment Overview zeigt falsche Werte
- **Erwartung**: Sollte aktuelle Werte aus API anzeigen (12/15, 80%)
- **Status**: API-Polling hinzugefügt, aber funktioniert noch nicht

### 6. **Live Logs Scrolling Bug** ❌
- **Problem**: Kann nicht mehr scrollen, Einträge werden abgeschnitten
- **Symptom**: Logs sind nicht vollständig sichtbar
- **Erwartung**: Alle Logs sollten scrollbar und vollständig sichtbar sein
- **Status**: CSS-Fixes hinzugefügt, aber funktioniert noch nicht richtig

### 7. **Code Flow zeigt nichts** ❌
- **Problem**: Code Flow Tab zeigt "No code-flow events yet" obwohl verbosity=3 aktiviert ist
- **Symptom**: Keine Code Flow Events werden angezeigt
- **Erwartung**: Code Flow Events sollten angezeigt werden wenn verbosity=3
- **Status**: Historische Events werden jetzt geladen, aber Backend sendet möglicherweise keine Events

### 8. **Experiment Overview zeigt immer noch 0/0** ❌
- **Problem**: Nach allen Fixes zeigt Overview immer noch "Iteration 0/0"
- **Symptom**: AttackProgress Komponente wird angezeigt, aber mit falschen Werten
- **Erwartung**: Sollte 12/15 zeigen
- **Status**: Komponente wird jetzt immer angezeigt, aber API-Aufruf funktioniert nicht

### 9. **Vulnerability Filter funktioniert nicht** ❌
- **Problem**: Live Logs Filter zeigt "0 Vulnerabilities" obwohl 1 gefunden wurde
- **Symptom**: Filter erkennt Vulnerabilities nicht korrekt
- **Erwartung**: Sollte alle Vulnerabilities korrekt filtern und anzeigen
- **Status**: Filter-Logik verbessert, aber funktioniert noch nicht

### 10. **Alle Werte stimmen nicht überein** ❌
- **Problem**: Überall werden unterschiedliche/inkonsistente Werte angezeigt
- **Symptom**: Keine einzige Anzeige stimmt mit der Realität überein
- **Erwartung**: Alle Anzeigen sollten konsistent und korrekt sein
- **Status**: Systematisches Problem - benötigt komplette Überarbeitung

### 11. **Verbosity Level setzt sich immer zurück** ❌
- **Problem**: Verbosity Level wird immer auf "Detailed" (Level 2) zurückgesetzt beim Neuladen
- **Symptom**: User wählt z.B. "Debug" (Level 3), aber beim Neuladen ist es wieder "Detailed"
- **Erwartung**: Verbosity Level sollte persistent gespeichert werden (pro Experiment)
- **Status**: ✅ GEFIXT - localStorage Persistenz implementiert
- **Dateien**: `frontend/src/pages/ExperimentMonitor.tsx`

---

## 🎯 TRAYCER PROMPT FÜR SYSTEMATISCHE FIXES

```markdown
# CEREBRO-RED v2: Systematische Fehlerbehebung aller UI/Status-Inkonsistenzen

## MISSION
Analysiere und fixe ALLE 10 kritischen Fehler in der CEREBRO-RED v2 Anwendung, die zu inkonsistenten Anzeigen führen.

## CONTEXT
Die Anwendung ist ein LLM Security Testing Framework mit:
- Backend: FastAPI (Python) auf Port 9000
- Frontend: React/TypeScript auf Port 3000
- Docker Compose Setup
- WebSocket für Live-Updates
- REST API für Status-Abfragen

## KRITISCHE FEHLER (Priorität: HOCH)

### Phase 1: Datenkonsistenz & API-Integration
**Ziel**: Alle Frontend-Komponenten müssen korrekte Daten von der API erhalten

1. **AttackProgress Komponente**
   - Problem: Zeigt immer "0/0" statt "12/15"
   - Root Cause: API-Aufruf funktioniert nicht oder Response wird falsch geparst
   - Fix:
     - Prüfe `apiClient.getScanStatus()` Response-Struktur
     - Stelle sicher, dass `response.data.data` korrekt extrahiert wird
     - Füge Error-Handling und Fallback-Logik hinzu
     - Teste mit curl: `curl http://localhost:9000/api/scan/status/{experiment_id}`
   - Dateien: `frontend/src/components/experiments/AttackProgress.tsx`, `frontend/src/lib/api/client.ts`

2. **Experiment Overview Progress**
   - Problem: Zeigt "Iteration 0/0" statt "12/15"
   - Root Cause: AttackProgress wird nicht korrekt initialisiert oder API-Aufruf schlägt fehl
   - Fix:
     - Initialisiere State mit API-Daten beim Mount
     - Füge Loading-State hinzu
     - Zeige Fehler an wenn API-Aufruf fehlschlägt
   - Dateien: `frontend/src/pages/ExperimentDetails.tsx`, `frontend/src/components/experiments/AttackProgress.tsx`

### Phase 2: Status-Logik & State Management
**Ziel**: Status wird korrekt berechnet und angezeigt

3. **Status-Inkonsistenz (running vs completed)**
   - Problem: Zeigt "completed" obwohl noch "running" (12/15 Iterationen)
   - Root Cause: Status-Logik setzt "completed" zu früh
   - Fix:
     - Status sollte NUR "completed" sein wenn `current_iteration >= total_iterations`
     - ODER wenn Backend-Status explizit "completed" ist
     - Entferne Logik die Status basierend auf "successful_iterations" setzt
   - Dateien: `frontend/src/pages/ExperimentMonitor.tsx` (Zeile ~529-538)

4. **Progress-Berechnung überall konsistent**
   - Problem: Unterschiedliche Werte an verschiedenen Stellen
   - Root Cause: Jede Komponente berechnet Progress anders
   - Fix:
     - Zentralisiere Progress-Berechnung in einem Hook oder Utility
     - Verwende IMMER: `progress = (current_iteration / total_iterations) * 100`
     - `total_iterations = max_iterations * len(initial_prompts)`
   - Dateien: Alle Komponenten die Progress anzeigen

### Phase 3: Strategie-Rotation komplett überarbeiten
**Ziel**: Alle ausgewählten Strategien werden gleichmäßig verwendet

5. **Strategie-Rotation defekt**
   - Problem: Nur 1 Strategie wird verwendet, 18 werden skipped
   - Root Cause: Round-Robin funktioniert nicht oder wird überschrieben
   - Fix:
     - Prüfe `_get_next_strategy()` in `backend/core/orchestrator.py`
     - Stelle sicher, dass Round-Robin IMMER verwendet wird (keine "intelligent selection" die es überschreibt)
     - Teste mit Experiment das 5 Iterationen und 3 Strategien hat → sollte: S1, S2, S3, S1, S2 verwenden
   - Dateien: `backend/core/orchestrator.py` (Zeile ~1906-1990)

### Phase 4: Vulnerability-Anzeige & Filter
**Ziel**: Vulnerabilities werden korrekt angezeigt und bleiben persistent

6. **Vulnerabilities verschwinden**
   - Problem: Verschwinden beim Verlassen/Wiederkommen des Live Monitors
   - Root Cause: Filter erkennt Vulnerabilities nicht oder Logs werden nicht korrekt geladen
   - Fix:
     - Prüfe Vulnerability-Filter in `LiveLogPanel.tsx`
     - Stelle sicher, dass historische Logs auch Vulnerabilities enthalten
     - Teste: Filter sollte alle Logs mit `metadata.vulnerability_id` finden
   - Dateien: `frontend/src/components/monitor/LiveLogPanel.tsx` (Zeile ~815)

7. **Vulnerability Filter zeigt 0**
   - Problem: Filter zeigt "0 Vulnerabilities" obwohl 1 gefunden wurde
   - Root Cause: Filter-Logik erkennt Vulnerability-Logs nicht
   - Fix:
     - Prüfe wie Vulnerabilities in Logs gespeichert werden (Typ, Metadata)
     - Verbessere Filter um alle Varianten zu erkennen:
       - `log.metadata?.vulnerability_id`
       - `log.type === 'vulnerability_found'`
       - `log.content?.includes('VULNERABILITY FOUND')`
   - Dateien: `frontend/src/components/monitor/LiveLogPanel.tsx`

### Phase 5: UI/UX Fixes
**Ziel**: Alle UI-Probleme beheben

8. **Scrolling Bug in Live Logs**
   - Problem: Kann nicht scrollen, Einträge werden abgeschnitten
   - Root Cause: CSS-Container-Höhe oder Overflow-Settings falsch
   - Fix:
     - Prüfe alle Container mit `max-h-[calc(100vh-XXXpx)]`
     - Stelle sicher, dass `overflow-y-auto` gesetzt ist
     - Teste mit vielen Log-Einträgen (50+)
   - Dateien: `frontend/src/components/monitor/LiveLogPanel.tsx` (alle Tabellen-Container)

9. **Code Flow zeigt nichts**
   - Problem: Zeigt "No code-flow events" obwohl verbosity=3 aktiviert
   - Root Cause: Events werden nicht gesendet oder nicht korrekt geladen
   - Fix:
     - Prüfe Backend: Werden Code Flow Events geloggt? (`backend/core/verbose_logging.py`)
     - Prüfe WebSocket: Werden `code_flow` Nachrichten gesendet?
     - Prüfe Frontend: Werden Events aus historischen Logs geladen?
     - Teste: Setze `CEREBRO_VERBOSITY=3` in `backend/.env` und starte Backend neu
   - Dateien: `frontend/src/pages/ExperimentMonitor.tsx`, `backend/core/verbose_logging.py`

10. **Verbosity Level setzt sich zurück**
    - Problem: Verbosity Level wird immer auf "Detailed" (2) zurückgesetzt beim Neuladen
    - Root Cause: Verbosity wird nicht in localStorage gespeichert
    - Fix:
      - Speichere Verbosity Level in localStorage beim Ändern: `localStorage.setItem('verbosity_${experimentId}', level)`
      - Lade Verbosity beim Mount: `localStorage.getItem('verbosity_${experimentId}')`
      - Verwende experiment-spezifischen Key (pro Experiment ID)
      - Fallback auf Level 2 (Detailed) wenn kein Wert gespeichert ist
    - Dateien: `frontend/src/pages/ExperimentMonitor.tsx` (handleVerbosityChange, useEffect)
    - Status: ✅ IMPLEMENTIERT

### Phase 6: Integration & Testing
**Ziel**: Alles funktioniert zusammen

10. **End-to-End Test**
    - Erstelle neues Experiment mit:
      - 3 Prompts
      - 5 Max Iterations
      - 3 Strategien ausgewählt
    - Prüfe:
      - ✅ AttackProgress zeigt korrekte Werte (0/15 → 15/15)
      - ✅ Status ist "running" bis alle 15 Iterationen fertig
      - ✅ Alle 3 Strategien werden verwendet (nicht nur 1)
      - ✅ Vulnerabilities bleiben sichtbar
      - ✅ Live Logs sind scrollbar
      - ✅ Code Flow Events werden angezeigt (wenn verbosity=3)

## TECHNISCHE ANFORDERUNGEN

1. **API Response-Struktur prüfen**:
   ```bash
   curl http://localhost:9000/api/scan/status/{experiment_id} | jq
   ```
   Erwartet: `{"data": {"current_iteration": 12, "total_iterations": 15, ...}}`

2. **WebSocket-Nachrichten prüfen**:
   - Öffne Browser DevTools → Network → WS
   - Prüfe ob `progress`, `code_flow`, `vulnerability_found` Nachrichten ankommen

3. **Backend-Logs prüfen**:
   ```bash
   docker compose logs cerebro-backend | grep -E "strategy|iteration|vulnerability"
   ```

4. **Frontend-Logs prüfen**:
   - Browser DevTools → Console
   - Prüfe `[AttackProgress]` Debug-Logs

## ERFOLGSKRITERIEN

- [ ] AttackProgress zeigt korrekte Werte (12/15, 80%)
- [ ] Status ist konsistent (running bis alle Iterationen fertig)
- [ ] Alle ausgewählten Strategien werden verwendet
- [ ] Vulnerabilities bleiben persistent und sichtbar
- [ ] Live Logs sind vollständig scrollbar
- [ ] Code Flow Events werden angezeigt (wenn verbosity=3)
- [ ] Verbosity Level bleibt persistent (wird nicht zurückgesetzt)
- [ ] Alle Anzeigen sind konsistent überall

## PRIORITÄT

**KRITISCH**: Diese Fehler machen die Anwendung unbrauchbar. Alle müssen behoben werden.

## HINWEISE

- Teste JEDEN Fix einzeln
- Verwende Browser DevTools für Debugging
- Prüfe Backend-Logs für Fehler
- Teste mit einem laufenden Experiment
- Stelle sicher, dass keine Regressionen entstehen
```

---

## 📝 ZUSÄTZLICHE HINWEISE FÜR TRAYCER

1. **Backend-Container muss neu gestartet werden** nach Code-Änderungen:
   ```bash
   docker compose restart cerebro-backend
   ```

2. **Frontend muss neu gebaut werden** nach Code-Änderungen:
   ```bash
   cd frontend && npm run build && docker compose restart cerebro-frontend
   ```

3. **Test-Experiment ID**: `1ecce593-1bee-49bb-9cc3-6b2dedda2064`
   - Hat 3 Prompts
   - Max 5 Iterations
   - Sollte 15 total Iterations haben (3 × 5)
   - Aktuell bei 12/15 (80%)

4. **Wichtige Dateien**:
   - `backend/core/orchestrator.py` - Strategie-Rotation
   - `backend/api/scans.py` - Status-API
   - `frontend/src/components/experiments/AttackProgress.tsx` - Progress-Anzeige
   - `frontend/src/pages/ExperimentMonitor.tsx` - Live Monitor
   - `frontend/src/components/monitor/LiveLogPanel.tsx` - Log-Anzeige
