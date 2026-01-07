# Telemetry Extensions for Phase 5.5

## Erweiterte Metadaten für log_judge_evaluation()

Die `log_judge_evaluation()` Methode muss alle 7 Evaluationskriterien in den Metadaten loggen:

### Erforderliche Metadaten-Felder

```python
metadata = {
    # Alle 7 Scores (KRITISCH)
    "jailbreak_success_score": float,  # 0-10
    "harmful_content_score": float,    # 0-10
    "hallucination_score": float,      # 0-10 (NEU)
    "bias_score": float,               # 0-10 (NEU)
    "logical_consistency_score": float, # 0-10 (NEU)
    "sycophancy_score": float,         # 0-10 (NEU)
    "policy_violation_score": float,   # 0-10
    
    # Zusätzliche Kontextinformationen
    "fallback_used": bool,             # Regex-Fallback verwendet?
    "refusal_level": str,              # RefusalLevel enum value
    "strategy": str,                   # AttackStrategyType value
    "iteration_number": int,           # Iteration im PAIR-Loop
    "confidence": float,               # Judge confidence (0-1)
    
    # Optional (für erweiterte Analyse)
    "target_response_length": int,
    "judge_model": str,
    "parsing_method": str,             # "json", "regex", "default"
}
```

### Beispiel-Aufruf

```python
audit_logger.log_judge_evaluation(
    experiment_id=experiment_id,
    iteration=i,
    score=judge_score.overall_score,
    reasoning=judge_score.reasoning,
    model_judge=judge_score.judge_model,
    model_target=target_response.model,
    latency_ms=judge_latency_ms,
    confidence=judge_score.confidence,
    tokens_used=target_response.tokens_used,
    metadata={
        "jailbreak_success_score": judge_score.jailbreak_success_score,
        "harmful_content_score": judge_score.harmful_content_score,
        "hallucination_score": judge_score.hallucination_score,
        "bias_score": judge_score.bias_score,
        "logical_consistency_score": judge_score.logical_consistency_score,
        "sycophancy_score": judge_score.sycophancy_score,
        "policy_violation_score": judge_score.policy_violation_score,
        "fallback_used": judge_score.fallback_used,
        "strategy": strategy.value,
        "iteration_number": i
    }
)
```

### JSONL-Format

Jeder Log-Eintrag wird als JSON-Zeile geschrieben:

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "event_type": "judge_evaluation",
  "experiment_id": "uuid",
  "iteration_number": 5,
  "model_judge": "gpt-4",
  "model_target": "llama2-7b",
  "success_score": 8.5,
  "latency_ms": 150,
  "tokens_used": 200,
  "metadata": {
    "jailbreak_success_score": 9.0,
    "harmful_content_score": 8.0,
    "hallucination_score": 7.5,
    "bias_score": 6.0,
    "logical_consistency_score": 5.5,
    "sycophancy_score": 7.0,
    "policy_violation_score": 8.5,
    "fallback_used": false,
    "strategy": "sycophancy",
    "iteration_number": 5,
    "confidence": 0.9
  }
}
```

## Wissenschaftliche Analyse-Queries

Mit den erweiterten Metadaten können folgende Analysen durchgeführt werden:

### 1. Score-Korrelationen

```python
# Korrelation zwischen Hallucination und Jailbreak Success
SELECT 
    AVG(metadata->>'hallucination_score') as avg_hallucination,
    AVG(metadata->>'jailbreak_success_score') as avg_jailbreak
FROM audit_logs
WHERE event_type = 'judge_evaluation'
GROUP BY metadata->>'strategy';
```

### 2. Strategie-Effektivität

```python
# Welche Strategie erzeugt die meisten Bias-Probleme?
SELECT 
    metadata->>'strategy' as strategy,
    AVG(CAST(metadata->>'bias_score' AS FLOAT)) as avg_bias
FROM audit_logs
WHERE event_type = 'judge_evaluation'
GROUP BY metadata->>'strategy'
ORDER BY avg_bias DESC;
```

### 3. Sycophancy-Anfälligkeit

```python
# Welche Target-Modelle sind anfällig für Sycophancy?
SELECT 
    model_target,
    AVG(CAST(metadata->>'sycophancy_score' AS FLOAT)) as avg_sycophancy,
    COUNT(*) as total_evaluations
FROM audit_logs
WHERE event_type = 'judge_evaluation'
  AND metadata->>'strategy' = 'sycophancy'
GROUP BY model_target
ORDER BY avg_sycophancy DESC;
```

