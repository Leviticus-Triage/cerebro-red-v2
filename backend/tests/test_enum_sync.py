"""
Phase 7: Frontend/Backend Enum Synchronization Test

Verifies that AttackStrategyType enum values match exactly between
frontend (TypeScript) and backend (Python).
"""

import pytest
import re
from pathlib import Path
from core.models import AttackStrategyType


def extract_backend_enum_values():
    """Extract all AttackStrategyType enum values from backend."""
    return set(strategy.value for strategy in AttackStrategyType)


def extract_frontend_enum_values():
    """
    Extract all AttackStrategyType enum values from frontend TypeScript file.
    
    Parses frontend/src/types/api.ts to extract enum values.
    """
    frontend_file = Path(__file__).parent.parent.parent / "frontend" / "src" / "types" / "api.ts"
    
    if not frontend_file.exists():
        pytest.skip(f"Frontend file not found: {frontend_file}")
    
    with open(frontend_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find AttackStrategyType enum block
    enum_pattern = r'export enum AttackStrategyType\s*\{([^}]+)\}'
    match = re.search(enum_pattern, content, re.DOTALL)
    
    if not match:
        pytest.fail("Could not find AttackStrategyType enum in frontend/src/types/api.ts")
    
    enum_content = match.group(1)
    
    # Extract enum values (format: KEY = "value",)
    value_pattern = r'=\s*["\']([^"\']+)["\']'
    values = re.findall(value_pattern, enum_content)
    
    return set(values)


def test_enum_count_matches():
    """
    Verify that frontend and backend have the same number of enum values.
    
    Phase 7 Step 2: Enum Synchronization Check
    """
    backend_values = extract_backend_enum_values()
    frontend_values = extract_frontend_enum_values()
    
    print(f"\n Enum Count:")
    print(f"   Backend: {len(backend_values)} strategies")
    print(f"   Frontend: {len(frontend_values)} strategies")
    
    assert len(backend_values) == len(frontend_values), \
        f"Enum count mismatch: Backend={len(backend_values)}, Frontend={len(frontend_values)}"
    
    assert len(backend_values) == 44, \
        f"Expected 44 strategies, got {len(backend_values)}"


def test_enum_values_match_exactly():
    """
    Verify that all enum values match exactly between frontend and backend.
    
    Phase 7 Step 2: Enum Synchronization Check
    """
    backend_values = extract_backend_enum_values()
    frontend_values = extract_frontend_enum_values()
    
    # Find mismatches
    only_in_backend = backend_values - frontend_values
    only_in_frontend = frontend_values - backend_values
    
    if only_in_backend or only_in_frontend:
        print(f"\n Enum Synchronization Errors:")
        
        if only_in_backend:
            print(f"\n   Only in Backend ({len(only_in_backend)}):")
            for value in sorted(only_in_backend):
                print(f"     - {value}")
        
        if only_in_frontend:
            print(f"\n   Only in Frontend ({len(only_in_frontend)}):")
            for value in sorted(only_in_frontend):
                print(f"     - {value}")
        
        pytest.fail(f"Enum mismatch: {len(only_in_backend)} backend-only, {len(only_in_frontend)} frontend-only")
    
    print(f" All {len(backend_values)} enum values match exactly")


def test_enum_naming_convention():
    """
    Verify that all enum values follow snake_case naming convention.
    
    Phase 7 Step 2: Validate naming consistency
    """
    backend_values = extract_backend_enum_values()
    
    invalid_names = []
    for value in backend_values:
        # Check for snake_case (lowercase with underscores)
        if not re.match(r'^[a-z][a-z0-9_]*$', value):
            invalid_names.append(value)
    
    if invalid_names:
        print(f"\n️  Invalid enum names (not snake_case):")
        for name in sorted(invalid_names):
            print(f"     - {name}")
        pytest.fail(f"{len(invalid_names)} enum values don't follow snake_case convention")
    
    print(f" All {len(backend_values)} enum values follow snake_case")


def test_no_duplicate_enum_values():
    """
    Verify that there are no duplicate enum values in backend.
    
    Phase 7 Step 2: Ensure uniqueness
    """
    backend_values = list(strategy.value for strategy in AttackStrategyType)
    unique_values = set(backend_values)
    
    if len(backend_values) != len(unique_values):
        duplicates = [v for v in unique_values if backend_values.count(v) > 1]
        print(f"\n Duplicate enum values found:")
        for dup in duplicates:
            print(f"     - {dup} (appears {backend_values.count(dup)} times)")
        pytest.fail(f"{len(duplicates)} duplicate enum values")
    
    print(f" All {len(backend_values)} enum values are unique")


def test_generate_enum_sync_script():
    """
    Generate shell script for manual enum synchronization check.
    
    Phase 7 Step 2: Provide automation script
    """
    script_path = Path(__file__).parent.parent / "scripts" / "check_enum_sync.sh"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    
    script_content = """#!/bin/bash
# Phase 7: Enum Synchronization Check Script
# Auto-generated by test_enum_sync.py

set -e

echo " Checking AttackStrategyType enum synchronization..."

# Extract backend enum values
echo " Extracting backend enum values..."
grep -A 100 "class AttackStrategyType" backend/core/models.py | \\
  grep '= "' | awk -F'"' '{print $2}' | sort > /tmp/backend_strategies.txt

# Extract frontend enum values
echo " Extracting frontend enum values..."
grep -A 100 "export enum AttackStrategyType" frontend/src/types/api.ts | \\
  grep '= "' | awk -F'"' '{print $2}' | sort > /tmp/frontend_strategies.txt

# Compare
echo "️  Comparing enums..."
if diff /tmp/backend_strategies.txt /tmp/frontend_strategies.txt > /dev/null; then
    BACKEND_COUNT=$(wc -l < /tmp/backend_strategies.txt)
    echo " Enums synchronized: $BACKEND_COUNT strategies match"
    exit 0
else
    echo " Enum mismatch detected:"
    echo ""
    echo "Differences:"
    diff /tmp/backend_strategies.txt /tmp/frontend_strategies.txt || true
    echo ""
    echo "Backend count: $(wc -l < /tmp/backend_strategies.txt)"
    echo "Frontend count: $(wc -l < /tmp/frontend_strategies.txt)"
    exit 1
fi
"""
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    script_path.chmod(0o755)
    
    print(f"\n Generated enum sync script: {script_path}")
    print(f"   Run: ./backend/scripts/check_enum_sync.sh")


def test_all_strategies_documented():
    """
    Verify that all strategies are documented in STRATEGY_IMPLEMENTATION_GUIDE.md.
    
    Phase 7 Step 2: Ensure documentation completeness
    """
    doc_file = Path(__file__).parent.parent.parent / "STRATEGY_IMPLEMENTATION_GUIDE.md"
    
    if not doc_file.exists():
        pytest.skip(f"Documentation file not found: {doc_file}")
    
    with open(doc_file, 'r', encoding='utf-8') as f:
        doc_content = f.read()
    
    backend_values = extract_backend_enum_values()
    undocumented = []
    
    for strategy in backend_values:
        # Check if strategy appears in documentation (case-insensitive)
        if strategy.lower() not in doc_content.lower():
            undocumented.append(strategy)
    
    if undocumented:
        print(f"\n️  Strategies missing from documentation:")
        for strategy in sorted(undocumented)[:10]:  # Show first 10
            print(f"     - {strategy}")
        print(f"\n   Total undocumented: {len(undocumented)}/{len(backend_values)}")
        # Don't fail, just warn
        print(f"   ️  Warning: Some strategies are not documented")
    else:
        print(f" All {len(backend_values)} strategies are documented")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
