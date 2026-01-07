#!/usr/bin/env python3
"""
Extract L1B3RT4S markdown prompts and convert to JSON format for CEREBRO-RED v2.

This script parses L1B3RT4S jailbreak prompts from:
- L1B3RT4S/*.mkd (markdown files with provider-specific jailbreaks)
- L1B3RT4S/#MOTHERLOAD.txt (advanced techniques)

Output: JSON structure compatible with advanced_payloads.json
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def extract_prompts_from_markdown(md_path: Path) -> List[Dict[str, Any]]:
    """Extract prompts from L1B3RT4S markdown file."""
    prompts = []
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # L1B3RT4S files contain prompts separated by headers, code blocks, or newlines
        # Extract text blocks that look like jailbreak prompts
        
        # Split by common separators
        blocks = re.split(r'\n{3,}|#{2,}\s+', content)
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            # Skip if too short or looks like metadata
            if len(block) < 20:
                continue
            
            # Skip if looks like a header or code block marker
            if block.startswith('#') or block.startswith('```'):
                continue
            
            # Check if it contains jailbreak-like content
            if any(keyword in block.lower() for keyword in [
                'ignore', 'jailbreak', 'developer mode', 'godmode', 'unrestricted',
                'bypass', 'filter', 'censor', 'ethics', 'policy', 'restriction'
            ]):
                prompts.append({
                    'prompt': block,
                    'source_file': md_path.name,
                    'provider': md_path.stem.upper() if md_path.stem != '-MISCELLANEOUS-' else 'GENERAL'
                })
    
    except Exception as e:
        print(f"Error parsing {md_path}: {e}", file=sys.stderr)
    
    return prompts


def categorize_l1b3rt4s_prompt(prompt_data: Dict[str, Any]) -> str:
    """Categorize L1B3RT4S prompt by content into CEREBRO strategy."""
    prompt_lower = prompt_data['prompt'].lower()
    
    # Emoji encoding
    if any(char in prompt_data['prompt'] for char in ['🎵', '🗣️', '☢️', '👅', '🍑']):
        return 'obfuscation_unicode'
    
    # Leetspeak + dividers (GODMODE patterns)
    if 'godmode' in prompt_lower or '.-.-.-' in prompt_data['prompt'] or '|l|o|v|e|' in prompt_lower:
        return 'obfuscation_leetspeak'
    
    # Steganography (zero-width, hidden text)
    if any(ord(c) > 0x2000 and ord(c) < 0x206F for c in prompt_data['prompt']):
        return 'obfuscation_token_smuggling'
    
    # Developer mode
    if 'developer mode' in prompt_lower or 'dev mode' in prompt_lower:
        return 'jailbreak_developer_mode'
    
    # Roleplay
    if 'role' in prompt_lower and ('play' in prompt_lower or 'pretend' in prompt_lower):
        return 'roleplay_injection'
    
    # Direct injection
    if 'ignore' in prompt_lower[:100] or 'forget' in prompt_lower[:100]:
        return 'direct_injection'
    
    # Default to obfuscation_unicode for L1B3RT4S (many use emoji/unicode)
    return 'obfuscation_unicode'


def extract_all_l1b3rt4s_prompts(base_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Extract all L1B3RT4S prompts and group by category."""
    prompts_by_category: Dict[str, List[Dict[str, Any]]] = {}
    
    l1b3rt4s_dir = base_path / 'L1B3RT4S'
    if not l1b3rt4s_dir.exists():
        print(f"L1B3RT4S directory not found at {l1b3rt4s_dir}", file=sys.stderr)
        return prompts_by_category
    
    # Process .mkd files
    for mkd_file in l1b3rt4s_dir.glob('*.mkd'):
        prompts = extract_prompts_from_markdown(mkd_file)
        for prompt_data in prompts:
            category = categorize_l1b3rt4s_prompt(prompt_data)
            if category not in prompts_by_category:
                prompts_by_category[category] = []
            prompts_by_category[category].append(prompt_data)
    
    # Process #MOTHERLOAD.txt
    motherload_file = l1b3rt4s_dir / '#MOTHERLOAD.txt'
    if motherload_file.exists():
        prompts = extract_prompts_from_markdown(motherload_file)
        for prompt_data in prompts:
            category = categorize_l1b3rt4s_prompt(prompt_data)
            if category not in prompts_by_category:
                prompts_by_category[category] = []
            prompts_by_category[category].append(prompt_data)
    
    return prompts_by_category


def format_for_payloads_json(prompts_by_category: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Format extracted prompts for advanced_payloads.json structure."""
    output = {}
    
    for category, prompts in prompts_by_category.items():
        output[category] = {
            'description': f'L1B3RT4S prompts for {category}',
            'severity': 'high',
            'source': 'L1B3RT4S (Elder Plinius)',
            'authors': ['Elder Plinius'],
            'templates': []
        }
        
        for prompt_data in prompts:
            # Add {original_prompt} placeholder if not present (Comment 2 fix)
            prompt_text = prompt_data['prompt']
            if '{original_prompt}' not in prompt_text:
                prompt_text = f"{prompt_text} {{original_prompt}}"
            
            output[category]['templates'].append(prompt_text)
    
    return output


if __name__ == '__main__':
    base_path = Path(__file__).parent.parent.parent
    
    print("Extracting L1B3RT4S prompts...")
    prompts_by_category = extract_all_l1b3rt4s_prompts(base_path)
    
    print(f"Found {sum(len(p) for p in prompts_by_category.values())} prompts in {len(prompts_by_category)} categories")
    
    formatted = format_for_payloads_json(prompts_by_category)
    
    # Output to JSON
    output_path = base_path / 'backend' / 'data' / 'l1b3rt4s_extracted.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted prompts written to {output_path}")
    
    # Print summary
    for category, prompts in prompts_by_category.items():
        print(f"  {category}: {len(prompts)} prompts")
