#!/bin/bash
# Script to validate .gitignore effectiveness
# Tests common sensitive file patterns

set -e

echo "Testing .gitignore patterns..."
echo ""

# Test patterns
test_files=(
    ".env.backup"
    "test.key"
    "test.pem"
    "backend/data/test.backup"
    "test.tmp"
    "backups/test.txt"
    "test-results/dummy.txt"
    "playwright-report/index.html"
    "recordings/test.webm"
)

passed=0
failed=0

for file in "${test_files[@]}"; do
    # Create directory if needed (skip if empty)
    dir=$(dirname "$file")
    if [ "$dir" != "." ]; then
        mkdir -p "$dir" 2>/dev/null || true
    fi
    
    # Create test file
    touch "$file" 2>/dev/null || true
    
    # Check if ignored
    if git check-ignore -q "$file" 2>/dev/null; then
        echo "✓ $file is ignored"
        passed=$((passed + 1))
    else
        echo "✗ $file is NOT ignored"
        failed=$((failed + 1))
    fi
    
    # Clean up
    rm -f "$file" 2>/dev/null || true
    if [ "$dir" != "." ] && [ -d "$dir" ]; then
        rmdir "$dir" 2>/dev/null || true
    fi
done

echo ""
echo "Results: $passed passed, $failed failed"

if [ $failed -eq 0 ]; then
    echo "✓ All patterns working correctly"
    exit 0
else
    echo "✗ Some patterns need attention"
    exit 1
fi
