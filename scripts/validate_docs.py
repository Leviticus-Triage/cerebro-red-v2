#!/usr/bin/env python3
"""
Validate API documentation integrity.

This script:
1. Regenerates OpenAPI schema
2. Regenerates API documentation
3. Checks for changes (git diff)
4. Validates links and structure
5. Checks German translation parity
"""

import subprocess
import sys
from pathlib import Path
import json
import re


def run_command(cmd: list, cwd: Path = None) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def check_git_diff(file_path: Path) -> bool:
    """Check if file has uncommitted changes."""
    code, stdout, _ = run_command(['git', 'diff', '--exit-code', str(file_path)])
    return code != 0  # True if there are changes


def validate_openapi_schema(schema_path: Path) -> list[str]:
    """Validate OpenAPI schema structure."""
    errors = []
    
    if not schema_path.exists():
        errors.append(f"OpenAPI schema not found: {schema_path}")
        return errors
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # Check required top-level fields
    required_fields = ['openapi', 'info', 'paths']
    for field in required_fields:
        if field not in schema:
            errors.append(f"Missing required field in schema: {field}")
    
    # Check paths start with /api/v1
    paths = schema.get('paths', {})
    allowed_paths = ['/health', '/', '/docs', '/redoc', '/metrics']
    invalid_paths = [
        p for p in paths.keys() 
        if not p.startswith('/api/v1/') 
        and not p.startswith('/ws/') 
        and not p.startswith('/health/')  # Allow /health/* subpaths
        and p not in allowed_paths
        and not p.startswith('/{')  # Allow catch-all routes like /{path}
    ]
    if invalid_paths:
        errors.append(f"Paths not using /api/v1/ prefix: {invalid_paths[:5]}")
    
    # Check info section
    info = schema.get('info', {})
    if 'version' not in info:
        errors.append("Missing 'version' in info section")
    if 'title' not in info:
        errors.append("Missing 'title' in info section")
    
    # Check servers
    servers = schema.get('servers', [])
    if not servers:
        errors.append("Missing 'servers' in schema")
    
    return errors


def validate_markdown_links(doc_path: Path) -> list[str]:
    """Validate internal links in Markdown documentation."""
    errors = []
    
    if not doc_path.exists():
        errors.append(f"Documentation file not found: {doc_path}")
        return errors
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all markdown links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)
    
    doc_dir = doc_path.parent
    
    for link_text, link_url in links:
        # Skip external links
        if link_url.startswith('http://') or link_url.startswith('https://'):
            continue
        
        # Skip anchor links
        if link_url.startswith('#'):
            continue
        
        # Resolve relative paths
        if link_url.startswith('./') or not link_url.startswith('/'):
            target_path = (doc_dir / link_url).resolve()
        else:
            target_path = (doc_path.parent.parent / link_url.lstrip('/')).resolve()
        
        if not target_path.exists():
            errors.append(f"Broken link: [{link_text}]({link_url}) -> {target_path}")
    
    return errors


def check_german_parity(en_path: Path, de_path: Path) -> list[str]:
    """Check if German translation has same structure as English."""
    errors = []
    
    if not en_path.exists():
        errors.append(f"English documentation not found: {en_path}")
        return errors
    
    if not de_path.exists():
        errors.append(f"German documentation not found: {de_path}")
        return errors
    
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read()
    
    with open(de_path, 'r', encoding='utf-8') as f:
        de_content = f.read()
    
    # Extract headers from both
    en_headers = re.findall(r'^##+\s+(.+)$', en_content, re.MULTILINE)
    de_headers = re.findall(r'^##+\s+(.+)$', de_content, re.MULTILINE)
    
    # Check header count (should be similar)
    if abs(len(en_headers) - len(de_headers)) > 5:
        errors.append(f"Header count mismatch: EN has {len(en_headers)}, DE has {len(de_headers)}")
    
    return errors


def main():
    """Main validation entry point."""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    docs_dir = project_root / "docs"
    
    errors = []
    warnings = []
    
    print(" Validating API documentation...")
    print()
    
    # Try to find venv Python
    import sys
    venv_python = sys.executable  # Use current Python (might be venv)
    
    # Step 1: Regenerate OpenAPI schema
    print("1⃣  Regenerating OpenAPI schema...")
    code, stdout, stderr = run_command(
        [venv_python, 'export_openapi.py'],
        cwd=backend_dir
    )
    if code != 0:
        errors.append(f"Failed to export OpenAPI schema: {stderr}")
    else:
        print("    OpenAPI schema regenerated")
    
    # Step 2: Regenerate API documentation
    print("2⃣  Regenerating API documentation...")
    code, stdout, stderr = run_command(
        [venv_python, 'scripts/generate_api_docs.py'],
        cwd=backend_dir
    )
    if code != 0:
        errors.append(f"Failed to generate API docs: {stderr}")
    else:
        print("    API documentation regenerated")
    
    # Step 3: Check for uncommitted changes
    print("3⃣  Checking for uncommitted changes...")
    api_ref_path = docs_dir / "en" / "api-reference.md"
    if check_git_diff(api_ref_path):
        errors.append(f"Uncommitted changes detected in {api_ref_path}. Run 'git diff' to see changes.")
    else:
        print("    No uncommitted changes")
    
    # Step 4: Validate OpenAPI schema
    print("4⃣  Validating OpenAPI schema...")
    schema_path = docs_dir / "openapi.json"
    schema_errors = validate_openapi_schema(schema_path)
    if schema_errors:
        errors.extend(schema_errors)
    else:
        print("    OpenAPI schema is valid")
    
    # Step 5: Validate Markdown links
    print("5⃣  Validating Markdown links...")
    link_errors = validate_markdown_links(api_ref_path)
    if link_errors:
        warnings.extend(link_errors[:10])  # Limit warnings
    else:
        print("    All links are valid")
    
    # Step 6: Check German translation parity
    print("6⃣  Checking German translation parity...")
    de_path = docs_dir / "de" / "api-referenz.md"
    parity_errors = check_german_parity(api_ref_path, de_path)
    if parity_errors:
        warnings.extend(parity_errors)
    else:
        print("    German translation structure matches")
    
    # Report results
    print()
    if errors:
        print(" Validation failed with errors:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    if warnings:
        print("  Validation completed with warnings:")
        for warning in warnings[:10]:
            print(f"   - {warning}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more warnings")
    
    print(" All validations passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
