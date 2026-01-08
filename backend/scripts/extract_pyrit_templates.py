#!/usr/bin/env python3
"""
Extract PyRIT YAML templates and convert to JSON format for CEREBRO-RED v2.

This script parses PyRIT jailbreak templates from:
- pyrit/datasets/jailbreak/templates/*.yaml
- pyrit/datasets/executors/crescendo/*.yaml
- pyrit/datasets/executors/skeleton_key/*.prompt

Output: JSON structure compatible with advanced_payloads.json
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def parse_pyrit_yaml(yaml_path: Path) -> Dict[str, Any]:
    """Parse a PyRIT YAML template file."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return {
            'name': data.get('name', yaml_path.stem),
            'description': data.get('description', ''),
            'authors': data.get('authors', []),
            'source': data.get('source', ''),
            'parameters': data.get('parameters', []),
            'template': data.get('value', ''),
            'file_path': str(yaml_path.relative_to(Path(__file__).parent.parent.parent))
        }
    except Exception as e:
        print(f"Error parsing {yaml_path}: {e}", file=sys.stderr)
        return None


def parse_pyrit_prompt(prompt_path: Path) -> Dict[str, Any]:
    """Parse a PyRIT .prompt file."""
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'name': prompt_path.stem,
            'description': f'PyRIT prompt from {prompt_path.name}',
            'authors': ['Microsoft AI Red Team'],
            'source': 'PyRIT',
            'template': content,
            'file_path': str(prompt_path.relative_to(Path(__file__).parent.parent.parent))
        }
    except Exception as e:
        print(f"Error parsing {prompt_path}: {e}", file=sys.stderr)
        return None


def categorize_template(template_data: Dict[str, Any]) -> str:
    """Categorize template by name/description into CEREBRO strategy."""
    name_lower = template_data['name'].lower()
    template_lower = template_data.get('template', '').lower()
    
    # Jailbreak categories
    if 'dude' in name_lower:
        return 'jailbreak_dude'
    elif 'dan' in name_lower or 'do anything now' in template_lower:
        return 'jailbreak_dan'
    elif 'aim' in name_lower or 'machiavellian' in template_lower:
        return 'jailbreak_aim'
    elif 'stan' in name_lower or 'strive to avoid norms' in template_lower:
        return 'jailbreak_stan'
    elif 'developer' in name_lower or 'dev mode' in template_lower:
        return 'jailbreak_developer_mode'
    elif 'skeleton' in name_lower or 'skeleton key' in template_lower:
        return 'skeleton_key'
    elif 'crescendo' in name_lower:
        return 'crescendo_attack'
    elif 'many' in name_lower and 'shot' in name_lower:
        return 'many_shot_jailbreak'
    elif 'role' in name_lower and 'play' in name_lower:
        return 'roleplay_injection'
    elif 'direct' in name_lower or 'ignore' in template_lower[:100]:
        return 'direct_injection'
    elif 'indirect' in name_lower:
        return 'indirect_injection'
    elif 'research' in name_lower or 'researcher' in name_lower:
        return 'research_pre_jailbreak'
    else:
        return 'other'


def extract_all_pyrit_templates(base_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Extract all PyRIT templates and group by category."""
    templates_by_category: Dict[str, List[Dict[str, Any]]] = {}
    
    # Jailbreak templates
    jailbreak_dir = base_path / 'PyRIT' / 'pyrit' / 'datasets' / 'jailbreak' / 'templates'
    if jailbreak_dir.exists():
        for yaml_file in jailbreak_dir.rglob('*.yaml'):
            template_data = parse_pyrit_yaml(yaml_file)
            if template_data:
                category = categorize_template(template_data)
                if category not in templates_by_category:
                    templates_by_category[category] = []
                templates_by_category[category].append(template_data)
    
    # Crescendo templates
    crescendo_dir = base_path / 'PyRIT' / 'pyrit' / 'datasets' / 'executors' / 'crescendo'
    if crescendo_dir.exists():
        for yaml_file in crescendo_dir.rglob('*.yaml'):
            template_data = parse_pyrit_yaml(yaml_file)
            if template_data:
                if 'crescendo_attack' not in templates_by_category:
                    templates_by_category['crescendo_attack'] = []
                templates_by_category['crescendo_attack'].append(template_data)
    
    # Skeleton Key prompts
    skeleton_dir = base_path / 'PyRIT' / 'pyrit' / 'datasets' / 'executors' / 'skeleton_key'
    if skeleton_dir.exists():
        for prompt_file in skeleton_dir.rglob('*.prompt'):
            template_data = parse_pyrit_prompt(prompt_file)
            if template_data:
                if 'skeleton_key' not in templates_by_category:
                    templates_by_category['skeleton_key'] = []
                templates_by_category['skeleton_key'].append(template_data)
    
    return templates_by_category


def format_for_payloads_json(templates_by_category: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Format extracted templates for advanced_payloads.json structure."""
    output = {}
    
    for category, templates in templates_by_category.items():
        if category == 'other':
            continue  # Skip uncategorized
        
        output[category] = {
            'description': f'PyRIT templates for {category}',
            'severity': 'high',
            'source': 'PyRIT (Microsoft AI Red Team)',
            'authors': ['Microsoft AI Red Team'],
            'templates': []
        }
        
        for template in templates:
            # Replace PyRIT parameter syntax {{ prompt }} with {original_prompt}
            template_text = template['template'].replace('{{ prompt }}', '{original_prompt}')
            template_text = template_text.replace('{{prompt}}', '{original_prompt}')
            
            output[category]['templates'].append(template_text)
    
    return output


if __name__ == '__main__':
    base_path = Path(__file__).parent.parent.parent
    
    print("Extracting PyRIT templates...")
    templates_by_category = extract_all_pyrit_templates(base_path)
    
    print(f"Found {sum(len(t) for t in templates_by_category.values())} templates in {len(templates_by_category)} categories")
    
    formatted = format_for_payloads_json(templates_by_category)
    
    # Output to JSON
    output_path = base_path / 'backend' / 'data' / 'pyrit_extracted.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted templates written to {output_path}")
    
    # Print summary
    for category, templates in templates_by_category.items():
        print(f"  {category}: {len(templates)} templates")
