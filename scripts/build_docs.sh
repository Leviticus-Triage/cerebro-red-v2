#!/bin/bash
# Build API documentation pipeline
#
# This script:
# 1. Exports OpenAPI schema
# 2. Generates API documentation
# 3. Validates documentation integrity
#
# Usage: ./scripts/build_docs.sh

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Try to find and use venv Python
VENV_PYTHON=""
if [ -f "$PROJECT_ROOT/../venv/bin/python3" ]; then
    VENV_PYTHON="$PROJECT_ROOT/../venv/bin/python3"
elif [ -f "$PROJECT_ROOT/venv/bin/python3" ]; then
    VENV_PYTHON="$PROJECT_ROOT/venv/bin/python3"
elif [ -n "$VIRTUAL_ENV" ] && [ -f "$VIRTUAL_ENV/bin/python3" ]; then
    VENV_PYTHON="$VIRTUAL_ENV/bin/python3"
fi

# Use venv Python if available, otherwise use system python3
if [ -n "$VENV_PYTHON" ]; then
    PYTHON_CMD="$VENV_PYTHON"
    echo " Using venv Python: $PYTHON_CMD"
else
    PYTHON_CMD="python3"
    echo "  Using system Python (consider activating venv first)"
    echo "   To activate venv: source ../venv/bin/activate"
fi
echo ""

echo " Building API documentation..."
echo ""

# Step 1: Export OpenAPI schema
echo "1⃣  Exporting OpenAPI schema..."
cd "$BACKEND_DIR"
$PYTHON_CMD export_openapi.py || {
    echo " Failed to export OpenAPI schema"
    echo "   Hint: Make sure FastAPI is installed: pip install fastapi uvicorn"
    exit 1
}
echo ""

# Step 2: Generate API documentation
echo "2⃣  Generating API documentation..."
$PYTHON_CMD scripts/generate_api_docs.py || {
    echo " Failed to generate API documentation"
    exit 1
}
echo ""

# Step 3: Validate documentation
echo "3⃣  Validating documentation..."
cd "$PROJECT_ROOT"
$PYTHON_CMD scripts/validate_docs.py || {
    echo " Documentation validation failed"
    echo "   Note: This is expected if docs have uncommitted changes"
    exit 1
}
echo ""

echo " Documentation build complete!"
echo ""
echo "Generated files:"
echo "  - docs/openapi.json"
echo "  - docs/en/api-reference.md"
echo "  - docs/de/api-referenz.md (if exists)"
