#!/usr/bin/env bash
# ============================================================================
# Secrets Validation Script for Cerebro-Red v2
# ============================================================================
# Scans repository for accidentally committed secrets and sensitive data
# Usage: ./scripts/validate_secrets.sh
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
SECRETS_FOUND=0
GITIGNORE_ISSUES=0

# Get repository root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Print header
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Cerebro-Red v2 - Secrets Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Files to exclude from scanning
EXCLUDE_PATTERNS=(
    ".env.example"
    ".env.railway"
    "*.md"
    "*.txt"
    "*/docs/*"
    "*/node_modules/*"
    "*/venv/*"
    "*/.git/*"
    "*/dist/*"
    "*/build/*"
    "*.min.js"
)

# Build exclude arguments for grep
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$pattern"
done

# Secret patterns to search for
declare -A SECRET_PATTERNS=(
    ["API Keys"]="(sk-[A-Za-z0-9]{32,}|api[_-]?key[=:]['\"]?[A-Za-z0-9]{20,}|apikey[=:]['\"]?[A-Za-z0-9]{20,})"
    ["AWS Credentials"]="(AKIA[0-9A-Z]{16}|aws[_-]?access[_-]?key[_-]?id[=:]['\"]?[A-Za-z0-9]{16,})"
    ["Private Keys"]="(BEGIN (RSA |DSA |EC )?PRIVATE KEY)"
    ["Passwords"]="(password[=:]['\"]?[^\s'\"\n]{8,}|passwd[=:]['\"]?[^\s'\"\n]{8,})"
    ["Tokens"]="(token[=:]['\"]?[A-Za-z0-9_-]{20,}|bearer[=:]['\"]?[A-Za-z0-9_-]{20,})"
    ["JWT Tokens"]="(eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.)"
    ["Database URLs with Credentials"]="(postgresql://[^:]+:[^@]+@|mysql://[^:]+:[^@]+@|mongodb://[^:]+:[^@]+@)"
    ["Azure Keys"]="(azure[_-]?key[=:]['\"]?[A-Za-z0-9/+]{40,})"
    ["OpenAI Keys"]="(sk-[A-Za-z0-9]{48})"
)

echo -e "${BLUE}Scanning for secrets in repository...${NC}"
echo ""

# Scan for each secret pattern
for pattern_name in "${!SECRET_PATTERNS[@]}"; do
    pattern="${SECRET_PATTERNS[$pattern_name]}"

    # Use git grep if in a git repository, otherwise use regular grep
    if git rev-parse --is-inside-work-tree &>/dev/null; then
        results=$(git grep -IEn "$pattern" $EXCLUDE_ARGS 2>/dev/null || true)
    else
        results=$(grep -IrEn "$pattern" . $EXCLUDE_ARGS 2>/dev/null || true)
    fi

    if [ -n "$results" ]; then
        echo -e "${RED} Found potential ${pattern_name}:${NC}"
        echo "$results" | while IFS=: read -r file line content; do
            echo -e "  ${YELLOW}${file}:${line}${NC}"
            # Mask the actual secret in output
            masked_content=$(echo "$content" | sed -E 's/([A-Za-z0-9]{8})[A-Za-z0-9]{10,}/\1***/g')
            echo -e "    ${masked_content}"
        done
        echo ""
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    fi
done

# Check .gitignore for common secret file patterns
echo -e "${BLUE}Checking .gitignore configuration...${NC}"
echo ""

REQUIRED_GITIGNORE_PATTERNS=(
    ".env"
    ".env.local"
    ".env.production"
    "*.key"
    "*.pem"
    "*.p12"
    "*.pfx"
    "secrets/"
    "credentials/"
)

if [ -f ".gitignore" ]; then
    for pattern in "${REQUIRED_GITIGNORE_PATTERNS[@]}"; do
        if ! grep -q "^${pattern}$" .gitignore 2>/dev/null; then
            echo -e "${YELLOW} Missing .gitignore pattern: ${pattern}${NC}"
            GITIGNORE_ISSUES=$((GITIGNORE_ISSUES + 1))
        fi
    done

    if [ $GITIGNORE_ISSUES -eq 0 ]; then
        echo -e "${GREEN} .gitignore includes common secret patterns${NC}"
    fi
else
    echo -e "${RED} .gitignore not found${NC}"
    GITIGNORE_ISSUES=$((GITIGNORE_ISSUES + 1))
fi

echo ""

# Check for actual .env files that might be committed
echo -e "${BLUE}Checking for committed environment files...${NC}"
echo ""

ENV_FILES_FOUND=0
if git rev-parse --is-inside-work-tree &>/dev/null; then
    env_files=$(git ls-files | grep -E "^\.env$|^\.env\.local$|^\.env\.production$" || true)
    if [ -n "$env_files" ]; then
        echo -e "${RED} Found committed environment files:${NC}"
        echo "$env_files" | while read -r file; do
            echo -e "  ${YELLOW}${file}${NC}"
            ENV_FILES_FOUND=$((ENV_FILES_FOUND + 1))
        done
        echo ""
        echo -e "${YELLOW}Recommendation: Remove these files and add to .gitignore${NC}"
        echo ""
        SECRETS_FOUND=$((SECRETS_FOUND + ENV_FILES_FOUND))
    else
        echo -e "${GREEN} No environment files committed${NC}"
        echo ""
    fi
fi

# Summary and remediation
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Validation Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ $SECRETS_FOUND -eq 0 ] && [ $GITIGNORE_ISSUES -eq 0 ]; then
    echo -e "${GREEN} No secrets detected!${NC}"
    echo ""
    echo "Your repository appears to be free of accidentally committed secrets."
    echo ""
    exit 0
else
    if [ $SECRETS_FOUND -gt 0 ]; then
        echo -e "${RED} Found ${SECRETS_FOUND} potential secret(s)${NC}"
        echo ""
        echo -e "${YELLOW}Remediation Steps:${NC}"
        echo ""
        echo "1. Remove secrets from files and replace with environment variables"
        echo "2. Update .gitignore to prevent future commits"
        echo "3. Rotate compromised credentials immediately"
        echo "4. Remove secrets from git history:"
        echo "   git filter-branch --force --index-filter \\"
        echo "     'git rm --cached --ignore-unmatch <file-with-secret>' \\"
        echo "     --prune-empty --tag-name-filter cat -- --all"
        echo ""
        echo "5. Use git-secrets or similar tools for prevention:"
        echo "   https://github.com/awslabs/git-secrets"
        echo ""
    fi

    if [ $GITIGNORE_ISSUES -gt 0 ]; then
        echo -e "${YELLOW} ${GITIGNORE_ISSUES} .gitignore issue(s) found${NC}"
        echo ""
        echo "Add missing patterns to .gitignore:"
        for pattern in "${REQUIRED_GITIGNORE_PATTERNS[@]}"; do
            if ! grep -q "^${pattern}$" .gitignore 2>/dev/null; then
                echo "  ${pattern}"
            fi
        done
        echo ""
    fi

    exit 1
fi
