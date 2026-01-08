# CEREBRO-RED v2 Dokumentation

[🇬🇧 English](../en/README.md) | [🇩🇪 Deutsch](README.md)

Willkommen zur CEREBRO-RED v2 Dokumentation. Diese Dokumentation bietet umfassende Anleitungen zur Nutzung, Konfiguration, Bereitstellung und zum Verständnis der Plattform.

## 📚 Dokumentationsübersicht

### Erste Schritte
- **[Benutzerhandbuch](benutzerhandbuch.md)** - Vollständige Anleitung zur Nutzung von CEREBRO-RED v2
  - Installation und Einrichtung
  - Erstellen und Verwalten von Experimenten
  - Verstehen von Ergebnissen und Telemetrie
  - Beheben häufiger Probleme

### Konfiguration
- **[Konfigurationsanleitung](konfiguration.md)** - Umgebungsvariablen und Einstellungen
  - LLM-Provider-Konfiguration (Ollama, Azure OpenAI, OpenAI)
  - Datenbank- und Speichereinstellungen
  - API-Sicherheit und Authentifizierung
  - Rate Limiting und Circuit Breaker

### Bereitstellung
- **[Bereitstellungsanleitung](bereitstellung.md)** - Produktions- und Demo-Bereitstellung
  - Lokale Docker-Bereitstellung
  - Railway Cloud-Bereitstellung
  - Umgebungseinrichtung und Health Checks
  - Demo-Modus-Konfiguration

## 🚀 Schnelllinks

- **Haupt-Repository**: [github.com/Leviticus-Triage/cerebro-red-v2](https://github.com/Leviticus-Triage/cerebro-red-v2)
- **Schnellstart**: Siehe [Benutzerhandbuch - Installation](benutzerhandbuch.md#installation)
- **API-Referenz**: Verfügbar am `/docs` Endpunkt, wenn Backend läuft
- **Live-Demo**: [Railway Demo-Instanz](https://cerebro-red-v2.railway.app) (nur Lese-Zugriff)

## 📖 Dokumentationsstruktur

```
docs/
├── en/                    # Englische Dokumentation (primär)
│   ├── README.md         # Dokumentations-Hub
│   ├── user-guide.md     # Vollständige Benutzerdokumentation
│   ├── configuration.md  # Umgebungsvariablen und Einstellungen
│   ├── deployment.md     # Bereitstellungsanleitungen
│   ├── architecture.md   # Technische Architektur
│   └── security.md       # Sicherheitsüberlegungen
├── de/                    # Deutsche Dokumentation (sekundär)
│   ├── README.md         # Dieser Datei - Dokumentations-Hub
│   ├── benutzerhandbuch.md
│   ├── konfiguration.md
│   └── bereitstellung.md
└── metadata.yml          # Dokumentations-Tracking-Metadaten
```

## 🔄 Sprachumschaltung

Jedes Dokument enthält Sprachumschalter-Links am Anfang:
- **Englische** Dokumente verlinken zu entsprechenden deutschen Übersetzungen
- **Deutsche** Dokumente verlinken zurück zu englischen Versionen
- Verwenden Sie den Sprachumschalter, um zwischen Sprachen zu navigieren

## 📝 Dokumentation beitragen

Verbesserungen der Dokumentation sind willkommen! Bitte:
1. Folgen Sie der bestehenden Struktur und dem Stil
2. Halten Sie englische und deutsche Versionen synchron
3. Verwenden Sie relative Pfade für interne Links
4. Aktualisieren Sie `docs/metadata.yml`, wenn neue Dokumente hinzugefügt werden

## 🔗 Externe Ressourcen

- **Forschungsarbeit**: [PAIR Algorithmus](https://arxiv.org/abs/2310.08419)
- **Upstream-Projekt**: [hexstrike-ai](https://github.com/0x4m4/hexstrike-ai)
- **Portfolio**: [exodus-hensen.site](https://exodus-hensen.site)

---

**Zuletzt aktualisiert**: 2026-01-08  
**Dokumentationsversion**: 2.0.0
