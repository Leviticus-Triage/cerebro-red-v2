# 🎯 Traycer Prompt - CEREBRO-RED v2 Live Monitoring Implementation

## Kontext

Du bist **Traycer**, ein Expert-System für Projektplanung und Task-Management. Du wirst mit der Aufgabe betraut, einen **umfassenden Phasenplan** für die Implementierung des Live-Monitoring-Systems im CEREBRO-RED v2 Projekt zu erstellen.

## Projekt-Übersicht

**Projekt:** CEREBRO-RED v2 - AI Red Team Framework  
**Ziel:** Vollständige Live-Monitoring-Funktionalität im Frontend Web-Interface  
**Status:** 🔴 KRITISCH - Aktuell funktioniert das Live-Monitoring nicht wie gewünscht

## Problemstellung

Das Projekt hat eine **Soll-Ist-Analyse** durchgeführt (siehe `SOLL_IST_ANALYSE.md`), die zeigt:

1. **WebSocket-Events werden nicht im Frontend angezeigt** - Live Logs Panel ist leer
2. **LLM Input/Output ist nicht sichtbar** - Requests/Responses erscheinen nicht
3. **Verbosity-Level fehlt im Frontend** - Keine Steuerung des Detail-Levels
4. **Code-Flow Events fehlen** - Keine Sichtbarkeit des Code-Flows
5. **Failure-Erklärungen sind zu generisch** - Keine detaillierte Analyse
6. **Task Queue zeigt keine echten Tasks** - Panel existiert, aber leer

**Kritische Anforderung:** Der Nutzer muss **ALLES** sehen können, was er im Terminal sieht, aber im Frontend Web-Interface.

## Nutzer-Anforderungen (SOLL)

### 1. LLM Input/Output Visibility
- Alle LLM-Requests (Attacker, Target, Judge) mit vollständigem Prompt-Inhalt
- Alle LLM-Responses mit vollständigem Response-Text
- Latenz, Token-Count, Model-Name, Provider für jede Interaktion
- Request/Response-Paare klar zugeordnet
- Farbcodierung nach Role

### 2. Verbosity-Level im Frontend
- Level 0: Nur Errors
- Level 1: + Warnings, Events
- Level 2: + LLM Details (Requests/Responses)
- Level 3: + Full Code Flow (jeder Funktionsaufruf, jeder Schritt)
- Verbosity-Level muss im Frontend konfigurierbar sein

### 3. Code-Flow Visibility
- Jeder Schritt des PAIR-Algorithmus sichtbar
- Funktionsaufrufe mit Parametern und Rückgabewerten
- Entscheidungspunkte (if/else, loops) mit Bedingungen

### 4. Iteration Details
- Original Prompt (p₀)
- Mutated Prompt (pᵢ)
- Target Response (rᵢ)
- Judge Score (sᵢ) mit allen 7 Sub-Scores
- Judge Reasoning (vollständiger Text)
- Success/Failure Status mit Erklärung
- Latenz-Breakdown (Mutation, Target, Judge)
- Token-Verbrauch pro Agent

### 5. Task Queue & Process Monitoring
- Alle Tasks in Warteschlange sichtbar
- Laufende Tasks mit Fortschritt
- Erledigte Tasks mit Ergebnis
- Failed Tasks mit Fehlerursache
- Task-Dependencies

### 6. Experiment Status & Failure Explanation
- Wenn Experiment "failed" → **DETAILLIERTE ERKLÄRUNG WARUM**
- Welche Iterationen wurden durchgeführt?
- Welche Scores wurden erreicht?
- Warum wurde der Threshold nicht erreicht?
- War es ein Fehler oder erfolgreiche Abwehr?
- Welche Strategien wurden versucht?
- Was war das beste Ergebnis?

### 7. Real-Time Updates via WebSocket
- Alle Events in Echtzeit über WebSocket
- LLM Request (sofort wenn gesendet)
- LLM Response (sofort wenn empfangen)
- Judge Evaluation (sofort nach Berechnung)
- Attack Mutation (sofort nach Mutation)
- Iteration Start/Complete
- Task Status Changes
- Code Flow Events (bei Verbosity 3)

## Technischer Stack

- **Backend:** FastAPI (Python), WebSocket, SQLAlchemy, LiteLLM
- **Frontend:** React, TypeScript, Vite, TanStack Query, WebSocket Client
- **Docker:** Multi-Container Setup (Backend + Frontend)
- **WebSocket:** FastAPI WebSocket Endpoint `/ws/scan/{experiment_id}`

## Aktuelle Code-Struktur

### Backend
- `backend/api/websocket.py` - WebSocket-Endpoint und Helper-Funktionen
- `backend/core/orchestrator.py` - PAIR-Algorithmus, sendet WebSocket-Events
- `backend/utils/verbose_logging.py` - Verbose Logging System
- `backend/utils/config.py` - Verbosity-Level Konfiguration

### Frontend
- `frontend/src/pages/ExperimentMonitor.tsx` - Haupt-Monitor-Seite
- `frontend/src/components/monitor/LiveLogPanel.tsx` - Live Logs Anzeige
- `frontend/src/lib/websocket/client.ts` - WebSocket Client
- `frontend/src/types/api.ts` - TypeScript Types für WebSocket Events

## Bekannte Probleme

1. **WebSocket-Events werden nicht angezeigt:**
   - Backend sendet Events (Code vorhanden)
   - Frontend empfängt Events nicht korrekt
   - Live Logs Panel bleibt leer

2. **Verbosity-Level fehlt:**
   - Backend hat `CEREBRO_VERBOSITY=3`
   - Frontend hat keine Verbosity-Konfiguration
   - Code-Flow-Events werden nicht gesendet

3. **Task Queue ist leer:**
   - Task-Events werden nicht gesendet
   - Task-Management fehlt im Orchestrator

## Deine Aufgabe

Erstelle einen **umfassenden Phasenplan** mit folgenden Anforderungen:

### Phasen-Struktur

1. **Phase 1: WebSocket-Integration Fix**
   - Diagnose warum Events nicht ankommen
   - Fix WebSocket-Event-Handler im Frontend
   - Test dass Events korrekt angezeigt werden

2. **Phase 2: LLM Input/Output Visibility**
   - Sicherstellen dass alle LLM-Requests/Responses gesendet werden
   - Frontend-Anzeige für Requests/Responses implementieren
   - Request/Response-Paarung

3. **Phase 3: Verbosity-Level System**
   - Backend: Code-Flow-Events implementieren
   - Frontend: Verbosity-Level-Selector
   - Frontend: Event-Filterung basierend auf Verbosity

4. **Phase 4: Code-Flow Tracking**
   - Backend: Jeden Funktionsaufruf tracken
   - Backend: Entscheidungspunkte dokumentieren
   - Frontend: Code-Flow-Panel implementieren

5. **Phase 5: Iteration Details Enhancement**
   - Latenz-Breakdown implementieren
   - Token-Verbrauch pro Agent tracken
   - Detaillierte Iteration-Ansicht

6. **Phase 6: Task Queue Implementation**
   - Task-Management im Orchestrator
   - Task-Events über WebSocket
   - Task-Queue-Panel funktionsfähig machen

7. **Phase 7: Failure Analysis Engine**
   - Detaillierte Failure-Analyse
   - Beste-Ergebnis-Tracking
   - Strategie-Analyse

8. **Phase 8: Testing & Validation**
   - End-to-End Tests
   - Performance-Tests
   - User-Acceptance-Tests

### Für jede Phase

1. **Detaillierte Task-Liste:**
   - Jeder Task muss spezifisch und umsetzbar sein
   - Dependencies zwischen Tasks klar definiert
   - Geschätzte Zeit pro Task

2. **Code-Änderungen:**
   - Welche Dateien müssen geändert werden?
   - Welche Funktionen müssen implementiert werden?
   - Welche Tests müssen geschrieben werden?

3. **Validierung:**
   - Wie wird getestet dass die Phase erfolgreich ist?
   - Welche Kriterien müssen erfüllt sein?

4. **Risiken & Mitigation:**
   - Welche Risiken gibt es?
   - Wie werden sie gemindert?

## Qualitätskriterien

- ✅ **Jeder Task ist spezifisch** - Keine vagen Beschreibungen
- ✅ **Jeder Task ist testbar** - Klare Erfolgskriterien
- ✅ **Dependencies sind klar** - Keine zirkulären Abhängigkeiten
- ✅ **Code-Änderungen sind dokumentiert** - Welche Dateien, welche Funktionen
- ✅ **Tests sind inkludiert** - Unit, Integration, E2E
- ✅ **Risiken sind identifiziert** - Mit Mitigation-Strategien

## Output-Format

Erstelle den Phasenplan als strukturiertes Dokument mit:

1. **Executive Summary** - Kurze Übersicht
2. **Phasen-Übersicht** - Alle Phasen mit Zielen
3. **Detaillierte Phasen** - Jede Phase mit:
   - Ziel
   - Tasks (mit Dependencies)
   - Code-Änderungen
   - Tests
   - Validierung
   - Risiken
4. **Timeline** - Geschätzte Dauer pro Phase
5. **Ressourcen** - Benötigte Skills/Tools
6. **Success Metrics** - Wie wird Erfolg gemessen?

## Wichtig

- **Jeder Punkt muss detailliert geplant werden**
- **Jeder Prozess muss tiefgehend analysiert werden**
- **Jede Implementierung muss getestet werden**
- **Jeder Fix muss validiert werden**

Der Nutzer hat bereits mehrfach darauf hingewiesen, dass Features nicht funktionieren. **Diesmal muss alles perfekt funktionieren.**

---

**Erstelle jetzt den umfassenden Phasenplan für Traycer.**
