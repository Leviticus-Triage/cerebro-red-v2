# Building API Documentation

## Quick Start

### Option 1: Using the Build Script (Recommended)

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2
./scripts/build_docs.sh
```

The script will automatically:
1. Detect and use venv Python if available
2. Export OpenAPI schema
3. Generate API documentation
4. Validate documentation

### Option 2: Manual Steps

**1. Activate Virtual Environment:**

```bash
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate
```

**2. Export OpenAPI Schema:**

```bash
cd cerebro-red-v2/backend
python3 export_openapi.py
```

**3. Generate API Documentation:**

```bash
python3 scripts/generate_api_docs.py
```

**4. Validate Documentation:**

```bash
cd ..
python3 scripts/validate_docs.py
```

## Troubleshooting

### ModuleNotFoundError: No module named 'fastapi'

**Solution:** Install dependencies in venv:

```bash
source /mnt/nvme0n1p5/danii/hexstrike-ai-kit/venv/bin/activate
cd cerebro-red-v2/backend
pip install -r requirements.txt
```

### Path Errors

Make sure you're running scripts from the correct directory:
- `build_docs.sh` should be run from `cerebro-red-v2/` directory
- `export_openapi.py` should be run from `cerebro-red-v2/backend/` directory

## CI/CD

The documentation is automatically validated in CI when:
- Files in `docs/` are changed
- Files in `backend/api/` are changed
- `backend/main.py` or export/generate scripts are changed

See `.github/workflows/docs-validation.yml` for details.
