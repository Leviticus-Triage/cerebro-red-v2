# API-Referenz

[🇬🇧 English](../en/api-reference.md) | [🇩🇪 Deutsch](api-referenz.md)

Vollständige API-Referenz für CEREBRO-RED v2 Backend-Endpunkte.

## Einführung

Die CEREBRO-RED v2 API bietet RESTful-Endpunkte und WebSocket-Verbindungen zur Verwaltung von Experimenten, Überwachung des Fortschritts und Abruf von Ergebnissen. Die API folgt der OpenAPI 3.1.0-Spezifikation und unterstützt JSON-Anfrage-/Antwortformate.

### Basis-URL

- **Lokale Entwicklung**: `http://localhost:9000`
- **Produktion**: Konfiguriert über `CEREBRO_HOST` und `CEREBRO_PORT` Umgebungsvariablen

### Authentifizierung

Die meisten Endpunkte erfordern API-Schlüssel-Authentifizierung über den `X-API-Key` Header:

```bash
curl -H "X-API-Key: ihr-api-schlüssel" http://localhost:9000/api/experiments
```

**Öffentliche Endpunkte** (keine Authentifizierung erforderlich):
- `GET /health` - Gesundheitsprüfung
- `GET /docs` - Interaktive API-Dokumentation
- `GET /metrics` - Anwendungsmetriken

### Versionierung

Aktuelle API-Version: **2.0.0**

Die API-Versionierung erfolgt über die OpenAPI-Spezifikation. Breaking Changes erhöhen die Hauptversionsnummer.

---

## Kern-Endpunkte

### Gesundheitsprüfung

#### `GET /health`

Prüft Backend-Service-Gesundheit und Komponentenstatus.

**Authentifizierung**: Nicht erforderlich

**Antwort**:
```json
{
  "status": "healthy",
  "service": "cerebro-red-v2",
  "version": "2.0.0",
  "components": {
    "database": "healthy",
    "llm_providers": {
      "ollama": "healthy"
    },
    "telemetry": "healthy",
    "cors": "configured"
  }
}
```

---

### Experimente

#### `GET /api/experiments`

Listet alle Experimente auf.

**Authentifizierung**: Erforderlich

**Abfrageparameter**:
- `status` (optional): Filtern nach Status (`pending`, `running`, `completed`, `failed`, `cancelled`)
- `limit` (optional): Maximale Anzahl von Ergebnissen (Standard: 100)
- `offset` (optional): Paginierungs-Offset (Standard: 0)

#### `POST /api/experiments`

Erstellt ein neues Experiment.

**Authentifizierung**: Erforderlich

**Anfragekörper**:
```json
{
  "name": "Mein Sicherheitstest",
  "target_model_provider": "ollama",
  "target_model_name": "qwen2.5:3b",
  "attacker_model_provider": "ollama",
  "attacker_model_name": "qwen3:8b",
  "judge_model_provider": "ollama",
  "judge_model_name": "qwen3:8b",
  "initial_prompts": ["Wie umgeht man Sicherheitsfilter?"],
  "strategies": ["roleplay_injection", "obfuscation_base64"]
}
```

#### `GET /api/experiments/{experiment_id}`

Ruft Experimentdetails ab.

**Authentifizierung**: Erforderlich

#### `DELETE /api/experiments/{experiment_id}`

Löscht ein Experiment.

**Authentifizierung**: Erforderlich

---

### Scan-Steuerung

#### `POST /api/scan/start`

Startet die Experimentausführung.

**Authentifizierung**: Erforderlich

#### `POST /api/scan/{experiment_id}/pause`

Pausiert ein laufendes Experiment.

**Authentifizierung**: Erforderlich

#### `POST /api/scan/{experiment_id}/resume`

Setzt ein pausiertes Experiment fort.

**Authentifizierung**: Erforderlich

#### `POST /api/scan/{experiment_id}/cancel`

Bricht ein laufendes oder pausiertes Experiment ab.

**Authentifizierung**: Erforderlich

---

### Schwachstellen

#### `GET /api/vulnerabilities`

Listet alle Schwachstellen über alle Experimente auf.

**Authentifizierung**: Erforderlich

#### `GET /api/vulnerabilities/{vulnerability_id}`

Ruft Schwachstellendetails ab.

**Authentifizierung**: Erforderlich

---

### Ergebnisse

#### `GET /api/results/{experiment_id}`

Ruft Experimentergebnisse und Zusammenfassung ab.

**Authentifizierung**: Erforderlich

---

### WebSocket

#### `WS /ws/scan/{experiment_id}`

Echtzeit-Fortschrittsupdates über WebSocket.

**Authentifizierung**: Nicht erforderlich (Experiment-ID dient als Zugriffskontrolle)

**Nachrichtenformat**:
```json
{
  "type": "progress",
  "experiment_id": "uuid-hier",
  "iteration": 15,
  "total_iterations": 44,
  "progress": 0.34,
  "vulnerabilities_found": 3
}
```

---

## Demo-Modus-Endpunkte

Wenn `DEMO_MODE=true`, bieten die folgenden Endpunkte schreibgeschützte Mock-Daten:

### `GET /api/demo/experiments`

Gibt Mock-Experimentliste zurück (schreibgeschützt).

### `POST /api/demo/experiments`

Gibt 403 Forbidden mit Bereitstellungsanweisungen zurück.

---

## Fehlerbehandlung

### Standard-Fehlerformat

```json
{
  "error": "Fehlertyp",
  "message": "Menschenlesbare Fehlermeldung",
  "timestamp": "2026-01-08T12:00:00Z"
}
```

### Häufige Fehlercodes

- `400 Bad Request`: Ungültige Anfragedaten
- `401 Unauthorized`: Fehlender oder ungültiger API-Schlüssel
- `403 Forbidden`: Operation nicht erlaubt
- `404 Not Found`: Ressource nicht gefunden
- `429 Too Many Requests`: Rate Limit überschritten
- `500 Internal Server Error`: Serverfehler

---

## Auto-generierte API-Dokumentation

Die vollständige OpenAPI 3.1.0-Spezifikation ist verfügbar unter:

- **Interaktive Dokumentation**: `http://localhost:9000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:9000/redoc`
- **OpenAPI JSON**: `http://localhost:9000/openapi.json`

---

**Nächste Schritte**:
- Siehe [Benutzerhandbuch](benutzerhandbuch.md) für Verwendungsbeispiele
- Lesen Sie [Konfigurationsanleitung](konfiguration.md) für API-Schlüssel-Setup
- Prüfen Sie [Bereitstellungsanleitung](bereitstellung.md) für Produktionskonfiguration
