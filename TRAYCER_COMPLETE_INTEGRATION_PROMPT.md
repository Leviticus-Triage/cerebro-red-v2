# Traycer Prompt: Vollständige Integration aller Attack Strategies und Template-System

## Kontext und Problemstellung

Das CEREBRO-RED v2 Tool zeigt im Frontend 44 verschiedene Attack Strategies an, aber:
1. **Nicht alle Strategien werden tatsächlich implementiert/getestet** - Trotz Auswahl im Frontend werden viele Strategien nicht verwendet
2. **Fehlende Jailbreak-Integration** - Repos wurden heruntergeladen (L1B3RT4S, PyRIT, llamator, Model-Inversion-Attack-ToolBox), aber deren Jailbreak-Techniken sind noch nicht integriert
3. **Kein Template-System** - Experiment-Konfigurationen können nicht gespeichert/geladen werden, alles muss jedes Mal neu eingegeben werden
4. **Strategie-Auswahl wird ignoriert** - Ausgewählte Strategien werden nicht korrekt im PAIR-Loop verwendet

## Aufgabe für Traycer

Erstelle einen **detaillierten, umfassenden Phasenplan**, der:

1. **Alle 44 im Frontend angezeigten Attack Strategies vollständig implementiert**
2. **Jailbreak-Techniken aus den Repos analysiert und integriert**
3. **Template-System für Experiment-Konfigurationen implementiert**
4. **Strategie-Auswahl und -Verwendung im Orchestrator korrigiert**
5. **Umfassende Tests, Debugging und Fixes durchführt**

## Verfügbare Repos und Ressourcen

Folgende Repos wurden bereits heruntergeladen und befinden sich im Projektverzeichnis:
- `L1B3RT4S/` - Jailbreak-Techniken und Templates
- `PyRIT/` - Microsoft AI Red Team Toolkit
- `llamator/` - LLAMATOR LLM Vulnerability Scanner
- `Model-Inversion-Attack-ToolBox/` - Model Inversion Angriffe
- `AI-llm-red-team-handbook/` - Red Team Handbuch
- `NVIDIA AI Red Team/` - NVIDIA Red Team Ressourcen
- `Offensive ML Playbook/` - Offensive ML Techniken
- `Atlan-ML-learning-for-red-teams_Vorlage/` - Red Team Templates
- `FiveStars-LLM-Security/` - LLM Security Forschung
- `LLAMATOR-LLM-VULN-SCANNER/` - Vulnerability Scanner
- `OWASP Top 10 for LLM Applications/` - OWASP Standards

## Frontend-Strategien (44 total)

### Obfuscation (8 Strategien)
1. obfuscation_base64
2. obfuscation_leetspeak
3. obfuscation_rot13
4. obfuscation_unicode
5. obfuscation_morse
6. obfuscation_ascii_art
7. obfuscation_token_smuggling
8. obfuscation_binary

### Jailbreaks (7 Strategien)
9. jailbreak_dan
10. jailbreak_aim
11. jailbreak_stan
12. jailbreak_dude
13. jailbreak_developer_mode
14. crescendo_attack
15. many_shot_jailbreak
16. skeleton_key

### Prompt Injection (4 Strategien)
17. direct_injection
18. indirect_injection
19. payload_splitting
20. virtualization

### Context Manipulation (3 Strategien)
21. context_flooding
22. context_ignoring
23. conversation_reset

### Social Engineering (4 Strategien)
24. roleplay_injection
25. authority_manipulation
26. emotional_manipulation
27. urgency_exploitation

### Semantic Attacks (4 Strategien)
28. sycophancy
29. rephrase_semantic
30. translation_attack
31. linguistic_evasion

### System Prompt Attacks (2 Strategien)
32. system_prompt_extraction
33. system_prompt_override

### RAG Attacks (3 Strategien)
34. rag_poisoning
35. rag_bypass
36. echoleak

### Adversarial ML (2 Strategien)
37. adversarial_suffix
38. gradient_based

### Bias/Hallucination (3 Strategien)
39. bias_probe
40. hallucination_probe
41. misinformation_injection

### MCP Attacks (2 Strategien)
42. mcp_tool_injection
43. mcp_context_poisoning

### Advanced Research (1 Strategie)
44. research_pre_jailbreak

## Anforderungen an den Phasenplan

### Phase 1: Analyse und Inventarisierung
- [ ] Analysiere alle 44 Frontend-Strategien gegen `backend/core/models.py` `AttackStrategyType` Enum
- [ ] Identifiziere fehlende Strategien im Backend
- [ ] Analysiere alle heruntergeladenen Repos auf Jailbreak-Techniken
- [ ] Erstelle Mapping: Frontend-Strategie → Backend-Enum → Implementierung
- [ ] Dokumentiere fehlende Implementierungen

### Phase 2: Strategie-Implementierung
- [ ] Implementiere alle fehlenden Strategien in `backend/core/mutator.py` oder `backend/core/attack_strategies.py`
- [ ] Integriere Jailbreak-Techniken aus L1B3RT4S, PyRIT, llamator
- [ ] Erstelle/Erweitere Payload-Templates in `backend/data/payloads.json`
- [ ] Stelle sicher, dass jede Strategie:
  - Einen eindeutigen `AttackStrategyType` Enum-Wert hat
  - Eine funktionierende `mutate()` Implementierung hat
  - Korrekte Payload-Templates verwendet
  - Fehlerbehandlung hat

### Phase 3: Strategie-Auswahl und -Verwendung korrigieren
- [ ] Analysiere `backend/core/orchestrator.py` `_run_pair_loop()`:
  - Wie werden ausgewählte Strategien aus `experiment_config.strategies` verwendet?
  - Werden alle ausgewählten Strategien tatsächlich getestet?
  - Gibt es eine Strategie-Rotation oder werden nur die ersten verwendet?
- [ ] Implementiere korrekte Strategie-Auswahl:
  - Wenn mehrere Strategien ausgewählt sind, rotiere durch alle
  - Verwende Strategie-Analyse basierend auf Judge-Scores
  - Stelle sicher, dass keine Strategie übersprungen wird
- [ ] Fixe Strategie-Transition-Logik in `_select_strategy()` oder ähnlichen Methoden

### Phase 4: Template-System implementieren
- [ ] Backend: Erstelle `ExperimentTemplate` Model in `backend/core/models.py`
- [ ] Backend: Erstelle API-Endpunkte:
  - `POST /api/templates` - Template speichern
  - `GET /api/templates` - Alle Templates auflisten
  - `GET /api/templates/{id}` - Template laden
  - `PUT /api/templates/{id}` - Template aktualisieren
  - `DELETE /api/templates/{id}` - Template löschen
- [ ] Backend: Erstelle `ExperimentTemplateRepository` in `backend/core/database.py`
- [ ] Backend: Erstelle Migration für `experiment_templates` Tabelle
- [ ] Frontend: Erstelle `TemplatesPage` Komponente
- [ ] Frontend: Erstelle Template-Formular (Speichern/Laden)
- [ ] Frontend: Integriere Template-Auswahl in Experiment-Erstellung
- [ ] Frontend: Zeige gespeicherte Templates in Experiment-Formular

### Phase 5: Integration aus Repos
- [ ] **L1B3RT4S**: Analysiere Jailbreak-Techniken und Templates
- [ ] **PyRIT**: Extrahiere Attack-Strategien und Scoring-Methoden
- [ ] **llamator**: Integriere Vulnerability-Scanning-Techniken
- [ ] **Model-Inversion-Attack-ToolBox**: Analysiere Model-Inversion-Angriffe
- [ ] Erstelle Mapping: Repo-Technik → CEREBRO-RED Strategie
- [ ] Integriere neue Techniken als neue `AttackStrategyType` Werte oder erweitere bestehende
- [ ] Erstelle Payload-Templates basierend auf Repo-Inhalten

### Phase 6: Testing und Validierung
- [ ] Erstelle Unit-Tests für jede neue Strategie
- [ ] Erstelle Integration-Tests für Strategie-Auswahl
- [ ] Teste Template-System (Speichern/Laden)
- [ ] Teste, dass alle ausgewählten Strategien tatsächlich verwendet werden
- [ ] Validiere, dass keine Strategie übersprungen wird
- [ ] Teste Strategie-Rotation über mehrere Iterationen

### Phase 7: Debugging und Fixes
- [ ] Debugge Strategie-Auswahl-Logik
- [ ] Fixe alle Fehler in Strategie-Implementierungen
- [ ] Stelle sicher, dass Payload-Templates korrekt geladen werden
- [ ] Fixe Template-System-Bugs
- [ ] Validiere Frontend-Backend-Kompatibilität

### Phase 8: Dokumentation
- [ ] Dokumentiere alle implementierten Strategien
- [ ] Erstelle Mapping-Dokument: Frontend → Backend → Implementierung
- [ ] Dokumentiere Template-System-Usage
- [ ] Aktualisiere README.md mit neuen Features
- [ ] Erstelle Beispiel-Templates

## Technische Details

### Backend-Struktur
- `backend/core/models.py` - `AttackStrategyType` Enum erweitern
- `backend/core/mutator.py` - Strategie-Implementierungen
- `backend/core/attack_strategies.py` - Strategie-Registry
- `backend/core/orchestrator.py` - Strategie-Auswahl-Logik
- `backend/data/payloads.json` - Payload-Templates
- `backend/api/experiments.py` - Experiment-API
- `backend/api/templates.py` - Template-API (neu)

### Frontend-Struktur
- `frontend/src/pages/ExperimentCreate.tsx` - Strategie-Auswahl
- `frontend/src/pages/TemplatesPage.tsx` - Template-Management (neu)
- `frontend/src/components/StrategySelector.tsx` - Strategie-UI
- `frontend/src/types/api.ts` - TypeScript-Types

### Datenbank
- Neue Tabelle: `experiment_templates`
  - `id` (UUID, Primary Key)
  - `name` (String)
  - `description` (String, optional)
  - `config_json` (JSON) - Gespeicherte ExperimentConfig
  - `created_at` (DateTime)
  - `updated_at` (DateTime)
  - `user_id` (String, optional) - Für Multi-User-Support

## Erfolgskriterien

✅ **Alle 44 Frontend-Strategien sind implementiert und funktionieren**
✅ **Jailbreak-Techniken aus Repos sind integriert**
✅ **Template-System funktioniert vollständig (Speichern/Laden)**
✅ **Ausgewählte Strategien werden korrekt verwendet (keine werden übersprungen)**
✅ **Alle Tests bestehen**
✅ **Keine kritischen Bugs**
✅ **Dokumentation ist vollständig**

## Erwartetes Ergebnis

Ein **detaillierter Phasenplan** mit:
1. **Konkreten Aufgaben** für jede Phase
2. **Datei-spezifischen Änderungen** (welche Dateien müssen wie geändert werden)
3. **Code-Beispielen** wo nötig
4. **Test-Strategien** für jede Phase
5. **Validierungs-Kriterien** für jede Phase
6. **Risiko-Analyse** und Mitigation-Strategien

Der Plan soll **so detailliert sein**, dass Traycer ihn Schritt-für-Schritt abarbeiten kann, ohne weitere Klärungen zu benötigen.

## Wichtige Hinweise

- **Nicht abbrechen** - Der Plan muss vollständig sein
- **Explorieren** - Analysiere alle Repos gründlich
- **Testen** - Jede Implementierung muss getestet werden
- **Dokumentieren** - Alle Änderungen müssen dokumentiert werden
- **Validieren** - Stelle sicher, dass Frontend und Backend synchron sind

---

**Erstelle jetzt den umfassenden Phasenplan für Traycer!**
