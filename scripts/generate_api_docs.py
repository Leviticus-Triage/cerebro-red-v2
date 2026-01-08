#!/usr/bin/env python3
"""
scripts/generate_api_docs.py
============================

Generate API reference documentation from OpenAPI schema.

This script extracts the OpenAPI JSON schema and appends it to the manual
API reference documentation, creating a hybrid documentation approach.
"""

import json
import sys
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent
OPENAPI_JSON = REPO_ROOT / "docs" / "openapi.json"
API_REFERENCE_EN = REPO_ROOT / "docs" / "en" / "api-reference.md"
API_REFERENCE_DE = REPO_ROOT / "docs" / "de" / "api-referenz.md"


def load_openapi_schema():
    """Load OpenAPI schema from JSON file."""
    if not OPENAPI_JSON.exists():
        print(f"Error: {OPENAPI_JSON} not found", file=sys.stderr)
        sys.exit(1)
    
    with open(OPENAPI_JSON, 'r') as f:
        return json.load(f)


def generate_endpoint_docs(schema):
    """Generate markdown documentation from OpenAPI schema."""
    paths = schema.get('paths', {})
    tags = {tag['name']: tag.get('description', '') for tag in schema.get('tags', [])}
    
    docs = []
    docs.append("## Auto-Generated Endpoint Reference\n")
    docs.append("This section is automatically generated from the OpenAPI schema.\n")
    
    # Group endpoints by tag
    endpoints_by_tag = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                endpoint_tags = details.get('tags', ['default'])
                for tag in endpoint_tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append({
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'operation_id': details.get('operationId', '')
                    })
    
    # Generate documentation for each tag
    for tag in sorted(endpoints_by_tag.keys()):
        docs.append(f"### {tag.title()}\n")
        if tag in tags:
            docs.append(f"{tags[tag]}\n")
        
        for endpoint in sorted(endpoints_by_tag[tag], key=lambda x: x['path']):
            docs.append(f"#### `{endpoint['method']} {endpoint['path']}`\n")
            if endpoint['summary']:
                docs.append(f"**{endpoint['summary']}**\n\n")
            if endpoint['description']:
                docs.append(f"{endpoint['description']}\n\n")
            docs.append("---\n\n")
    
    return "\n".join(docs)


def append_to_manual_docs(generated_content, target_file):
    """Append generated content to manual documentation."""
    if not target_file.exists():
        print(f"Warning: {target_file} not found, skipping append", file=sys.stderr)
        return
    
    content = target_file.read_text()
    
    # Check if auto-generated section already exists
    if "## Auto-Generated Endpoint Reference" in content:
        # Replace existing auto-generated section
        lines = content.split('\n')
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if "## Auto-Generated Endpoint Reference" in line:
                start_idx = i
            elif start_idx is not None and line.startswith('##') and "Auto-Generated" not in line:
                end_idx = i
                break
        
        if start_idx is not None:
            if end_idx is not None:
                lines = lines[:start_idx] + generated_content.split('\n') + lines[end_idx:]
            else:
                lines = lines[:start_idx] + generated_content.split('\n')
            content = '\n'.join(lines)
    else:
        # Append to end
        content += "\n\n" + generated_content
    
    target_file.write_text(content)
    print(f"✓ Updated {target_file}")


def main():
    """Main execution."""
    print("Generating API documentation from OpenAPI schema...")
    
    schema = load_openapi_schema()
    generated_content = generate_endpoint_docs(schema)
    
    # Append to English documentation
    append_to_manual_docs(generated_content, API_REFERENCE_EN)
    
    # Note: German version would need translation, skipping for now
    print("\n✓ API documentation generation complete")
    print(f"  Updated: {API_REFERENCE_EN}")
    print(f"  Note: German version (api-referenz.md) requires manual translation")


if __name__ == "__main__":
    main()
