# Rollback Guide

This guide provides step-by-step procedures for rolling back CEREBRO-RED v2 to a previous working state when experiments fail or critical bugs are introduced.

## Table of Contents

1. [Finding the Last Known Good Commit](#finding-the-last-known-good-commit)
2. [Full Rollback Procedure](#full-rollback-procedure)
3. [Selective File Rollback](#selective-file-rollback)
4. [Git Revert Flow](#git-revert-flow)
5. [Rebuild and Restart](#rebuild-and-restart)
6. [Verification Steps](#verification-steps)
7. [Minimal Experiment Sanity Test](#minimal-experiment-sanity-test)
8. [Volume Mount Sanity Check](#volume-mount-sanity-check)
9. [Stashing Work in Progress](#stashing-work-in-progress)

## Finding the Last Known Good Commit

### Method 1: Git Log Search

```bash
cd cerebro-red-v2

# View recent commits with messages
git log --oneline -20

# Search for commits mentioning "fix", "working", "tested"
git log --oneline --grep="fix\|working\|tested" -10

# View commits with file changes
git log --oneline --stat -10
```

### Method 2: Check CHANGELOG or Commit Messages

```bash
# Look for documented working states
cat CHANGELOG.md | grep -A 5 "working\|tested\|verified"

# Or check commit messages for test results
git log --format="%h %s" -30 | grep -i "test\|pass\|working"
```

### Method 3: Binary Search Recent Commits

```bash
# List last 10 commits
git log --oneline -10

# Checkout and test each commit until you find the last working one
git checkout <commit-hash>
docker compose build cerebro-backend --no-cache
docker compose up -d cerebro-backend
# Test experiment start
# If works, record this hash
```

### Recording the Good Commit

Once you find the last known good commit, **record it immediately**:

```bash
# Get the full commit hash
GOOD_COMMIT=$(git rev-parse HEAD)
echo "Last known good commit: $GOOD_COMMIT" >> CHANGELOG.md
echo "Date: $(date)" >> CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: Record last known good commit $GOOD_COMMIT"
```

## Full Rollback Procedure

### Step 1: Stash Current Work (if needed)

```bash
# Save current uncommitted changes
git stash push -m "WIP before rollback to $GOOD_COMMIT"

# List stashes to verify
git stash list
```

### Step 2: Reset to Good Commit

**Option A: Hard Reset (destructive - use with caution)**
```bash
# WARNING: This discards all commits after the good commit
git reset --hard <good-commit-hash>

# Verify you're on the right commit
git log --oneline -5
```

**Option B: Checkout Good Commit (safer - creates detached HEAD)**
```bash
# Checkout without modifying current branch
git checkout <good-commit-hash>

# Create a new branch from this point (optional)
git checkout -b rollback-$(date +%Y%m%d)
```

### Step 3: Clean Build Artifacts

```bash
# Remove Docker containers and volumes
docker compose down

# Remove built images
docker rmi cerebro-red-v2:latest 2>/dev/null || true

# Clear Python cache
find backend -name "*.pyc" -delete
find backend -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null || true
```

### Step 4: Rebuild and Restart

```bash
# Rebuild from scratch
docker compose build cerebro-backend --no-cache

# Start services
docker compose up -d cerebro-backend

# Wait for startup
sleep 15
```

### Step 5: Verify Health

```bash
# Health check
curl http://localhost:9000/health | python3 -m json.tool

# Check logs
docker compose logs cerebro-backend --tail=50 | grep -E "started|Uvicorn|ERROR"
```

## Selective File Rollback

If only specific files are problematic, rollback individual files:

### Rollback Critical Files

```bash
# Rollback scans.py
git checkout <good-commit-hash> -- backend/api/scans.py

# Rollback orchestrator.py
git checkout <good-commit-hash> -- backend/core/orchestrator.py

# Verify changes
git diff backend/api/scans.py
git diff backend/core/orchestrator.py
```

### Common Files to Rollback

```bash
# Core experiment execution
git checkout <good-commit-hash> -- backend/api/scans.py
git checkout <good-commit-hash> -- backend/core/orchestrator.py

# Experiment management
git checkout <good-commit-hash> -- backend/api/experiments.py

# Database/Repository layer
git checkout <good-commit-hash> -- backend/core/database.py

# Configuration
git checkout <good-commit-hash> -- backend/main.py
```

### Restart After Selective Rollback

```bash
# Restart backend (no rebuild needed if only Python files changed)
docker compose restart cerebro-backend
sleep 10

# Or rebuild if unsure
docker compose build cerebro-backend
docker compose up -d cerebro-backend
```

## Git Revert Flow

If you want to keep commit history but undo changes:

### Revert Single Commit

```bash
# Revert the most recent commit
git revert HEAD

# Revert specific commit
git revert <commit-hash>

# Resolve conflicts if any
git status
# Edit conflicted files
git add <resolved-files>
git commit
```

### Revert Multiple Commits

```bash
# Revert last 3 commits (creates 3 new revert commits)
git revert --no-commit HEAD~3..HEAD
git commit -m "Revert last 3 commits"
```

### Revert Range of Commits

```bash
# Revert commits from <bad-commit> to HEAD
git revert --no-commit <bad-commit>^..HEAD
git commit -m "Revert commits from <bad-commit> to HEAD"
```

## Rebuild and Restart

After any rollback operation:

### Full Rebuild (Recommended)

```bash
# Stop services
docker compose down

# Remove old images
docker rmi cerebro-red-v2:latest 2>/dev/null || true

# Rebuild without cache
docker compose build cerebro-backend --no-cache

# Start services
docker compose up -d cerebro-backend

# Wait for startup
sleep 15
```

### Quick Restart (If only Python files changed)

```bash
# Just restart (uses existing image)
docker compose restart cerebro-backend
sleep 10
```

## Verification Steps

### 1. Health Check

```bash
curl http://localhost:9000/health | python3 -m json.tool
# Expected: {"status": "healthy", "service": "cerebro-red-v2", ...}
```

### 2. Check for run_experiment Execution

```bash
# Start a test experiment (see Minimal Experiment Sanity Test below)
# Then check logs for execution
docker compose logs cerebro-backend --tail=200 | grep -E "run_experiment|DIAG|WRAPPER"
# Should show: [DIAG] ========== run_experiment CALLED for ...
```

### 3. Verify BackgroundTasks Pattern

```bash
# Check that scans.py uses BackgroundTasks
grep -A 3 "background_tasks.add_task" backend/api/scans.py
# Should show: background_tasks.add_task(_run_experiment_with_error_handling, ...)

# Verify no asyncio.create_task (except in batch concurrent execution)
grep -n "asyncio.create_task" backend/api/scans.py backend/api/experiments.py
# Should only appear in _run_batch_experiments_concurrently or be absent
```

### 4. Check Log Output

```bash
# Monitor logs for 30 seconds
timeout 30 docker compose logs -f cerebro-backend | grep -E "DIAG|ERROR|Exception"
```

## Minimal Experiment Sanity Test

After rollback, run this minimal test to verify basic functionality:

```bash
# Create minimal experiment
curl -X POST http://localhost:9000/api/scan/start \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "experiment_config": {
      "experiment_id": "00000000-0000-0000-0000-000000000001",
      "name": "Rollback Sanity Test",
      "description": "Minimal test after rollback",
      "target_model_provider": "ollama",
      "target_model_name": "qwen2.5:3b",
      "attacker_model_provider": "ollama",
      "attacker_model_name": "qwen3:8b",
      "judge_model_provider": "ollama",
      "judge_model_name": "qwen3:8b",
      "initial_prompts": ["Test prompt for rollback verification"],
      "strategies": ["jailbreak_dan"],
      "max_iterations": 1,
      "max_concurrent_attacks": 1,
      "success_threshold": 7.0,
      "timeout_seconds": 60
    }
  }' | python3 -m json.tool

# Get experiment ID from response, then check status
EXPERIMENT_ID="<from-response>"

# Wait 5 seconds
sleep 5

# Check experiment status
curl http://localhost:9000/api/scan/status/$EXPERIMENT_ID \
  -H "X-API-Key: test-api-key" | python3 -m json.tool

# Check logs for execution
docker compose logs cerebro-backend --tail=100 | grep -E "$EXPERIMENT_ID|run_experiment|DIAG"
```

**Success Criteria:**
- ✅ Experiment created with status `pending` or `running`
- ✅ Logs show `[DIAG] run_experiment CALLED for $EXPERIMENT_ID`
- ✅ Logs show `[DIAG-WRAPPER]` or `[DIAG-START]` entries
- ✅ Experiment progresses (status changes or iterations appear)

## Volume Mount Sanity Check

If using live code reload, verify volume mount is working:

```bash
# Check if volume is mounted
docker compose exec cerebro-backend ls -la /app/main.py

# Verify file content matches host
docker compose exec cerebro-backend head -5 /app/main.py
head -5 backend/main.py
# Should match

# Check file modification times
docker compose exec cerebro-backend stat /app/main.py
stat backend/main.py
# Should be similar (within seconds)

# Test file write (if needed)
echo "# Test" >> backend/test_volume.txt
docker compose exec cerebro-backend cat /app/test_volume.txt
# Should show: # Test
rm backend/test_volume.txt
```

**If volume mount fails:**
- Check `docker-compose.yml` for volume configuration
- Verify Docker file sharing settings (Docker Desktop)
- Rebuild image: `docker compose build cerebro-backend --no-cache`

## Stashing Work in Progress

Before rollback, save any uncommitted work:

### Stash Current Changes

```bash
# Stash all changes (including untracked files)
git stash push -u -m "WIP before rollback - $(date +%Y%m%d-%H%M%S)"

# List stashes
git stash list

# View stash contents
git stash show -p stash@{0}
```

### Apply Stash After Rollback (if needed)

```bash
# List stashes
git stash list

# Apply most recent stash
git stash pop

# Or apply specific stash
git stash apply stash@{0}

# Drop stash after applying (if using pop, this is automatic)
git stash drop stash@{0}
```

### Create Backup Branch

```bash
# Create branch from current state before rollback
git checkout -b backup-before-rollback-$(date +%Y%m%d)

# Commit current state
git add -A
git commit -m "Backup before rollback to $GOOD_COMMIT"

# Return to main branch
git checkout main  # or your working branch
```

## Quick Reference

### One-Liner Full Rollback

```bash
GOOD_COMMIT="<commit-hash>" && \
git stash push -u -m "WIP before rollback" && \
git reset --hard $GOOD_COMMIT && \
docker compose down && \
docker compose build cerebro-backend --no-cache && \
docker compose up -d cerebro-backend && \
sleep 15 && \
curl http://localhost:9000/health
```

### One-Liner Selective Rollback

```bash
GOOD_COMMIT="<commit-hash>" && \
git checkout $GOOD_COMMIT -- backend/api/scans.py backend/core/orchestrator.py && \
docker compose restart cerebro-backend && \
sleep 10 && \
curl http://localhost:9000/health
```

## Notes

- **Always record the good commit hash** in CHANGELOG.md before rollback
- **Test immediately after rollback** with minimal experiment
- **Keep stashes** until you're confident the rollback worked
- **Document what broke** so it can be fixed properly later
- **Consider creating a branch** from the good commit for parallel investigation

## Related Documentation

- `README.md` - Quick Restart Checklist and BackgroundTasks troubleshooting
- `TASK_DIAGNOSIS.md` - Diagnostic procedures for experiment failures
- `INTEGRATION_TEST_RESULTS.md` - Test results and verification procedures
