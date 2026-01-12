"""
Generate API Reference Documentation from OpenAPI Schema

This script reads the OpenAPI schema (openapi.json) and generates
comprehensive API reference documentation in Markdown format.

Features:
- Automatic endpoint documentation generation
- Request/response schema documentation
- Authentication requirements
- Code examples in multiple languages
- Error response documentation
- Rate limiting information

Usage:
    python scripts/generate_api_docs.py

Output:
    ../docs/en/api-reference.md (generated documentation)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class EndpointDoc:
    """Represents documentation for a single API endpoint."""
    path: str
    method: str
    summary: str
    description: str
    tags: List[str]
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    security: List[Dict[str, Any]]
    deprecated: bool = False


class APIDocGenerator:
    """Generates Markdown documentation from OpenAPI schema."""

    def __init__(self, openapi_path: Path):
        """Initialize generator with OpenAPI schema."""
        self.openapi_path = openapi_path
        self.schema = self._load_schema()
        self.endpoints = self._parse_endpoints()

    def _load_schema(self) -> Dict[str, Any]:
        """Load and parse OpenAPI schema."""
        if not self.openapi_path.exists():
            raise FileNotFoundError(f"OpenAPI schema not found: {self.openapi_path}")

        with open(self.openapi_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_endpoints(self) -> List[EndpointDoc]:
        """Parse all endpoints from OpenAPI schema."""
        endpoints = []

        paths = self.schema.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'patch', 'delete']:
                    endpoint = EndpointDoc(
                        path=path,
                        method=method.upper(),
                        summary=details.get('summary', 'No summary'),
                        description=details.get('description', ''),
                        tags=details.get('tags', []),
                        parameters=details.get('parameters', []),
                        request_body=details.get('requestBody'),
                        responses=details.get('responses', {}),
                        security=details.get('security', []),
                        deprecated=details.get('deprecated', False)
                    )
                    endpoints.append(endpoint)

        # Sort by tag and path
        endpoints.sort(key=lambda e: (e.tags[0] if e.tags else 'zzz', e.path))
        return endpoints

    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """Format parameter documentation."""
        if not parameters:
            return "*No parameters*\n"

        # Group by location (path, query, header)
        by_location = {}
        for param in parameters:
            location = param.get('in', 'unknown')
            if location not in by_location:
                by_location[location] = []
            by_location[location].append(param)

        output = []

        # Path parameters
        if 'path' in by_location:
            output.append("**Path Parameters:**\n")
            for param in by_location['path']:
                name = param.get('name', 'unknown')
                required = " *(required)*" if param.get('required', False) else ""
                schema = param.get('schema', {})
                param_type = schema.get('type', 'string')
                description = param.get('description', 'No description')
                output.append(f"- `{name}` ({param_type}){required}: {description}\n")
            output.append("\n")

        # Query parameters
        if 'query' in by_location:
            output.append("**Query Parameters:**\n")
            for param in by_location['query']:
                name = param.get('name', 'unknown')
                required = " *(required)*" if param.get('required', False) else ""
                schema = param.get('schema', {})
                param_type = schema.get('type', 'string')
                default = schema.get('default')
                description = param.get('description', 'No description')

                default_text = f" (default: `{default}`)" if default is not None else ""
                output.append(f"- `{name}` ({param_type}){required}{default_text}: {description}\n")
            output.append("\n")

        # Header parameters
        if 'header' in by_location:
            output.append("**Headers:**\n")
            for param in by_location['header']:
                name = param.get('name', 'unknown')
                required = " *(required)*" if param.get('required', False) else ""
                description = param.get('description', 'No description')
                output.append(f"- `{name}`{required}: {description}\n")
            output.append("\n")

        return ''.join(output)

    def _format_request_body(self, request_body: Optional[Dict[str, Any]]) -> str:
        """Format request body documentation."""
        if not request_body:
            return "*No request body*\n"

        content = request_body.get('content', {})
        if not content:
            return "*No request body*\n"

        # Get JSON schema if available
        json_schema = content.get('application/json', {}).get('schema', {})
        if not json_schema:
            return "*Request body: application/json*\n"

        # Check if it's a reference
        if '$ref' in json_schema:
            ref_name = json_schema['$ref'].split('/')[-1]
            return f"**Request Body:** See schema [`{ref_name}`](#schema-{ref_name.lower()})\n\n"

        # Format inline schema
        output = ["**Request Body (application/json):**\n\n"]
        output.append("```json\n")
        output.append(json.dumps(self._schema_to_example(json_schema), indent=2))
        output.append("\n```\n\n")

        return ''.join(output)

    def _format_responses(self, responses: Dict[str, Dict[str, Any]]) -> str:
        """Format response documentation."""
        if not responses:
            return "*No documented responses*\n"

        output = ["**Responses:**\n\n"]

        for status_code, response_data in sorted(responses.items()):
            description = response_data.get('description', 'No description')
            output.append(f"**{status_code}** - {description}\n\n")

            content = response_data.get('content', {})
            json_content = content.get('application/json', {})

            if json_content:
                schema = json_content.get('schema', {})
                if schema:
                    if '$ref' in schema:
                        ref_name = schema['$ref'].split('/')[-1]
                        output.append(f"Response schema: [`{ref_name}`](#schema-{ref_name.lower()})\n\n")
                    else:
                        output.append("```json\n")
                        output.append(json.dumps(self._schema_to_example(schema), indent=2))
                        output.append("\n```\n\n")

        return ''.join(output)

    def _schema_to_example(self, schema: Dict[str, Any]) -> Any:
        """Convert JSON schema to example data."""
        schema_type = schema.get('type', 'object')

        if schema_type == 'object':
            properties = schema.get('properties', {})
            example = {}
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._schema_to_example(prop_schema)
            return example

        elif schema_type == 'array':
            items = schema.get('items', {})
            return [self._schema_to_example(items)]

        elif schema_type == 'string':
            return schema.get('example', 'string')

        elif schema_type == 'integer':
            return schema.get('example', 0)

        elif schema_type == 'number':
            return schema.get('example', 0.0)

        elif schema_type == 'boolean':
            return schema.get('example', False)

        else:
            return None

    def _generate_curl_example(self, endpoint: EndpointDoc) -> str:
        """Generate cURL command example."""
        base_url = "http://localhost:9000"

        # Replace path parameters with examples
        path = endpoint.path
        for param in endpoint.parameters:
            if param.get('in') == 'path':
                param_name = param.get('name')
                path = path.replace(f"{{{param_name}}}", f"example-{param_name}")

        # Build cURL command
        cmd = [f"curl -X {endpoint.method}"]
        cmd.append(f'"{base_url}{path}"')

        # Add authentication if required
        if endpoint.security:
            cmd.append("-H 'X-API-Key: your-api-key'")

        # Add content-type for POST/PUT/PATCH
        if endpoint.method in ['POST', 'PUT', 'PATCH'] and endpoint.request_body:
            cmd.append("-H 'Content-Type: application/json'")

        # Add query parameters example
        query_params = [p for p in endpoint.parameters if p.get('in') == 'query']
        if query_params and len(query_params) <= 2:  # Only show if few params
            param_examples = []
            for param in query_params[:2]:
                name = param.get('name')
                schema = param.get('schema', {})
                default = schema.get('default', 'value')
                param_examples.append(f"{name}={default}")

            if param_examples:
                # Add ? or & to path
                separator = '&' if '?' in path else '?'
                cmd[1] = cmd[1].replace('"', '') + separator + '&'.join(param_examples) + '"'

        # Add request body example
        if endpoint.request_body and endpoint.method in ['POST', 'PUT', 'PATCH']:
            content = endpoint.request_body.get('content', {})
            json_schema = content.get('application/json', {}).get('schema', {})
            if json_schema:
                example = self._schema_to_example(json_schema)
                body_json = json.dumps(example, separators=(',', ':'))
                cmd.append(f"-d '{body_json}'")

        return ' \\\n  '.join(cmd)

    def _generate_python_example(self, endpoint: EndpointDoc) -> str:
        """Generate Python requests example."""
        base_url = "http://localhost:9000"

        # Replace path parameters
        path = endpoint.path
        path_params = {}
        for param in endpoint.parameters:
            if param.get('in') == 'path':
                param_name = param.get('name')
                path_params[param_name] = f"example_{param_name}"
                path = path.replace(f"{{{param_name}}}", f"{{param_name}}")

        lines = ["import requests", ""]

        # Add base URL and path
        if path_params:
            for key, val in path_params.items():
                lines.append(f'{key} = "{val}"')
            lines.append(f'url = f"{base_url}{path}"')
        else:
            lines.append(f'url = "{base_url}{path}"')

        # Add headers
        headers = {}
        if endpoint.security:
            headers['X-API-Key'] = 'your-api-key'
        if endpoint.method in ['POST', 'PUT', 'PATCH'] and endpoint.request_body:
            headers['Content-Type'] = 'application/json'

        if headers:
            lines.append("headers = {")
            for key, val in headers.items():
                lines.append(f'    "{key}": "{val}",')
            lines.append("}")

        # Add query parameters
        query_params = [p for p in endpoint.parameters if p.get('in') == 'query']
        if query_params:
            lines.append("params = {")
            for param in query_params[:2]:  # Limit examples
                name = param.get('name')
                schema = param.get('schema', {})
                default = schema.get('default', 'value')
                if isinstance(default, str):
                    lines.append(f'    "{name}": "{default}",')
                else:
                    lines.append(f'    "{name}": {default},')
            lines.append("}")

        # Add request body
        if endpoint.request_body and endpoint.method in ['POST', 'PUT', 'PATCH']:
            content = endpoint.request_body.get('content', {})
            json_schema = content.get('application/json', {}).get('schema', {})
            if json_schema:
                lines.append("data = {")
                example = self._schema_to_example(json_schema)
                for key, val in (example.items() if isinstance(example, dict) else {}):
                    if isinstance(val, str):
                        lines.append(f'    "{key}": "{val}",')
                    else:
                        lines.append(f'    "{key}": {json.dumps(val)},')
                lines.append("}")

        # Make request
        request_args = ["url"]
        if headers:
            request_args.append("headers=headers")
        if query_params:
            request_args.append("params=params")
        if endpoint.request_body and endpoint.method in ['POST', 'PUT', 'PATCH']:
            request_args.append("json=data")

        method = endpoint.method.lower()
        lines.append(f"response = requests.{method}({', '.join(request_args)})")
        lines.append("print(response.json())")

        return '\n'.join(lines)

    def _generate_endpoint_section(self, endpoint: EndpointDoc) -> str:
        """Generate documentation section for a single endpoint."""
        output = []

        # Endpoint header
        deprecated_tag = " 🚫 DEPRECATED" if endpoint.deprecated else ""
        output.append(f"### `{endpoint.method} {endpoint.path}`{deprecated_tag}\n\n")

        # Summary and description
        output.append(f"**{endpoint.summary}**\n\n")
        if endpoint.description:
            output.append(f"{endpoint.description}\n\n")

        # Authentication
        if endpoint.security:
            output.append("🔒 **Authentication Required:** API Key\n\n")

        # Parameters
        if endpoint.parameters:
            output.append(self._format_parameters(endpoint.parameters))

        # Request body
        if endpoint.request_body:
            output.append(self._format_request_body(endpoint.request_body))

        # Responses
        output.append(self._format_responses(endpoint.responses))

        # Code examples
        output.append("**Examples:**\n\n")

        # cURL example
        output.append("<details>\n<summary>cURL</summary>\n\n```bash\n")
        output.append(self._generate_curl_example(endpoint))
        output.append("\n```\n</details>\n\n")

        # Python example
        output.append("<details>\n<summary>Python</summary>\n\n```python\n")
        output.append(self._generate_python_example(endpoint))
        output.append("\n```\n</details>\n\n")

        output.append("---\n\n")

        return ''.join(output)

    def generate(self) -> str:
        """Generate complete API reference documentation."""
        output = []

        # Header
        info = self.schema.get('info', {})
        title = info.get('title', 'API Reference')
        version = info.get('version', '1.0.0')
        description = info.get('description', '')

        output.append(f"# {title}\n\n")
        output.append(f"**Version:** {version}\n\n")
        if description:
            output.append(f"{description}\n\n")

        output.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        output.append("---\n\n")

        # Table of contents
        output.append("## Table of Contents\n\n")

        # Group endpoints by tag
        by_tag = {}
        for endpoint in self.endpoints:
            tag = endpoint.tags[0] if endpoint.tags else 'Other'
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(endpoint)

        for tag in sorted(by_tag.keys()):
            tag_id = tag.lower().replace(' ', '-')
            output.append(f"- [{tag}](#{tag_id})\n")
            for endpoint in by_tag[tag]:
                endpoint_id = f"{tag_id}-{endpoint.method.lower()}-{endpoint.path.replace('/', '-').replace('{', '').replace('}', '')}"
                output.append(f"  - [`{endpoint.method} {endpoint.path}`](#{endpoint_id})\n")

        output.append("\n---\n\n")

        # Authentication, Rate Limiting, Error Responses sections
        # These will be replaced by manual sections if available in template
        output.append("## Authentication\n\n")
        output.append("*(This section will be replaced by manual content if available)*\n\n")
        output.append("---\n\n")

        output.append("## Rate Limiting\n\n")
        output.append("*(This section will be replaced by manual content if available)*\n\n")
        output.append("---\n\n")

        output.append("## Error Responses\n\n")
        output.append("*(This section will be replaced by manual content if available)*\n\n")
        output.append("---\n\n")

        # Endpoints by tag
        for tag in sorted(by_tag.keys()):
            tag_id = tag.lower().replace(' ', '-')
            output.append(f"## {tag}\n\n")

            for endpoint in by_tag[tag]:
                output.append(self._generate_endpoint_section(endpoint))

        # Schemas section
        output.append("## Data Schemas\n\n")
        output.append("Common data schemas used across endpoints:\n\n")

        components = self.schema.get('components', {})
        schemas = components.get('schemas', {})

        for schema_name, schema_def in sorted(schemas.items()):
            schema_id = schema_name.lower()
            output.append(f"### `{schema_name}` {{#schema-{schema_id}}}\n\n")

            description = schema_def.get('description', '')
            if description:
                output.append(f"{description}\n\n")

            output.append("```json\n")
            output.append(json.dumps(self._schema_to_example(schema_def), indent=2))
            output.append("\n```\n\n")

        return ''.join(output)


def load_manual_sections(template_file: Path) -> Dict[str, str]:
    """
    Load manual sections from template file.
    
    Returns a dictionary mapping section headers to content.
    """
    if not template_file.exists():
        print(f"⚠️  Manual sections template not found: {template_file}")
        return {}
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        # Check if line is a header (starts with ##)
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = line[3:].strip()  # Remove '## '
            current_content = []
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def merge_manual_sections(generated_doc: str, manual_sections: Dict[str, str]) -> str:
    """
    Merge manual sections into generated documentation.
    
    Replaces or inserts manual sections at appropriate locations.
    """
    lines = generated_doc.split('\n')
    output = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a section header we want to replace
        if line.startswith('## '):
            section_name = line[3:].strip()
            
            # Check if we have a manual section for this
            if section_name in manual_sections:
                # Replace with manual section
                output.append(line)
                output.append('')
                output.append(manual_sections[section_name])
                output.append('')
                output.append('---')
                output.append('')
                
                # Skip the generated content for this section until next ## or ---
                i += 1
                while i < len(lines):
                    if lines[i].startswith('## ') or (lines[i].strip() == '---' and i > 0):
                        i -= 1  # Back up to process this line
                        break
                    i += 1
                i += 1
                continue
        
        output.append(line)
        i += 1
    
    return '\n'.join(output)


def main():
    """Main entry point."""
    # Paths
    backend_dir = Path(__file__).parent.parent
    project_root = backend_dir.parent
    openapi_file = project_root / "docs" / "openapi.json"
    template_file = project_root / "docs" / "templates" / "manual-sections.md"
    output_file = project_root / "docs" / "en" / "api-reference.md"

    # Ensure OpenAPI schema exists
    if not openapi_file.exists():
        print("❌ OpenAPI schema not found. Run 'python backend/export_openapi.py' first.")
        sys.exit(1)

    # Load manual sections
    print("📖 Loading manual sections...")
    manual_sections = load_manual_sections(template_file)

    # Generate documentation
    print("📚 Generating API reference documentation...")
    generator = APIDocGenerator(openapi_file)
    documentation = generator.generate()

    # Merge manual sections
    if manual_sections:
        print(f"🔗 Merging {len(manual_sections)} manual sections...")
        documentation = merge_manual_sections(documentation, manual_sections)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write documentation
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(documentation)

    print(f"✅ API reference generated: {output_file}")
    print(f"   Total endpoints documented: {len(generator.endpoints)}")
    print(f"   Manual sections merged: {len(manual_sections)}")
    print(f"   File size: {len(documentation):,} characters")


if __name__ == "__main__":
    main()
