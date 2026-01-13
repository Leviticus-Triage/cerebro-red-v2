# E2E Test Execution Guide

## Backend E2E Tests

### Prerequisites

1. **Activate Virtual Environment:**
   ```bash
   source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
   pip install -r requirements.txt
   pip install pytest pytest-asyncio
   ```

### Running Tests

**Experiment Lifecycle E2E Test:**
```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
pytest tests/e2e/test_experiment_lifecycle.py -v -m e2e
```

**CORS & Auth Tests:**
```bash
pytest tests/test_cors.py -v -m "cors or auth"
```

**All Tests:**
```bash
pytest tests/ -v
```

## Frontend E2E Tests

### Prerequisites

1. **Install Dependencies:**
   ```bash
   cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend
   npm install
   npx playwright install --with-deps
   ```

### Running Tests

**Important:** Use `npm run` NOT `npx run`:

```bash
# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

**Common Error:**
-  `npx run test:e2e` - This will fail with "Cannot find module"
-  `npm run test:e2e` - This is the correct command

## Troubleshooting

### Backend: ModuleNotFoundError for sqlalchemy

**Problem:** Tests fail with `ModuleNotFoundError: No module named 'sqlalchemy'`

**Solution:** Ensure you're using the virtual environment:
```bash
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate
which python3  # Should show venv path
pytest tests/e2e/test_experiment_lifecycle.py -v
```

### Frontend: Cannot find module error

**Problem:** `npx run test:e2e` fails with "Cannot find module"

**Solution:** Use `npm run` instead:
```bash
npm run test:e2e  # Correct
# NOT: npx run test:e2e  # Wrong
```

### Database Session Issues

The E2E tests use in-memory SQLite databases via dependency overrides. If you see database-related errors:

1. Ensure `conftest.py` is properly configured
2. Check that `db_session` fixture is working
3. Verify dependency overrides are set correctly

