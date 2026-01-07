# TRAYCER Audit & Fix Prompt für CEREBRO-RED v2

## Kontext & Problemstellung

CEREBRO-RED v2 ist ein **research-grade Framework für autonomes LLM Red Teaming** mit PAIR-Algorithmus. Das Projekt besteht aus:

- **Backend**: FastAPI (Python 3.11+) mit SQLAlchemy ORM, litellm für Multi-Provider LLM Support
- **Frontend**: React + TypeScript + Vite + TailwindCSS + ShadcnUI
- **Datenbank**: SQLite (async via aiosqlite)
- **Telemetry**: JSONL-basierte Audit-Logs für Research

### Aktuelle kritische Probleme:

1. **CORS-Fehler**: Frontend (localhost:5173) kann nicht mit Backend (localhost:8889) kommunizieren
2. **500 Internal Server Error**: Experiment-Erstellung schlägt fehl
3. **422 Unprocessable Entity**: `/api/vulnerabilities/statistics` Endpoint gibt Validierungsfehler
4. **Frontend-Backend Inkonsistenz**: API Response-Struktur stimmt nicht überein
5. **"Experiment not found"**: Navigation nach Experiment-Erstellung funktioniert nicht
6. **TypeError**: `Cannot read properties of undefined (reading 'experiment_id')`

### Bekannte Fixes (teilweise implementiert, aber nicht vollständig getestet):

- CORS-Konfiguration in `backend/main.py` verbessert
- Route-Reihenfolge in `backend/api/vulnerabilities.py` korrigiert (`/statistics` vor `/{vulnerability_id}`)
- `ExperimentResponse.from_db()` für `experiment_metadata` korrigiert
- Frontend `ExperimentNew.tsx` Fehlerbehandlung verbessert
- `apiClient.createExperiment()` Response-Wrapping hinzugefügt

---

## TRAYCER Auftrag: Vollständiger Stack-Audit & Fix-Plan

### Phase 1: Systematische Problem-Analyse

**Ziel**: Alle Fehlerquellen identifizieren und kategorisieren

1. **Backend API Audit**:
   - Teste alle Endpoints mit `curl` (GET, POST, PUT, DELETE)
   - Prüfe CORS-Header für alle Requests (inkl. OPTIONS Preflight)
   - Validiere Request/Response-Strukturen gegen Pydantic Models
   - Prüfe Error-Handling und Exception-Propagation
   - Teste Datenbank-Transaktionen (Commit/Rollback bei Fehlern)

2. **Frontend-Backend Integration Audit**:
   - Vergleiche TypeScript Interfaces (`frontend/src/types/api.ts`) mit Backend Pydantic Models
   - Prüfe API Client (`frontend/src/lib/api/client.ts`) Response-Handling
   - Validiere alle React Query Hooks (`frontend/src/hooks/useExperiments.ts`)
   - Teste WebSocket-Verbindungen (`frontend/src/lib/websocket/client.ts`)

3. **Datenbank & ORM Audit**:
   - Prüfe Alembic Migrations auf Konsistenz
   - Validiere SQLAlchemy ORM Models gegen Pydantic Models
   - Teste Repository-Pattern Implementierung
   - Prüfe Foreign Key Constraints und Relationships

4. **Konfiguration & Environment Audit**:
   - Validiere `.env` Datei-Ladung (Backend und Frontend)
   - Prüfe `API_KEY_ENABLED` Logik in `backend/api/auth.py`
   - Teste CORS-Konfiguration aus `.env`
   - Validiere LLM Provider-Konfiguration (Ollama, Azure, OpenAI)

---

### Phase 2: End-to-End Test-Suite Erstellung

**Ziel**: Automatisierte Tests für kritische User-Flows

1. **Backend Integration Tests**:
   ```python
   # tests/e2e/test_experiment_lifecycle.py
   - Test: Experiment erstellen (POST /api/experiments)
   - Test: Experiment abrufen (GET /api/experiments/{id})
   - Test: Scan starten (POST /api/scan/start)
   - Test: Scan-Status abrufen (GET /api/scan/{experiment_id}/status)
   - Test: Vulnerabilities abrufen (GET /api/vulnerabilities)
   - Test: Statistics abrufen (GET /api/vulnerabilities/statistics)
   ```

2. **Frontend E2E Tests** (mit Playwright oder Cypress):
   ```typescript
   // tests/e2e/experiment-creation.spec.ts
   - Test: Formular ausfüllen und Experiment erstellen
   - Test: Navigation nach Experiment-Erstellung
   - Test: Experiment-Details anzeigen
   - Test: Scan starten und Status anzeigen
   - Test: Vulnerabilities anzeigen
   ```

3. **CORS & API Authentication Tests**:
   ```python
   # tests/test_cors.py
   - Test: OPTIONS Preflight Requests
   - Test: CORS-Header für alle Origins
   - Test: API Key Authentication (enabled/disabled)
   - Test: Unauthorized Requests (401)
   ```

---

### Phase 3: Systematische Fehlerbehebung

**Priorität 1: Kritische Blocking-Issues**

1. **CORS-Fehler beheben**:
   - Stelle sicher, dass `CORSMiddleware` korrekt konfiguriert ist
   - Prüfe, ob `allow_origins` korrekt aus `.env` geladen wird
   - Teste mit verschiedenen Browsern (Chrome, Firefox, Safari)
   - Validiere Preflight (OPTIONS) Requests

2. **500 Internal Server Error beheben**:
   - Aktiviere detailliertes Error-Logging im Backend
   - Prüfe Backend-Logs für Stack-Traces
   - Validiere Datenbank-Transaktionen (Commit/Rollback)
   - Teste mit minimalen Request-Payloads

3. **422 Unprocessable Entity beheben**:
   - Prüfe FastAPI Route-Reihenfolge (spezifische Routes vor Parameter-Routes)
   - Validiere Query-Parameter und Request-Body gegen Pydantic Models
   - Teste mit verschiedenen Request-Kombinationen

**Priorität 2: Frontend-Backend Inkonsistenzen**

4. **API Response-Struktur vereinheitlichen**:
   - Entscheide: Soll Backend `{ data: ... }` wrappen oder Frontend direkt `ExperimentResponse` erwarten?
   - Implementiere konsistente Response-Struktur für alle Endpoints
   - Update TypeScript Interfaces entsprechend
   - Update API Client entsprechend

5. **Fehlerbehandlung verbessern**:
   - Implementiere zentrale Error-Handler im Frontend
   - Zeige benutzerfreundliche Fehlermeldungen (Toast-Notifications)
   - Logge Fehler für Debugging (aber nicht in Production)

**Priorität 3: Code-Qualität & Best Practices**

6. **Type Safety verbessern**:
   - Prüfe alle TypeScript `any` Types
   - Validiere Pydantic Model-Konsistenz
   - Implementiere Runtime-Validierung für API Responses

7. **Testing & Dokumentation**:
   - Erstelle Unit-Tests für kritische Komponenten
   - Dokumentiere API-Endpoints (OpenAPI/Swagger)
   - Erstelle Troubleshooting-Guide

---

### Phase 4: Performance & Robustheit

**Ziel**: System stabilisieren und optimieren

1. **Database Performance**:
   - Prüfe SQL-Queries auf N+1 Problems
   - Implementiere Database-Indizes für häufige Queries
   - Validiere Connection-Pooling

2. **API Performance**:
   - Implementiere Request-Caching (React Query)
   - Prüfe Response-Größen (Pagination)
   - Validiere Timeout-Handling

3. **Error Recovery**:
   - Implementiere Retry-Logic für fehlgeschlagene Requests
   - Validiere Graceful Degradation
   - Prüfe Circuit-Breaker Pattern für externe Services (LLM APIs)

---

### Phase 5: Validierung & Abschluss

**Ziel**: Vollständige System-Validierung

1. **End-to-End Test-Durchlauf**:
   - Führe alle Tests aus (Backend + Frontend)
   - Validiere kritische User-Flows manuell
   - Prüfe Browser-Kompatibilität

2. **Dokumentation**:
   - Update README mit Troubleshooting-Section
   - Dokumentiere bekannte Issues und Workarounds
   - Erstelle Deployment-Checklist

3. **Code-Review**:
   - Prüfe alle Änderungen auf Code-Qualität
   - Validiere Best Practices (Security, Performance, Maintainability)
   - Erstelle Changelog

---

## Erwartete Deliverables

1. **Fix-Report**: Detaillierte Liste aller gefundenen und behobenen Probleme
2. **Test-Results**: Vollständige Test-Suite mit Ergebnissen
3. **Updated Code**: Alle Fixes implementiert und getestet
4. **Documentation**: Updated README, API-Docs, Troubleshooting-Guide
5. **Recommendations**: Vorschläge für weitere Verbesserungen

---

## Spezifische Test-Szenarien

### Szenario 1: Experiment-Erstellung (Kritisch)
```
1. Frontend: Formular ausfüllen
2. Frontend: "Create Experiment" klicken
3. Backend: POST /api/experiments empfängt Request
4. Backend: Validiert Request gegen ExperimentConfig
5. Backend: Erstellt Experiment in Datenbank
6. Backend: Gibt ExperimentResponse zurück
7. Frontend: Empfängt Response
8. Frontend: Navigiert zu /experiments/{experiment_id}
9. Frontend: Lädt Experiment-Details
10. Frontend: Zeigt Experiment-Informationen an
```

**Erwartetes Ergebnis**: Alle Schritte erfolgreich, keine Fehler

### Szenario 2: CORS & Authentication
```
1. Browser: Sendet OPTIONS Preflight Request
2. Backend: Gibt CORS-Header zurück
3. Browser: Sendet POST Request mit Origin
4. Backend: Validiert API Key (falls enabled)
5. Backend: Verarbeitet Request
6. Backend: Gibt Response mit CORS-Headern zurück
```

**Erwartetes Ergebnis**: Keine CORS-Fehler, korrekte Authentication

### Szenario 3: Statistics Endpoint
```
1. Frontend: Lädt Dashboard
2. Frontend: Ruft GET /api/vulnerabilities/statistics auf
3. Backend: Route wird korrekt matched (nicht als /{vulnerability_id})
4. Backend: Gibt Statistics zurück
5. Frontend: Zeigt Statistics an
```

**Erwartetes Ergebnis**: Keine 422-Fehler, Statistics werden angezeigt

---

## Technische Anforderungen

- **Python 3.11+** mit aktiviertem venv
- **Node.js 20+** für Frontend
- **Ollama** läuft auf localhost:11434
- **SQLite** Datenbank initialisiert
- **Backend** läuft auf localhost:8889
- **Frontend** läuft auf localhost:5173

---

## Erfolgskriterien

✅ Alle Endpoints funktionieren ohne Fehler  
✅ CORS funktioniert für alle Origins  
✅ Frontend kann erfolgreich Experiments erstellen  
✅ Navigation funktioniert nach Experiment-Erstellung  
✅ Statistics-Endpoint gibt korrekte Daten zurück  
✅ Keine TypeScript-Fehler im Frontend  
✅ Keine Python-Linter-Fehler im Backend  
✅ Alle Tests bestehen  

---

**Bitte starte mit Phase 1 und arbeite systematisch durch alle Phasen. Dokumentiere jeden Schritt und alle gefundenen Probleme mit Lösungsvorschlägen.**

