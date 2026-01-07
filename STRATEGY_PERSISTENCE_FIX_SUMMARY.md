# Strategy Persistence Bug Fix - Implementation Summary

**Date:** 2026-01-06  
**Status:** ✅ All Changes Implemented

## Overview

Fixed critical data inconsistency where WebSocket events showed correct strategies (jailbreak_dan, jailbreak_aim, jailbreak_dude) but JSON export/API showed only "roleplay_injection" for all iterations.

**Root Cause:** Exception handlers in orchestrator overwrote the `strategy` variable with `ROLEPLAY_INJECTION` fallback **after** WebSocket events were already sent with the original strategy.

## Implemented Changes

### 1. ✅ Database Schema Extended

**File:** `backend/core/database.py`

Added three new fields to `AttackIterationDB`:
- `intended_strategy` (String, nullable) - Originally selected strategy before fallbacks
- `strategy_fallback_occurred` (Boolean, default=False) - Whether fallback occurred
- `fallback_reason` (Text, nullable) - Exception message or reason for fallback

**Migration:** `backend/alembic/versions/005_add_strategy_tracking_fields.py` created

### 2. ✅ Pydantic Model Extended

**File:** `backend/core/models.py`

Added three new fields to `AttackIteration`:
- `intended_strategy: Optional[AttackStrategyType]`
- `strategy_fallback_occurred: bool = False`
- `fallback_reason: Optional[str] = None`

### 3. ✅ Orchestrator Exception Handling Overhauled

**File:** `backend/core/orchestrator.py`

**Changes:**
- Added `intended_strategy`, `fallback_occurred`, `fallback_reason` tracking before mutation attempt (line 776-778)
- Updated all 4 exception handlers (ValueError x2, KeyError, generic Exception) to:
  - Set `fallback_occurred = True`
  - Set `fallback_reason` with exception message
  - Log intended vs executed strategy in audit logs
  - Send WebSocket `strategy_fallback` event
  - Log explicit warning with context
- Updated both `AttackIteration` creation points (successful and failed) to include new fields

### 4. ✅ Repository Layer Updated

**File:** `backend/core/database.py`

**Changes in `AttackIterationRepository.create()`:**
- Added enum-to-string conversion with validation
- Added data integrity check: logs warning if strategies differ
- Saves all three new fields to database

### 5. ✅ API Response Serialization Improved

**Files:** 
- `backend/api/experiments.py`
- `backend/api/vulnerabilities.py`

**Changes:**
- `get_experiment_iterations()`: Added `intended_strategy`, `strategy_fallback_occurred`, `fallback_reason` to response
- `get_experiment_statistics()`: Added `strategy_fallback_count` and `strategy_fallback_rate`
- All vulnerability endpoints: Added validation to ensure `attack_strategy` is always a string

### 6. ✅ WebSocket Event for Strategy Fallback Added

**File:** `backend/api/websocket.py`

**New Function:** `send_strategy_fallback()`
- Sends notification when strategy fallback occurs
- Includes: intended_strategy, fallback_strategy, reason
- Broadcasts to all connected clients (verbosity level 1+)

### 7. ✅ Logging Improved

**File:** `backend/core/orchestrator.py`

**Changes:**
- Added explicit warning log for each strategy fallback
- Includes: experiment_id, iteration, intended_strategy, executed_strategy, fallback_reason, exception_type
- Enhanced audit log metadata with intended_strategy and fallback_strategy

### 8. ✅ Tests Created

**File:** `backend/tests/test_strategy_persistence.py`

**Test Scenarios:**
1. `test_strategy_persistence_on_success` - Strategy correctly persisted when no fallback
2. `test_strategy_persistence_on_fallback` - Both intended and executed strategies persisted on fallback
3. `test_api_serialization_consistency` - API returns consistent strategy values (strings, not enums)
4. `test_websocket_database_consistency` - Database values match expected WebSocket values

## Files Modified

1. `backend/core/database.py` - Schema + Repository
2. `backend/core/models.py` - Pydantic model
3. `backend/core/orchestrator.py` - Exception handling + iteration creation
4. `backend/api/experiments.py` - API serialization
5. `backend/api/vulnerabilities.py` - API serialization
6. `backend/api/websocket.py` - New fallback event
7. `backend/alembic/versions/005_add_strategy_tracking_fields.py` - Migration (NEW)
8. `backend/tests/test_strategy_persistence.py` - Tests (NEW)

## Next Steps

### Immediate (Required before testing):

1. **Run Alembic Migration:**
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Restart Backend:**
   ```bash
   docker compose restart cerebro-backend
   ```

3. **Run Tests:**
   ```bash
   cd backend
   pytest tests/test_strategy_persistence.py -v
   ```

### Validation Commands:

```bash
# 1. Verify migration
docker compose exec cerebro-backend alembic current

# 2. Check database schema
docker compose exec cerebro-backend python -c "from core.database import AttackIterationDB; print([c.name for c in AttackIterationDB.__table__.columns])"

# 3. Test API response
curl http://localhost:9000/api/experiments/{experiment_id}/iterations | jq '.data.iterations[] | {iteration: .iteration_number, intended: .intended_strategy, executed: .strategy_used, fallback: .strategy_fallback_occurred}'
```

## Expected Behavior After Fix

### Before:
- WebSocket: `strategy: "jailbreak_dan"` ✅
- Database: `strategy_used: "roleplay_injection"` ❌
- API: `"strategy_used": "roleplay_injection"` ❌

### After:
- WebSocket: `strategy: "jailbreak_dan"` ✅
- Database: 
  - `strategy_used: "roleplay_injection"` (executed)
  - `intended_strategy: "jailbreak_dan"` (intended) ✅
  - `strategy_fallback_occurred: true` ✅
  - `fallback_reason: "ValueError: ..."` ✅
- API: 
  - `"strategy_used": "roleplay_injection"` ✅
  - `"intended_strategy": "jailbreak_dan"` ✅
  - `"strategy_fallback_occurred": true` ✅
  - `"fallback_reason": "ValueError: ..."` ✅

## Backward Compatibility

✅ **Fully backward compatible:**
- New fields are nullable (for existing data)
- Default values set (fallback_occurred = False)
- Old API responses still work (new fields are optional)
- Migration safely adds columns without breaking existing queries

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Migration breaks existing data | Fields are nullable, defaults set |
| Performance overhead | Minimal (3 additional fields) |
| Frontend compatibility | Fields are optional in API responses |
| Test coverage | 4 comprehensive test scenarios |

## Success Criteria

✅ Database schema extended with 3 new fields  
✅ Migration created and ready to run  
✅ All exception handlers track intended vs executed strategy  
✅ Repository saves all new fields  
✅ API returns both intended and executed strategies  
✅ WebSocket sends fallback events  
✅ Tests created for all scenarios  
✅ No linter errors  

## Notes

- **No breaking changes:** All changes are additive
- **Data integrity:** Logs warning if strategies differ unexpectedly
- **Observability:** Full audit trail of strategy selection and fallbacks
- **User transparency:** Users can now see which strategies were intended vs actually executed

---

**Implementation Complete** ✅  
**Ready for:** Migration execution and testing
