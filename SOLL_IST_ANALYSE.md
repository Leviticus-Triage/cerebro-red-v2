# 📊 CEREBRO-RED v2 - Soll-Ist-Analyse

**Datum:** 2025-12-25  
**Projekt:** CEREBRO-RED v2 - AI Red Team Framework  
**Status:** 🔴 Kritische Abweichungen zwischen Soll und Ist

---

## 🎯 Nutzer-Anforderungen (SOLL)

### 1. Live-Monitoring im Frontend Web-Interface

**Anforderung:**
> "wir müssen in das frontend webinterface noch eine möglichkeit einbauen, den gesamten input output der agents und modellen, sowie scorings/rankings/parameter, sowie auch forschrittsanzeige und result's, prompts und deren antworten, als auch erledigte Prozesse/Tasks und Prozesse/Tasks die To-do/warteschlange sind - monitoren und sehen zu können (natürlich schön strukturiert, formatiert und übersichtlich kategorisiert)"

**Detaillierte Anforderungen:**

#### 1.1 LLM Input/Output Visibility
- ✅ **SOLL:** Alle LLM-Requests (Attacker, Target, Judge) mit vollständigem Prompt-Inhalt im Frontend sichtbar
- ✅ **SOLL:** Alle LLM-Responses mit vollständigem Response-Text im Frontend sichtbar
- ✅ **SOLL:** Latenz, Token-Count, Model-Name, Provider für jede LLM-Interaktion
- ✅ **SOLL:** Request/Response-Paare klar zugeordnet (Request → Response)
- ✅ **SOLL:** Farbcodierung nach Role (Attacker=Rot, Target=Blau, Judge=Amber)

#### 1.2 Verbosity-Level im Frontend
- ✅ **SOLL:** Verbosity-Level 0-3 konfigurierbar im Frontend
- ✅ **SOLL:** Level 0: Nur Errors
- ✅ **SOLL:** Level 1: + Warnings, Events
- ✅ **SOLL:** Level 2: + LLM Details (Requests/Responses)
- ✅ **SOLL:** Level 3: + Full Code Flow (jeder Funktionsaufruf, jeder Schritt)
- ✅ **SOLL:** Verbosity-Level steuert was im Frontend angezeigt wird

#### 1.3 Code-Flow Visibility
- ✅ **SOLL:** Jeder Schritt des PAIR-Algorithmus sichtbar:
  - Strategy Selection
  - Prompt Mutation (Original → Mutated)
  - Target LLM Call
  - Judge Evaluation
  - Score Calculation
  - Database Write
  - WebSocket Broadcast
- ✅ **SOLL:** Funktionsaufrufe mit Parametern und Rückgabewerten
- ✅ **SOLL:** Entscheidungspunkte (if/else, loops) mit Bedingungen

#### 1.4 Iteration Details
- ✅ **SOLL:** Für jede Iteration vollständige Details:
  - Original Prompt (p₀)
  - Mutated Prompt (pᵢ)
  - Target Response (rᵢ)
  - Judge Score (sᵢ) mit allen 7 Sub-Scores
  - Judge Reasoning (vollständiger Text)
  - Success/Failure Status mit Erklärung
  - Latenz-Breakdown (Mutation, Target, Judge)
  - Token-Verbrauch pro Agent

#### 1.5 Task Queue & Process Monitoring
- ✅ **SOLL:** Alle Tasks in Warteschlange sichtbar
- ✅ **SOLL:** Laufende Tasks mit Fortschritt
- ✅ **SOLL:** Erledigte Tasks mit Ergebnis
- ✅ **SOLL:** Failed Tasks mit Fehlerursache
- ✅ **SOLL:** Task-Dependencies (welche Task wartet auf welche)

#### 1.6 Experiment Status & Failure Explanation
- ✅ **SOLL:** Wenn Experiment "failed" → **DETAILLIERTE ERKLÄRUNG WARUM**
  - Welche Iterationen wurden durchgeführt?
  - Welche Scores wurden erreicht?
  - Warum wurde der Threshold nicht erreicht?
  - War es ein Fehler oder erfolgreiche Abwehr?
  - Welche Strategien wurden versucht?
  - Was war das beste Ergebnis?

#### 1.7 Real-Time Updates via WebSocket
- ✅ **SOLL:** Alle Events in Echtzeit über WebSocket:
  - LLM Request (sofort wenn gesendet)
  - LLM Response (sofort wenn empfangen)
  - Judge Evaluation (sofort nach Berechnung)
  - Attack Mutation (sofort nach Mutation)
  - Iteration Start/Complete
  - Task Status Changes
  - Code Flow Events (bei Verbosity 3)

---

## ❌ Aktueller Zustand (IST)

### 1. Live-Monitoring im Frontend

#### 1.1 LLM Input/Output Visibility
- ❌ **IST:** Live Logs Panel ist **LEER** - keine Events werden angezeigt
- ❌ **IST:** WebSocket-Events werden zwar gesendet, aber nicht im Frontend empfangen/angezeigt
- ❌ **IST:** Keine LLM-Requests sichtbar
- ❌ **IST:** Keine LLM-Responses sichtbar
- ❌ **IST:** Keine Latenz/Token-Informationen sichtbar
- ⚠️ **IST:** Im Terminal (Docker Logs) sind alle Informationen vorhanden, aber nicht im Frontend

#### 1.2 Verbosity-Level im Frontend
- ❌ **IST:** Verbosity-Level existiert nur im Backend (`CEREBRO_VERBOSITY=3`)
- ❌ **IST:** Keine Frontend-Konfiguration für Verbosity
- ❌ **IST:** Frontend zeigt nicht unterschiedliche Detail-Levels
- ❌ **IST:** Code-Flow-Events werden nicht über WebSocket gesendet

#### 1.3 Code-Flow Visibility
- ❌ **IST:** Keine Code-Flow-Events im Frontend
- ❌ **IST:** Keine Funktionsaufrufe sichtbar
- ❌ **IST:** Keine Entscheidungspunkte dokumentiert
- ⚠️ **IST:** Im Terminal-Logging vorhanden, aber nicht im Frontend

#### 1.4 Iteration Details
- ✅ **IST:** Iteration Details werden von API zurückgegeben (nach Fix)
- ⚠️ **IST:** Details werden nur angezeigt wenn man auf Iteration klickt
- ❌ **IST:** Keine Live-Updates während der Iteration
- ❌ **IST:** Keine Latenz-Breakdown (nur Gesamt-Latenz)
- ❌ **IST:** Keine Token-Verbrauch pro Agent

#### 1.5 Task Queue & Process Monitoring
- ⚠️ **IST:** Task Queue Panel existiert, aber zeigt keine echten Tasks
- ❌ **IST:** Keine Warteschlange sichtbar
- ❌ **IST:** Keine Task-Dependencies
- ❌ **IST:** Keine Fortschrittsanzeige pro Task

#### 1.6 Experiment Status & Failure Explanation
- ✅ **IST:** Basis-Erklärung wurde hinzugefügt (nach Fix)
- ⚠️ **IST:** Erklärung ist generisch, nicht detailliert genug
- ❌ **IST:** Keine Analyse welche Strategien versucht wurden
- ❌ **IST:** Keine Beste-Ergebnis-Anzeige

#### 1.7 Real-Time Updates via WebSocket
- ❌ **IST:** WebSocket-Verbindung wird hergestellt, aber Events kommen nicht an
- ❌ **IST:** `llm_request`, `llm_response`, `judge_evaluation` Events werden nicht angezeigt
- ❌ **IST:** Frontend zeigt nur "Waiting for logs..."
- ⚠️ **IST:** Backend sendet Events (im Code vorhanden), aber Frontend empfängt sie nicht

---

## 🔴 Kritische Abweichungen

### Abweichung 1: WebSocket-Events werden nicht im Frontend angezeigt
- **SOLL:** Alle LLM-Requests/Responses in Echtzeit im Frontend
- **IST:** Live Logs Panel ist leer
- **Ursache:** WebSocket-Events werden nicht korrekt verarbeitet/angezeigt
- **Impact:** 🔴 KRITISCH - Nutzer kann nicht sehen was passiert

### Abweichung 2: Verbosity-Level fehlt komplett im Frontend
- **SOLL:** Konfigurierbare Verbosity-Level im Frontend
- **IST:** Keine Verbosity-Konfiguration im Frontend
- **Ursache:** Verbosity existiert nur im Backend, Frontend ignoriert es
- **Impact:** 🔴 KRITISCH - Nutzer kann Detail-Level nicht steuern

### Abweichung 3: Code-Flow Events fehlen
- **SOLL:** Jeder Funktionsaufruf, jeder Schritt sichtbar
- **IST:** Keine Code-Flow-Events im Frontend
- **Ursache:** Code-Flow-Events werden nicht über WebSocket gesendet
- **Impact:** 🟡 HOCH - Nutzer kann Code-Flow nicht nachvollziehen

### Abweichung 4: Failure-Erklärung zu generisch
- **SOLL:** Detaillierte Erklärung warum Experiment failed
- **IST:** Generische Erklärung "Kein Jailbreak erfolgreich"
- **Ursache:** Keine detaillierte Analyse der Iterationen
- **Impact:** 🟡 HOCH - Nutzer versteht nicht was genau passiert ist

### Abweichung 5: Task Queue zeigt keine echten Tasks
- **SOLL:** Alle Tasks in Warteschlange/laufend/erledigt sichtbar
- **IST:** Task Queue Panel existiert, aber leer
- **Ursache:** Tasks werden nicht als WebSocket-Events gesendet
- **Impact:** 🟡 MITTEL - Nutzer sieht keine Task-Struktur

---

## 📋 Fehlende Features (Gap-Analyse)

### Frontend
1. ❌ WebSocket-Event-Handler für `llm_request`/`llm_response` funktioniert nicht
2. ❌ Verbosity-Level-Selector im Frontend fehlt
3. ❌ Code-Flow-Panel fehlt komplett
4. ❌ Latenz-Breakdown-Visualisierung fehlt
5. ❌ Token-Verbrauch-Chart fehlt
6. ❌ Task-Dependency-Graph fehlt
7. ❌ Failure-Analyse-Panel fehlt

### Backend
1. ❌ Code-Flow-Events werden nicht über WebSocket gesendet
2. ❌ Task-Status-Events werden nicht gesendet
3. ❌ Verbosity-Level wird nicht an Frontend kommuniziert
4. ❌ Latenz-Breakdown wird nicht getrackt
5. ❌ Token-Verbrauch pro Agent wird nicht getrackt

### Integration
1. ❌ WebSocket-Events werden nicht korrekt vom Frontend empfangen
2. ❌ Event-Handler im Frontend funktionieren nicht
3. ❌ Live-Log-Panel zeigt keine Events an

---

## 🎯 Prioritäten

### P0 - KRITISCH (Sofort)
1. **WebSocket-Events im Frontend anzeigen** - Live Logs müssen funktionieren
2. **LLM Input/Output sichtbar machen** - Requests/Responses müssen erscheinen
3. **Verbosity-Level im Frontend** - Nutzer muss Detail-Level steuern können

### P1 - HOCH (Diese Woche)
4. **Code-Flow Events** - Jeder Schritt muss sichtbar sein
5. **Failure-Erklärung detaillieren** - Warum failed muss klar sein
6. **Task Queue funktionsfähig machen** - Tasks müssen sichtbar sein

### P2 - MITTEL (Nächste Woche)
7. **Latenz-Breakdown** - Pro-Schritt-Latenz
8. **Token-Verbrauch-Charts** - Pro-Agent-Tracking
9. **Task-Dependency-Graph** - Visualisierung

---

## 📝 Technische Schulden

1. **WebSocket-Integration:** Events werden gesendet, aber Frontend empfängt sie nicht korrekt
2. **Event-Handler:** Frontend-Handler für WebSocket-Events funktionieren nicht
3. **Verbosity-System:** Nur Backend, keine Frontend-Integration
4. **Code-Flow-Tracking:** Fehlt komplett
5. **Task-Management:** Tasks werden nicht als Events gesendet
6. **Failure-Analysis:** Keine detaillierte Analyse-Engine

---

*Erstellt am: 2025-12-25*  
*Status: 🔴 KRITISCH - Sofortige Behebung erforderlich*
