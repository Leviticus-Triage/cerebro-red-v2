#!/usr/bin/env python3
"""
Update README status section with CI metrics.

Extracts version from pyproject.toml, fetches build status and coverage
from CI environment, and updates the README with timestamped metrics.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple


def extract_version_from_pyproject(pyproject_path: Path) -> str:
    """Extract version from pyproject.toml."""
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found: {pyproject_path}")
    
    content = pyproject_path.read_text(encoding='utf-8')
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    
    if not match:
        raise ValueError(f"Version not found in {pyproject_path}")
    
    return match.group(1)


def parse_readme(readme_path: Path) -> Tuple[str, int, int]:
    """Parse README to find Development Status section."""
    if not readme_path.exists():
        raise FileNotFoundError(f"README not found: {readme_path}")
    
    content = readme_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Find "Development Status" section
    section_start = None
    section_end = None
    
    for i, line in enumerate(lines):
        if line.strip() == "##  Development Status":
            section_start = i
            break
    
    if section_start is None:
        raise ValueError("Development Status section not found in README")
    
    # Find end of section (next ## heading or end of file)
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        if lines[i].startswith('## ') and not lines[i].startswith('###'):
            section_end = i
            break
    
    return content, section_start, section_end


def generate_status_section(
    version: str,
    build_status: str,
    coverage: str,
    timestamp: str
) -> str:
    """Generate formatted status section with badges."""
    # Determine badge colors
    build_color = "green" if build_status.lower() == "passing" else "red"
    
    # Coverage color logic
    try:
        coverage_float = float(coverage.replace('%', ''))
        if coverage_float >= 80:
            coverage_color = "green"
        elif coverage_float >= 60:
            coverage_color = "yellow"
        else:
            coverage_color = "red"
        coverage_display = f"{coverage_float:.1f}%"
    except (ValueError, AttributeError):
        coverage_color = "lightgrey"
        coverage_display = str(coverage) if coverage else "N/A"
    
    # Generate badges
    version_badge = f"![Version](https://img.shields.io/badge/Version-{version}-blue)"
    build_badge = f"![Build](https://img.shields.io/badge/Build-{build_status}-{build_color})"
    coverage_badge = f"![Coverage](https://img.shields.io/badge/Coverage-{coverage_display}-{coverage_color})"
    
    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        formatted_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, AttributeError):
        formatted_timestamp = timestamp if timestamp else datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Generate section
    section = f"""##  Project Status

<!-- AUTO-GENERATED: Do not edit this section manually -->
{version_badge}
{build_badge}
{coverage_badge}

**Last Updated:** {formatted_timestamp}

<!-- END AUTO-GENERATED -->

##  Development Status

**Phase 1**:  Project Foundation & Infrastructure
- [x] Project structure
- [x] Requirements & dependencies
- [x] Docker setup
- [x] Environment configuration

**Phase 2**:  Data Models & Database Schema
- [x] SQLAlchemy ORM models
- [x] Alembic migrations
- [x] Performance indexes

**Phase 3**:  Prompt Mutator with PAIR Algorithm
- [x] 8 attack strategies implemented
- [x] PAIR semantic rephrase (core algorithm)
- [x] Mutation history tracking

**Phase 4**:  Security Judge with LLM-as-a-Judge
- [x] 7-criteria evaluation
- [x] Chain-of-Thought reasoning
- [x] Regex fallback patterns

**Phase 5**:  Async Orchestration Engine
- [x] RedTeamOrchestrator implementation
- [x] Batch processing with exponential backoff
- [x] Real-time WebSocket progress
- [x] Circuit breaker pattern

**Phase 6**:  FastAPI REST API
- [x] Complete CRUD operations
- [x] WebSocket streaming
- [x] OpenAPI documentation
- [x] API key authentication

**Phase 7**:  React Frontend
- [x] Modern dashboard UI
- [x] Real-time progress visualization
- [x] Vulnerability analytics
- [x] Export functionality

**Phase 8**:  Research-Grade Quality Review
- [x] Comprehensive test suites
- [x] E2E testing (backend + frontend)
- [x] Benchmark tests
- [x] Documentation complete
"""
    
    return section


def validate_readme_format(content: str) -> bool:
    """Validate README format and structure."""
    errors = []
    
    # Check for required sections
    if "# CEREBRO-RED v2" not in content and "# CEREBRO-RED" not in content:
        errors.append("Missing title section")
    
    if "## " not in content and "Quick Start" not in content.lower():
        errors.append("Missing quickstart section")
    
    if "##  Development Status" not in content:
        errors.append("Missing Development Status section")
    
    # Check markdown structure (basic validation)
    header_count = len(re.findall(r'^##+\s+', content, re.MULTILINE))
    if header_count < 5:
        errors.append(f"Too few sections found ({header_count})")
    
    # Check for balanced markdown
    code_block_count = content.count('```')
    if code_block_count % 2 != 0:
        errors.append("Unbalanced code blocks")
    
    if errors:
        print(" README validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False
    
    return True


def update_readme(
    readme_path: Path,
    new_section: str,
    start_line: int,
    end_line: int,
    dry_run: bool = False
) -> bool:
    """Update README with new status section."""
    content = readme_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Replace section
    new_lines = lines[:start_line] + new_section.split('\n') + lines[end_line:]
    new_content = '\n'.join(new_lines)
    
    # Validate format
    if not validate_readme_format(new_content):
        return False
    
    if dry_run:
        print(" Dry run - would update README:")
        print("=" * 60)
        print('\n'.join(new_section.split('\n')[:20]))
        print("=" * 60)
        return True
    
    # Write updated content
    readme_path.write_text(new_content, encoding='utf-8')
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Update README status section with CI metrics'
    )
    parser.add_argument(
        '--readme-path',
        type=Path,
        default=Path('./README.md'),
        help='Path to README.md (default: ./README.md)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing'
    )
    parser.add_argument(
        '--version',
        type=str,
        help='Version string (default: extract from pyproject.toml)'
    )
    parser.add_argument(
        '--build-status',
        type=str,
        default='passing',
        help='Build status (default: passing)'
    )
    parser.add_argument(
        '--coverage',
        type=str,
        default='N/A',
        help='Test coverage percentage (default: N/A)'
    )
    parser.add_argument(
        '--timestamp',
        type=str,
        help='Timestamp in ISO format (default: current UTC)'
    )
    parser.add_argument(
        '--pyproject-path',
        type=Path,
        default=Path('./backend/pyproject.toml'),
        help='Path to pyproject.toml (default: ./backend/pyproject.toml)'
    )
    
    args = parser.parse_args()
    
    try:
        # Extract version
        if args.version:
            version = args.version
        else:
            version = extract_version_from_pyproject(args.pyproject_path)
        
        # Get build status
        build_status = args.build_status or os.getenv('BUILD_STATUS', 'passing')
        
        # Get coverage
        coverage = args.coverage or os.getenv('COVERAGE', 'N/A')
        
        # Get timestamp
        if args.timestamp:
            timestamp = args.timestamp
        else:
            timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Parse README
        content, start_line, end_line = parse_readme(args.readme_path)
        
        # Generate new section
        new_section = generate_status_section(
            version=version,
            build_status=build_status,
            coverage=coverage,
            timestamp=timestamp
        )
        
        # Update README
        success = update_readme(
            readme_path=args.readme_path,
            new_section=new_section,
            start_line=start_line,
            end_line=end_line,
            dry_run=args.dry_run
        )
        
        if success:
            if args.dry_run:
                print(" Dry run completed successfully")
            else:
                print(" README updated successfully")
                print(f"   Version: {version}")
                print(f"   Build: {build_status}")
                print(f"   Coverage: {coverage}")
                print(f"   Timestamp: {timestamp}")
            sys.exit(0)
        else:
            print(" Failed to update README")
            sys.exit(1)
    
    except Exception as e:
        print(f" Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
