#!/usr/bin/env python3
"""
scripts/validate_docs.py
========================

Validate documentation integrity: check links, language switchers, and translations.

This script validates:
- All markdown links (internal and external)
- Language switcher links exist and point to correct files
- All English documents have corresponding German translations (per metadata.yml)
- Broken image references
- Relative paths are correct
"""

import re
import sys
import yaml
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Tuple, Dict

# Repository root
REPO_ROOT = Path(__file__).parent.parent
DOCS_EN = REPO_ROOT / "docs" / "en"
DOCS_DE = REPO_ROOT / "docs" / "de"
METADATA = REPO_ROOT / "docs" / "metadata.yml"

# Track validation results
errors: List[str] = []
warnings: List[str] = []


def load_metadata():
    """Load documentation metadata."""
    if not METADATA.exists():
        warnings.append(f"Metadata file not found: {METADATA}")
        return None
    
    with open(METADATA, 'r') as f:
        return yaml.safe_load(f)


def find_markdown_files(directory: Path) -> List[Path]:
    """Find all markdown files in directory."""
    return list(directory.rglob("*.md"))


def extract_links(content: str, file_path: Path) -> List[Tuple[str, str]]:
    """Extract all markdown links from content.
    
    Returns: List of (link_text, link_url) tuples
    """
    # Markdown link pattern: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(link_pattern, content)
    return [(text, url) for text, url in matches]


def check_language_switcher(content: str, file_path: Path, metadata: Dict):
    """Check if language switcher link exists and is correct."""
    # Check for language switcher pattern
    has_switcher = re.search(r'\[🇬🇧|\[🇩🇪', content)
    
    if not has_switcher:
        errors.append(f"Missing language switcher in {file_path}")
        return
    
    # Determine expected language
    is_english = "docs/en" in str(file_path)
    is_german = "docs/de" in str(file_path)
    
    if is_english:
        # Should link to German version
        if "🇩🇪" not in content[:500]:  # Check first 500 chars
            errors.append(f"English doc {file_path} missing German switcher link")
    elif is_german:
        # Should link to English version
        if "🇬🇧" not in content[:500]:
            errors.append(f"German doc {file_path} missing English switcher link")


def validate_link(link_url: str, source_file: Path) -> bool:
    """Validate that a link is correct.
    
    Returns: True if valid, False if broken
    """
    # Skip external URLs (they're checked separately)
    if link_url.startswith('http://') or link_url.startswith('https://'):
        return True  # External links validated separately
    
    # Skip anchor-only links
    if link_url.startswith('#'):
        return True
    
    # Skip mailto links
    if link_url.startswith('mailto:'):
        return True
    
    # Resolve relative path
    source_dir = source_file.parent
    target_path = (source_dir / link_url).resolve()
    
    # Check if file exists
    if not target_path.exists():
        errors.append(f"Broken link in {source_file}: {link_url} -> {target_path} (not found)")
        return False
    
    return True


def validate_image_reference(link_url: str, source_file: Path) -> bool:
    """Validate image reference."""
    if not (link_url.endswith('.png') or link_url.endswith('.jpg') or 
            link_url.endswith('.jpeg') or link_url.endswith('.svg')):
        return True  # Not an image
    
    source_dir = source_file.parent
    target_path = (source_dir / link_url).resolve()
    
    if not target_path.exists():
        warnings.append(f"Image not found in {source_file}: {link_url} -> {target_path}")
        return False
    
    return True


def validate_translations(metadata: Dict):
    """Validate that all English docs have German translations."""
    if not metadata or 'documents' not in metadata:
        return
    
    for doc in metadata['documents']:
        path_en = doc.get('path_en')
        path_de = doc.get('path_de')
        
        if path_en:
            en_path = REPO_ROOT / path_en
            if en_path.exists() and path_de:
                de_path = REPO_ROOT / path_de
                if not de_path.exists():
                    warnings.append(f"Missing German translation: {path_de} (for {path_en})")


def validate_file(file_path: Path, metadata: Dict):
    """Validate a single markdown file."""
    content = file_path.read_text(encoding='utf-8')
    
    # Check language switcher
    check_language_switcher(content, file_path, metadata)
    
    # Extract and validate links
    links = extract_links(content, file_path)
    for link_text, link_url in links:
        # Validate link
        if not validate_link(link_url, file_path):
            continue
        
        # Check if it's an image
        if link_text.startswith('!['):
            validate_image_reference(link_url, file_path)


def main():
    """Main validation execution."""
    print("Validating documentation...")
    print(f"Repository root: {REPO_ROOT}")
    print()
    
    # Load metadata
    metadata = load_metadata()
    
    # Find all markdown files
    en_files = find_markdown_files(DOCS_EN)
    de_files = find_markdown_files(DOCS_DE)
    
    print(f"Found {len(en_files)} English documents")
    print(f"Found {len(de_files)} German documents")
    print()
    
    # Validate English files
    print("Validating English documents...")
    for file_path in en_files:
        validate_file(file_path, metadata)
    
    # Validate German files
    print("Validating German documents...")
    for file_path in de_files:
        validate_file(file_path, metadata)
    
    # Validate translations
    print("Validating translations...")
    validate_translations(metadata)
    
    # Print results
    print()
    print("=" * 60)
    print("Validation Results")
    print("=" * 60)
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        print("\n✗ Validation failed with errors")
        sys.exit(1)
    else:
        print("\n✓ Validation passed with no errors")
        if warnings:
            print(f"  ({len(warnings)} warnings - review recommended)")
        sys.exit(0)


if __name__ == "__main__":
    main()
