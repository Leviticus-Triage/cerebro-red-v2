#!/usr/bin/env python3
"""
Phase 7: Merge advanced_payloads.json into payloads.json

This script merges the repo-derived templates from advanced_payloads.json
into the main payloads.json file, preserving existing categories.
"""

import json
from pathlib import Path
from datetime import datetime

def merge_payloads():
    """Merge advanced_payloads.json into payloads.json."""
    
    data_dir = Path(__file__).parent
    payloads_file = data_dir / "payloads.json"
    advanced_file = data_dir / "advanced_payloads.json"
    backup_file = data_dir / f"payloads.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("═" * 79)
    print("  PHASE 7: PAYLOAD FILE MERGE")
    print("═" * 79)
    print()
    
    # Load existing payloads
    print(f" Loading {payloads_file.name}...")
    with open(payloads_file, 'r', encoding='utf-8') as f:
        payloads = json.load(f)
    
    existing_categories = set(payloads.get("categories", {}).keys())
    print(f"   Found {len(existing_categories)} existing categories")
    
    # Load advanced payloads
    print(f" Loading {advanced_file.name}...")
    with open(advanced_file, 'r', encoding='utf-8') as f:
        advanced = json.load(f)
    
    # Filter out metadata keys
    metadata_keys = {"version", "source", "last_updated"}
    advanced_categories = {k: v for k, v in advanced.items() if k not in metadata_keys}
    print(f"   Found {len(advanced_categories)} advanced categories")
    
    # Backup original
    print(f" Creating backup: {backup_file.name}...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(payloads, f, indent=2, ensure_ascii=False)
    
    # Merge categories
    print(f" Merging categories...")
    if "categories" not in payloads:
        payloads["categories"] = {}
    
    merged_count = 0
    skipped_count = 0
    
    for category, templates in advanced_categories.items():
        if category in payloads["categories"]:
            print(f"   ️  Skipping {category} (already exists)")
            skipped_count += 1
        else:
            payloads["categories"][category] = templates
            print(f"    Added {category} ({len(templates)} templates)")
            merged_count += 1
    
    # Update metadata
    if "metadata" not in payloads:
        payloads["metadata"] = {}
    
    payloads["metadata"]["last_updated"] = datetime.now().isoformat()
    payloads["metadata"]["total_categories"] = len(payloads["categories"])
    payloads["metadata"]["merged_from_advanced"] = merged_count
    payloads["metadata"]["merge_date"] = datetime.now().isoformat()
    
    # Save merged file
    print(f" Saving merged payloads to {payloads_file.name}...")
    with open(payloads_file, 'w', encoding='utf-8') as f:
        json.dump(payloads, f, indent=2, ensure_ascii=False)
    
    print()
    print("═" * 79)
    print("  MERGE COMPLETE")
    print("═" * 79)
    print()
    print(f" Merged {merged_count} new categories")
    print(f"️  Skipped {skipped_count} existing categories")
    print(f" Total categories: {len(payloads['categories'])}")
    print(f" Backup saved: {backup_file.name}")
    print()
    print("Next steps:")
    print("  1. Rebuild Docker image: docker compose build cerebro-backend")
    print("  2. Restart container: docker compose up -d cerebro-backend")
    print("  3. Re-run tests: ./run_tests.sh payload")
    print()

if __name__ == "__main__":
    merge_payloads()
