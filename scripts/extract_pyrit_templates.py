#!/usr/bin/env python3
"""
Extract PyRIT jailbreak templates from YAML files and convert to payloads.json format.

This script:
1. Parses all YAML files in PyRIT/pyrit/datasets/jailbreak/templates/
2. Groups templates by jailbreak type (DAN, AIM, DUDE, Developer Mode, etc.)
3. Converts {{ prompt }} placeholders to {original_prompt}
4. Outputs JSON compatible with backend/data/payloads.json structure
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import re


def normalize_placeholder(text: str) -> str:
    """Convert PyRIT {{ prompt }} to CEREBRO {original_prompt}."""
    # Replace {{ prompt }} with {original_prompt}
    text = re.sub(r'\{\{\s*prompt\s*\}\}', '{original_prompt}', text)
    # Also handle variations like {{prompt}}, {{ prompt}}, etc.
    text = re.sub(r'\{\{\s*prompt\s*\}\}', '{original_prompt}', text, flags=re.IGNORECASE)
    return text


def parse_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Parse a single PyRIT YAML template file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'value' not in data:
            return None
        
        template_text = data['value']
        # Normalize placeholder
        template_text = normalize_placeholder(template_text)
        
        return {
            'name': data.get('name', file_path.stem),
            'description': data.get('description', ''),
            'template': template_text,
            'source': data.get('source', 'PyRIT'),
            'authors': data.get('authors', [])
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def categorize_template(filename: str, name: str) -> str:
    """Categorize template by filename and name."""
    filename_lower = filename.lower()
    name_lower = name.lower()
    
    # DAN variants
    if 'dan' in filename_lower or 'dan' in name_lower:
        if 'superior' in filename_lower or 'superior' in name_lower:
            return 'jailbreak_dan_templates'
        elif 'better' in filename_lower or 'better' in name_lower:
            return 'jailbreak_dan_templates'
        elif 'cosmos' in filename_lower or 'cosmos' in name_lower:
            return 'jailbreak_dan_templates'
        else:
            return 'jailbreak_dan_templates'
    
    # AIM
    if 'aim' in filename_lower or 'aim' in name_lower or 'machiavellian' in name_lower:
        return 'jailbreak_aim_templates'
    
    # DUDE
    if 'dude' in filename_lower or 'dude' in name_lower:
        return 'jailbreak_dude_templates'
    
    # Developer Mode
    if 'dev_mode' in filename_lower or 'developer' in filename_lower or 'developer' in name_lower:
        return 'jailbreak_developer_mode_templates'
    
    # STAN (if exists)
    if 'stan' in filename_lower or 'stan' in name_lower:
        return 'jailbreak_stan_templates'
    
    # Skeleton Key
    if 'skeleton' in filename_lower or 'skeleton' in name_lower:
        return 'jailbreak_skeleton_key_templates'
    
    # Many-shot
    if 'many_shot' in filename_lower or 'many-shot' in filename_lower:
        return 'many_shot_jailbreak_templates'
    
    # Crescendo
    if 'crescendo' in filename_lower or 'crescendo' in name_lower:
        return 'crescendo_attack_templates'
    
    # Default: advanced jailbreak
    return 'jailbreak_advanced_templates'


def extract_all_templates(pyrit_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Extract all templates from PyRIT directory."""
    templates_dir = pyrit_path / 'pyrit' / 'datasets' / 'jailbreak' / 'templates'
    
    if not templates_dir.exists():
        print(f"Error: Templates directory not found: {templates_dir}")
        return {}
    
    categorized = defaultdict(list)
    
    # Get all YAML files (exclude multi_parameter subdirectory as per PyRIT convention)
    yaml_files = [
        f for f in templates_dir.rglob('*.yaml')
        if 'multi_parameter' not in f.parts
    ]
    
    print(f"Found {len(yaml_files)} YAML files")
    
    for yaml_file in yaml_files:
        parsed = parse_yaml_file(yaml_file)
        if parsed:
            category = categorize_template(yaml_file.stem, parsed['name'])
            categorized[category].append(parsed['template'])
            print(f"   {yaml_file.stem} → {category}")
    
    return dict(categorized)


def generate_payloads_json(categorized_templates: Dict[str, List[str]]) -> Dict[str, Any]:
    """Generate payloads.json compatible structure."""
    categories = {}
    
    descriptions = {
        'jailbreak_dan_templates': 'DAN (Do Anything Now) jailbreak variants from PyRIT',
        'jailbreak_aim_templates': 'AIM (Always Intelligent and Machiavellian) jailbreak from PyRIT',
        'jailbreak_dude_templates': 'DUDE jailbreak variants from PyRIT',
        'jailbreak_developer_mode_templates': 'Developer Mode jailbreak variants from PyRIT',
        'jailbreak_stan_templates': 'STAN (Strive To Avoid Norms) jailbreak from PyRIT',
        'jailbreak_skeleton_key_templates': 'Skeleton Key universal jailbreak from PyRIT',
        'many_shot_jailbreak_templates': 'Many-Shot jailbreak templates from PyRIT',
        'crescendo_attack_templates': 'Crescendo multi-turn escalation attack templates',
        'jailbreak_advanced_templates': 'Advanced jailbreak techniques from PyRIT',
    }
    
    for category, templates in categorized_templates.items():
        if templates:
            categories[category] = {
                'description': descriptions.get(category, f'{category} from PyRIT'),
                'templates': templates[:10]  # Limit to 10 templates per category
            }
    
    return {
        'categories': categories,
        'metadata': {
            'source': 'PyRIT',
            'extracted_templates': sum(len(t) for t in categorized_templates.values()),
            'categories_count': len(categories)
        }
    }


def main():
    """Main extraction function."""
    # Path to PyRIT directory (relative to script location)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    pyrit_path = project_root / 'PyRIT'
    
    if not pyrit_path.exists():
        print(f"Error: PyRIT directory not found at {pyrit_path}")
        return
    
    print(f"Extracting templates from: {pyrit_path}")
    
    # Extract templates
    categorized = extract_all_templates(pyrit_path)
    
    # Generate JSON structure
    payloads_json = generate_payloads_json(categorized)
    
    # Output to file
    output_file = project_root / 'backend' / 'data' / 'pyrit_templates_extracted.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(payloads_json, f, indent=2, ensure_ascii=False)
    
    print(f"\n Extracted {payloads_json['metadata']['extracted_templates']} templates")
    print(f" Created {payloads_json['metadata']['categories_count']} categories")
    print(f" Output saved to: {output_file}")
    print("\nNext step: Merge into backend/data/payloads.json")


if __name__ == '__main__':
    main()
