#!/usr/bin/env bash
#
# build_docs.sh
# =============
#
# Build and validate documentation for CEREBRO-RED v2
#
# This script:
# 1. Exports OpenAPI schema
# 2. Generates API documentation
# 3. Validates documentation integrity
# 4. Reports any issues
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "CEREBRO-RED v2 Documentation Builder"
echo "========================================"
echo

cd "$REPO_ROOT"

# Step 1: Export OpenAPI Schema
echo -e "${GREEN}Step 1: Exporting OpenAPI schema${NC}"
if [ -f "backend/export_openapi.py" ]; then
    python3 backend/export_openapi.py
    echo "  ✓ OpenAPI schema exported"
else
    echo -e "  ${YELLOW}⚠ backend/export_openapi.py not found, skipping${NC}"
fi
echo

# Step 2: Generate API Documentation
echo -e "${GREEN}Step 2: Generating API documentation${NC}"
if [ -f "scripts/generate_api_docs.py" ]; then
    python3 scripts/generate_api_docs.py
    echo "  ✓ API documentation generated"
else
    echo -e "  ${RED}✗ scripts/generate_api_docs.py not found${NC}"
    exit 1
fi
echo

# Step 3: Validate Documentation
echo -e "${GREEN}Step 3: Validating documentation${NC}"
if [ -f "scripts/validate_docs.py" ]; then
    if python3 scripts/validate_docs.py; then
        echo -e "  ${GREEN}✓ Documentation validation passed${NC}"
    else
        echo -e "  ${RED}✗ Documentation validation failed${NC}"
        exit 1
    fi
else
    echo -e "  ${YELLOW}⚠ scripts/validate_docs.py not found, skipping validation${NC}"
fi
echo

# Step 4: Check for git changes
echo -e "${GREEN}Step 4: Checking for uncommitted changes${NC}"
if git diff --quiet docs/; then
    echo "  ✓ Documentation is up to date"
else
    echo -e "  ${YELLOW}⚠ Documentation has uncommitted changes${NC}"
    echo "  Run 'git status' to see changes"
fi
echo

# Summary
echo "========================================"
echo -e "${GREEN}✓ Documentation build complete${NC}"
echo "========================================"
echo
echo "Generated files:"
echo "  - docs/openapi.json"
echo "  - docs/en/api-reference.md"
echo
echo "Next steps:"
echo "  - Review generated documentation"
echo "  - Commit changes if documentation updated"
echo "  - Deploy documentation to production"
