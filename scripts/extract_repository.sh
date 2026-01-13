#!/bin/bash
set -e

echo "=== CEREBRO-RED v2 Repository Extraction Script ==="
echo "This script creates a new repository from cerebro-red-v2/ directory"
echo ""

# Configuration
ORIGINAL_REPO="hexstrike-ai-kit"
SUBDIRECTORY="cerebro-red-v2"
NEW_REPO_NAME="cerebro-red-v2"
GITHUB_ORG="Leviticus-Triage"
SOURCE_DIR="/mnt/nvme0n1p5/danii/${ORIGINAL_REPO}/${SUBDIRECTORY}"
OUTPUT_DIR="/tmp/${NEW_REPO_NAME}-extraction"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Validation function
validate_step() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN} $1${NC}"
    else
        echo -e "${RED} $1 FAILED${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}Step 1: Preparing output directory...${NC}"
rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"
cd "${OUTPUT_DIR}"
validate_step "Output directory prepared"

echo -e "${YELLOW}Step 2: Initializing new git repository...${NC}"
git init
git branch -M main
validate_step "Git repository initialized"

echo -e "${YELLOW}Step 3: Copying files from ${SUBDIRECTORY}/...${NC}"
# Copy all files except .git directory and third-party directories
rsync -av \
    --exclude='.git' \
    --exclude='llamator' \
    --exclude='PyRIT' \
    --exclude='Model-Inversion-Attack-ToolBox' \
    --exclude='L1B3RT4S' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='dist' \
    --exclude='build' \
    "${SOURCE_DIR}/" .
validate_step "Files copied"

echo -e "${YELLOW}Step 4: Removing third-party directories if they exist...${NC}"
# Remove any third-party directories that might have been copied
for dir in llamator PyRIT Model-Inversion-Attack-ToolBox L1B3RT4S; do
    if [ -d "${dir}" ]; then
        rm -rf "${dir}"
        echo "Removed ${dir}/"
    fi
done
validate_step "Third-party directories removed"

echo -e "${YELLOW}Step 5: Creating initial commit...${NC}"
git add .
git commit -m "Initial commit: CEREBRO-RED v2 - Advanced Red Team Research Platform

- PAIR algorithm implementation
- LLM-as-a-Judge evaluation system
- FastAPI backend with WebSocket support
- React frontend with real-time monitoring
- Docker containerization
- Comprehensive documentation

Extracted from hexstrike-ai-kit repository"
validate_step "Initial commit created"

echo -e "${YELLOW}Step 6: Validating extraction...${NC}"
COMMIT_COUNT=$(git rev-list --all --count)
echo "Commit count: ${COMMIT_COUNT}"

# Check that third-party directories are gone
if [ -d "llamator" ] || [ -d "PyRIT" ] || [ -d "Model-Inversion-Attack-ToolBox" ] || [ -d "L1B3RT4S" ]; then
    echo -e "${RED} Third-party directories still exist!${NC}"
    exit 1
fi
validate_step "Third-party directories removed from working tree"

# Check expected directories exist
if [ ! -d "backend" ] || [ ! -d "frontend" ] || [ ! -d "docker" ]; then
    echo -e "${RED} Expected directories missing!${NC}"
    echo "Current directories:"
    ls -la
    exit 1
fi
validate_step "Expected directories present"

# Verify git status is clean
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW} Working tree has uncommitted changes:${NC}"
    git status --short
    # This is OK for initial commit, just warn
else
    validate_step "Working tree is clean"
fi

echo ""
echo -e "${GREEN}=== Extraction Complete ===${NC}"
echo "Location: ${OUTPUT_DIR}"
echo "Commits: ${COMMIT_COUNT}"
echo ""
echo "Next steps:"
echo "1. Review the extracted repository: cd ${OUTPUT_DIR}"
echo "2. Create GitHub repository: gh repo create ${GITHUB_ORG}/${NEW_REPO_NAME} --public"
echo "3. Push to GitHub: git remote add origin git@github.com:${GITHUB_ORG}/${NEW_REPO_NAME}.git && git push -u origin main"
