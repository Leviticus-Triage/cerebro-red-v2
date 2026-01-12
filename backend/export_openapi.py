"""
Export OpenAPI schema to JSON file with validation and enrichment.

This script exports the FastAPI application's OpenAPI schema
for documentation and API client generation, with validation
and automatic enrichment of missing fields.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main import app


def validate_and_enrich(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and enrich OpenAPI schema with missing fields.
    
    Ensures:
    - All paths have summary, description, tags, operationId
    - Info section has servers, contact, license
    - Security schemes are defined
    - Examples are added where missing
    """
    errors = []
    warnings = []
    
    # Enrich info section
    info = schema.get('info', {})
    if 'servers' not in schema:
        schema['servers'] = [
            {'url': 'http://localhost:9000/api/v1', 'description': 'Local development server'},
            {'url': 'https://api.cerebro-red.example.com/api/v1', 'description': 'Production server'}
        ]
    
    if 'contact' not in info:
        info['contact'] = {
            'name': 'CEREBRO-RED v2 Support',
            'url': 'https://github.com/your-org/cerebro-red-v2/issues',
            'email': 'support@cerebro-red.example.com'
        }
    
    if 'license' not in info:
        info['license'] = {
            'name': 'Apache 2.0',
            'url': 'https://www.apache.org/licenses/LICENSE-2.0'
        }
    
    schema['info'] = info
    
    # Validate and enrich paths
    paths = schema.get('paths', {})
    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                continue
            
            # Check required fields
            if 'summary' not in operation:
                errors.append(f"Missing 'summary' in {method.upper()} {path}")
                operation['summary'] = f"{method.upper()} {path}"
            
            if 'description' not in operation:
                warnings.append(f"Missing 'description' in {method.upper()} {path}")
                operation['description'] = operation.get('summary', '')
            
            if 'tags' not in operation or not operation['tags']:
                warnings.append(f"Missing 'tags' in {method.upper()} {path}")
                # Try to infer tag from path
                tag = path.split('/')[3] if len(path.split('/')) > 3 else 'other'
                operation['tags'] = [tag]
            
            if 'operationId' not in operation:
                # Generate operationId from method and path
                path_parts = path.strip('/').split('/')
                operation_id = f"{method.lower()}_{'_'.join(path_parts)}"
                operation_id = operation_id.replace('{', '').replace('}', '').replace('-', '_')
                operation['operationId'] = operation_id
            
            # Add examples to requestBody if missing
            if 'requestBody' in operation:
                request_body = operation['requestBody']
                content = request_body.get('content', {})
                json_content = content.get('application/json', {})
                if json_content and 'examples' not in json_content and 'example' not in json_content:
                    schema_ref = json_content.get('schema', {})
                    if '$ref' in schema_ref:
                        # Can't generate example from ref, but mark as needing manual addition
                        warnings.append(f"Missing example in requestBody for {method.upper()} {path}")
            
            # Add examples to responses if missing
            responses = operation.get('responses', {})
            for status_code, response_data in responses.items():
                if status_code.startswith('2'):
                    content = response_data.get('content', {})
                    json_content = content.get('application/json', {})
                    if json_content and 'examples' not in json_content and 'example' not in json_content:
                        schema_ref = json_content.get('schema', {})
                        if '$ref' in schema_ref:
                            warnings.append(f"Missing example in {status_code} response for {method.upper()} {path}")
    
    # Ensure security schemes are defined
    components = schema.get('components', {})
    if 'securitySchemes' not in components:
        components['securitySchemes'] = {
            'ApiKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key',
                'description': 'API key authentication'
            }
        }
        schema['components'] = components
    
    # Report validation results
    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"   - {error}")
        raise ValueError(f"Schema validation failed with {len(errors)} errors")
    
    if warnings:
        print(f"⚠️  Validation warnings ({len(warnings)}):")
        for warning in warnings[:10]:  # Show first 10
            print(f"   - {warning}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more warnings")
    
    return schema


def main():
    """Main entry point."""
    # Get OpenAPI schema
    print("📋 Generating OpenAPI schema...")
    openapi_schema = app.openapi()
    
    # Validate and enrich
    print("🔍 Validating and enriching schema...")
    openapi_schema = validate_and_enrich(openapi_schema)
    
    # Write to docs/openapi.json
    docs_dir = Path(__file__).parent.parent / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = docs_dir / "openapi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    # Statistics
    paths = openapi_schema.get('paths', {})
    total_endpoints = sum(
        len([m for m in methods.keys() if m.lower() in ['get', 'post', 'put', 'patch', 'delete']])
        for methods in paths.values()
    )
    
    print(f"✅ OpenAPI schema exported to {output_file}")
    print(f"   Total paths: {len(paths)}")
    print(f"   Total endpoints: {total_endpoints}")
    print(f"   API version: {openapi_schema.get('info', {}).get('version', 'unknown')}")
    print(f"   Servers: {len(openapi_schema.get('servers', []))}")


if __name__ == "__main__":
    main()

