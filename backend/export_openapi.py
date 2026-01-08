"""
Export OpenAPI schema to JSON file.

This script exports the FastAPI application's OpenAPI schema
for documentation and API client generation.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main import app

# Get OpenAPI schema
openapi_schema = app.openapi()

# Write to docs/openapi.json
docs_dir = Path(__file__).parent.parent / "docs"
docs_dir.mkdir(exist_ok=True)

output_file = docs_dir / "openapi.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

print(f"✅ OpenAPI schema exported to {output_file}")
print(f"   Total endpoints: {len(openapi_schema.get('paths', {}))}")
print(f"   API version: {openapi_schema.get('info', {}).get('version', 'unknown')}")

