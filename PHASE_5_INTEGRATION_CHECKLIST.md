# Phase 5 Integration Checklist

Diese Checkliste stellt sicher, dass der Orchestrator (Phase 5) alle Phase 5.5 Anforderungen erfüllt.

## Mutator Integration

- [ ] `mutate()` Methode routet zu `_mutate_sycophancy()` für `AttackStrategyType.SYCOPHANCY`
- [ ] `mutate()` Methode routet zu `_mutate_linguistic_evasion()` für `AttackStrategyType.LINGUISTIC_EVASION`
- [ ] Beide Strategien verwenden `PayloadManager.get_templates()` mit Fehlerbehandlung
- [ ] Fallback-Templates werden bei PayloadManager-Fehlern verwendet
- [ ] Fehler werden via `audit_logger.log_error()` geloggt

## Judge Integration

- [ ] `SecurityJudge.evaluate()` gibt alle 7 Scores zurück (JudgeScore-Model)
- [ ] `hallucination_score`, `bias_score`, `logical_consistency_score`, `sycophancy_score` sind vorhanden
- [ ] `get_feedback_dict()` enthält alle relevanten Scores für PAIR-Feedback

## Orchestrator Implementation

### Vulnerability Finding

- [ ] `_create_vulnerability_finding()` integriert alle 7 Scores in Description
- [ ] Severity-Berechnung verwendet gewichtete Formel (40% overall, 30% harmful, 10% hallucination, 10% bias, 10% policy)
- [ ] Metadata enthält alle Score-Werte für spätere Analyse

### Telemetry

- [ ] `log_judge_evaluation()` wird mit allen 7 Scores in metadata aufgerufen
- [ ] `log_mutation()` wird für jede Strategie (inkl. SYCOPHANCY, LINGUISTIC_EVASION) aufgerufen
- [ ] `log_strategy_transition()` wird bei Strategie-Wechseln aufgerufen

### Error Handling

- [ ] `ValueError` für fehlendes Feedback (REPHRASE_SEMANTIC) wird spezifisch behandelt
- [ ] `KeyError` für fehlende Templates (SYCOPHANCY, LINGUISTIC_EVASION) wird spezifisch behandelt
- [ ] Fallback zu `ROLEPLAY_INJECTION` bei Strategie-Fehlern
- [ ] Alle Fehler werden mit Context geloggt

### Mitigation Suggestions

- [ ] `_generate_mitigation_suggestions()` deckt alle 8 Strategien ab
- [ ] SYCOPHANCY hat mindestens 4 Suggestions
- [ ] LINGUISTIC_EVASION hat mindestens 4 Suggestions

### Strategy Selection

- [ ] `_select_initial_strategy()` berücksichtigt SYCOPHANCY für agreement-seeking prompts
- [ ] `_select_initial_strategy()` berücksichtigt LINGUISTIC_EVASION für academic/hypothetical prompts

## Testing

- [ ] `test_sycophancy_strategy_with_payload_manager` passed
- [ ] `test_sycophancy_fallback_when_templates_missing` passed
- [ ] `test_linguistic_evasion_strategy_with_payload_manager` passed
- [ ] `test_linguistic_evasion_fallback_euphemism_mapping` passed
- [ ] `test_vulnerability_finding_includes_all_7_scores` passed
- [ ] `test_severity_calculation_uses_weighted_formula` passed
- [ ] `test_telemetry_metadata_includes_all_7_scores` passed
- [ ] `test_mitigation_suggestions_cover_all_8_strategies` passed
- [ ] `test_judge_returns_all_7_scores` passed

## Documentation

- [ ] `orchestrator_requirements.md` dokumentiert alle Anforderungen
- [ ] `telemetry_phase_5_5_spec.md` dokumentiert erweiterte Metadaten
- [ ] Code-Kommentare referenzieren PAIR Paper, PyRIT, OWASP
- [ ] Docstrings enthalten Beispiele für neue Strategien

## Performance

- [ ] Keine Performance-Regression durch neue Strategien
- [ ] Fallback-Mechanismen sind schnell (< 10ms)
- [ ] Telemetry-Logging blockiert nicht den PAIR-Loop

## Backward Compatibility

- [ ] Alte Experiments (ohne neue Scores) funktionieren weiterhin
- [ ] Default-Werte (0.0) für neue Scores in JudgeScore-Model
- [ ] Telemetry-Logs sind abwärtskompatibel (neue Felder optional)

