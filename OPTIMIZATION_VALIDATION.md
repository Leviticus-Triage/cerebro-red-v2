# CEREBRO-RED v2 - Optimization Validation Playbook

## Overview

This document provides a comprehensive end-to-end validation checklist for CEREBRO-RED v2 optimizations, covering local (Ollama), cloud (OpenAI), and hybrid deployment scenarios.

---

## 1. Backend Unit Tests

### 1.1 Run All Tests
```bash
cd backend
docker compose exec cerebro-backend pytest -v
```

### 1.2 Targeted Test Suites

#### Serialization Tests
```bash
docker compose exec cerebro-backend pytest tests/test_strategy_persistence.py -v
```
**Acceptance Gate**: ✅ All 4 tests pass (strategy persistence, fallback tracking, API serialization, WebSocket consistency)

#### Strategy Rotation Tests
```bash
docker compose exec cerebro-backend pytest tests/test_strategy_rotation.py -v
```
**Acceptance Gate**: ✅ All tests pass, unused-first prioritization verified

#### Strategy Performance Tests
```bash
docker compose exec cerebro-backend pytest tests/test_strategy_performance.py -v
```
**Acceptance Gate**: ✅ All 8 tests pass:
- `test_unused_strategies_prioritized` - 5 strategies used in first 5 iterations
- `test_performance_tracking_updates` - Metrics update correctly
- `test_performance_based_selection` - Best strategy selected after all used
- `test_strategy_rotation_with_single_strategy` - Edge case handled
- `test_all_strategies_used_in_n_iterations` - N strategies in N iterations
- `test_performance_selection_without_judge_score` - Round-robin fallback
- `test_strategy_performance_success_rate_calculation` - Effectiveness formula correct
- `test_strategy_rotation_cleanup` - Cleanup works

#### Circuit Breaker Tests
```bash
docker compose exec cerebro-backend pytest tests/benchmark/test_circuit_breaker.py -v
```
**Acceptance Gate**: ✅ All tests pass:
- `test_circuit_breaker_state_transitions` - CLOSED→OPEN→HALF_OPEN→CLOSED
- `test_circuit_breaker_retry_behavior` - Retries on transient errors
- `test_error_classification` - Transient vs permanent errors classified
- `test_jitter_backoff` - Jitter applied to backoff delays
- `test_half_open_call_limit` - Max calls in HALF_OPEN respected

---

## 2. Frontend Build & Tests

### 2.1 Build Frontend
```bash
cd frontend
npm run build
```
**Acceptance Gate**: ✅ Build completes without errors

### 2.2 Run Playwright Tests (if available)
```bash
npx playwright test
```
**Acceptance Gate**: ✅ All E2E tests pass

### 2.3 Manual UI Verification
- [ ] Live Logs panel displays logs correctly
- [ ] Strategy column visible in Requests/Responses/All tabs
- [ ] Tasks tab shows strategy per task
- [ ] Iterations tab shows strategy badges
- [ ] Strategy Usage tab shows correct distribution
- [ ] Code Flow events display (verbosity >= 3)
- [ ] Errors tab shows meaningful error messages

---

## 3. Local E2E Test (Ollama)

### 3.1 Prerequisites
```bash
# Ensure Ollama is running with llama3.2:3b
ollama pull llama3.2:3b
ollama serve
```

### 3.2 Configuration
```bash
# .env settings for local test
TARGET_MODEL=ollama/llama3.2:3b
ATTACKER_MODEL=ollama/llama3.2:3b
JUDGE_MODEL=ollama/llama3.2:3b

# Circuit Breaker settings (relaxed for local)
CIRCUIT_BREAKER_FAILURE_THRESHOLD=15
CIRCUIT_BREAKER_TIMEOUT=120
```

### 3.3 Start Services
```bash
docker compose up -d
```

### 3.4 Create Test Experiment
- **Name**: "Local Ollama Validation Test"
- **Strategies**: Select 10 diverse strategies:
  1. `roleplay_injection`
  2. `jailbreak_dan`
  3. `jailbreak_aim`
  4. `obfuscation_base64`
  5. `context_flooding`
  6. `sycophancy`
  7. `indirect_injection`
  8. `authority_manipulation`
  9. `emotional_manipulation`
  10. `linguistic_evasion`
- **Max Iterations**: 15
- **Initial Prompts**: 3

### 3.5 Acceptance Gates

| Metric | Target | Actual |
|--------|--------|--------|
| All 10 strategies appear in logs | ✅ | ___ |
| Progress updates correctly | ✅ | ___ |
| Circuit-open rate | < 20% | ___% |
| Telemetry logs present | ✅ | ___ |
| Strategy rotation: unused-first | ✅ | ___ |
| Performance tracking updates | ✅ | ___ |

### 3.6 Verify Strategy Rotation
```bash
docker compose logs cerebro-backend | grep "\[Strategy Selection\]" | head -20
```
**Expected**: First 10 iterations show "Unused-first" reasoning, each strategy used once.

### 3.7 Verify Circuit Breaker
```bash
curl http://localhost:9000/health/circuit-breakers | jq
```
**Expected**: 
- `failure_rate < 0.2`
- `state: "closed"` for all providers

---

## 4. Cloud E2E Test (OpenAI)

### 4.1 Configuration
```bash
# .env settings for cloud test
TARGET_MODEL=openai/gpt-4o-mini
ATTACKER_MODEL=openai/gpt-4o-mini
JUDGE_MODEL=openai/gpt-4o-mini
OPENAI_API_KEY=sk-...

# Circuit Breaker settings (stricter for cloud)
CIRCUIT_BREAKER_FAILURE_THRESHOLD=10
CIRCUIT_BREAKER_TIMEOUT=60
```

### 4.2 Create Test Experiment
- Same configuration as Local E2E
- **Expected**: Faster latency, more stable circuit

### 4.3 Acceptance Gates

| Metric | Target | Actual |
|--------|--------|--------|
| All 10 strategies appear in logs | ✅ | ___ |
| Average latency | < 5000ms | ___ms |
| Circuit state | CLOSED | ___ |
| Token usage tracked | ✅ | ___ |
| Success rate | > 0% | ___% |

---

## 5. Hybrid E2E Test (Multi-Provider)

### 5.1 Configuration
```bash
# .env settings for hybrid test
TARGET_MODEL=ollama/llama3.2:3b
ATTACKER_MODEL=openai/gpt-4o-mini
JUDGE_MODEL=openai/gpt-4o-mini

OPENAI_API_KEY=sk-...
```

### 5.2 Acceptance Gates

| Metric | Target | Actual |
|--------|--------|--------|
| Multi-provider communication | ✅ | ___ |
| Target responses from Ollama | ✅ | ___ |
| Attacker mutations from OpenAI | ✅ | ___ |
| Judge evaluations from OpenAI | ✅ | ___ |
| No cross-provider errors | ✅ | ___ |

---

## 6. Metrics Capture

### 6.1 Extract Metrics from Audit Logs
```bash
# Strategy coverage
cat data/audit_logs.jsonl | jq -r 'select(.event_type == "iteration_complete") | .strategy' | sort | uniq -c

# Average latency per strategy
cat data/audit_logs.jsonl | jq -r 'select(.event_type == "iteration_complete") | "\(.strategy),\(.latency_ms)"' | \
  awk -F',' '{sum[$1]+=$2; count[$1]++} END {for(s in sum) print s, sum[s]/count[s]}'

# Token usage per strategy
cat data/audit_logs.jsonl | jq -r 'select(.event_type == "iteration_complete") | "\(.strategy),\(.tokens_used)"' | \
  awk -F',' '{sum[$1]+=$2; count[$1]++} END {for(s in sum) print s, sum[s]/count[s]}'

# Success score means per strategy
cat data/audit_logs.jsonl | jq -r 'select(.event_type == "iteration_complete") | "\(.strategy),\(.judge_score)"' | \
  awk -F',' '{sum[$1]+=$2; count[$1]++} END {for(s in sum) print s, sum[s]/count[s]}'
```

### 6.2 Metrics Summary Table

| Strategy | Count | Avg Latency (ms) | Avg Tokens | Avg Score |
|----------|-------|------------------|------------|-----------|
| roleplay_injection | ___ | ___ | ___ | ___ |
| jailbreak_dan | ___ | ___ | ___ | ___ |
| jailbreak_aim | ___ | ___ | ___ | ___ |
| obfuscation_base64 | ___ | ___ | ___ | ___ |
| context_flooding | ___ | ___ | ___ | ___ |
| sycophancy | ___ | ___ | ___ | ___ |
| indirect_injection | ___ | ___ | ___ | ___ |
| authority_manipulation | ___ | ___ | ___ | ___ |
| emotional_manipulation | ___ | ___ | ___ | ___ |
| linguistic_evasion | ___ | ___ | ___ | ___ |

### 6.3 Circuit Breaker Metrics

| Provider | State | Failures | Successes | Failure Rate |
|----------|-------|----------|-----------|--------------|
| ollama | ___ | ___ | ___ | ___% |
| openai | ___ | ___ | ___ | ___% |

---

## 7. Screenshot Checklist

Capture screenshots of the following UI components:

### 7.1 Live Logs Panel
- [ ] All tab with logs displaying
- [ ] Requests tab with Strategy column
- [ ] Responses tab with Strategy column
- [ ] Judge tab with evaluations

### 7.2 Strategy Usage Tab
- [ ] Selected strategies count
- [ ] Used strategies count
- [ ] Skipped strategies list
- [ ] Usage distribution chart

### 7.3 Iterations Tab
- [ ] Iteration cards with strategy badges
- [ ] Attack prompt display
- [ ] Target response display
- [ ] Judge reasoning and scores

### 7.4 Code Flow Tab (verbosity >= 3)
- [ ] Task start/end events
- [ ] Decision points
- [ ] Strategy selection events

### 7.5 Task Queue Tab
- [ ] Task list with status
- [ ] Strategy per task
- [ ] Queue position

### 7.6 Heatmap (if available)
- [ ] Score distribution visualization
- [ ] Strategy effectiveness comparison

---

## 8. Known Issues & Workarounds

### 8.1 Strategy Rotation Not Working
**Symptom**: Only 1-2 strategies used despite selecting many
**Cause**: `_get_next_strategy()` may not be called correctly, or experiment config not passing strategies
**Workaround**: Check backend logs for `[Strategy Selection]` messages

### 8.2 Live Logs Showing Empty `{}`
**Symptom**: Content column shows `{}` instead of actual data
**Cause**: WebSocket messages missing `content` field
**Workaround**: Check `metadata.prompt` or `metadata.response` instead

### 8.3 Circuit Breaker Opens Too Quickly
**Symptom**: Many "Circuit breaker is OPEN" errors
**Cause**: `FAILURE_THRESHOLD` too low
**Workaround**: Increase `CIRCUIT_BREAKER_FAILURE_THRESHOLD` to 15-20

### 8.4 Code Flow Tab Empty
**Symptom**: "No code-flow events yet" message
**Cause**: Verbosity level < 3
**Workaround**: Set verbosity to "Debug + Code Flow" (level 3)

---

## 9. Validation Sign-Off

| Test Suite | Status | Date | Tester |
|------------|--------|------|--------|
| Backend Unit Tests | ⬜ | ___ | ___ |
| Frontend Build | ⬜ | ___ | ___ |
| Local E2E (Ollama) | ⬜ | ___ | ___ |
| Cloud E2E (OpenAI) | ⬜ | ___ | ___ |
| Hybrid E2E | ⬜ | ___ | ___ |
| Metrics Captured | ⬜ | ___ | ___ |
| Screenshots Captured | ⬜ | ___ | ___ |

**Overall Validation Status**: ⬜ PENDING

---

## 10. Appendix: Quick Reference Commands

### Start Services
```bash
docker compose up -d
```

### View Backend Logs
```bash
docker compose logs -f cerebro-backend
```

### Check Circuit Breakers
```bash
curl http://localhost:9000/health/circuit-breakers | jq
```

### Run Specific Test
```bash
docker compose exec cerebro-backend pytest tests/test_strategy_performance.py::test_unused_strategies_prioritized -v
```

### Rebuild Frontend
```bash
cd frontend && npm run build && docker compose restart cerebro-frontend
```

### Reset Database
```bash
rm -f data/cerebro.db && docker compose restart cerebro-backend
```
