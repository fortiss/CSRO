#!/usr/bin/env python3
"""
CSRO Attack Technique Label Merger

Merges rdfs:label properties into existing ContainerAttackTechnique instances
in the main CSRO ontology file. This script adds labels to techniques that
don't already have them.

Usage:
    python merge_technique_labels.py
    python merge_technique_labels.py --ontology ../../csro.ttl --backup
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime


def generate_technique_label(technique_name: str) -> str:
    """Generate a human-readable label for a technique."""
    # Remove 'Container' prefix if present
    if technique_name.startswith('Container'):
        technique_name = technique_name[9:]  # Remove 'Container'
    
    # Convert CamelCase to space-separated words
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', technique_name)
    return f"Container {spaced}"


def find_technique_instances(content: str) -> list:
    """Find all ContainerAttackTechnique instances in the content."""
    # Pattern to match technique definitions
    pattern = r'###\s+https://w3id\.org/csro/ontology#(\w+)\s*\ncsro:\1\s+rdf:type\s+owl:NamedIndividual\s*,\s*\n\s*csro:ContainerAttackTechnique\s*;'
    
    matches = re.finditer(pattern, content, re.MULTILINE)
    techniques = []
    
    for match in matches:
        technique_name = match.group(1)
        start_pos = match.start()
        
        # Find the end of this technique definition (next ### or end of file)
        end_pos = len(content)
        next_section = content.find('\n###', start_pos + 1)
        if next_section != -1:
            end_pos = next_section
        
        # Extract the full definition
        definition = content[start_pos:end_pos]
        
        # Check if it already has an rdfs:label
        has_label = 'rdfs:label' in definition
        
        techniques.append({
            'name': technique_name,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'definition': definition,
            'has_label': has_label
        })
    
    return techniques


def add_label_to_technique(definition: str, technique_name: str) -> str:
    """Add rdfs:label to a technique definition if it doesn't have one."""
    lines = definition.split('\n')
    
    # Find the line with the type declaration
    type_line_idx = None
    for i, line in enumerate(lines):
        if 'csro:ContainerAttackTechnique' in line and ';' in line:
            type_line_idx = i
            break
    
    if type_line_idx is None:
        print(f"WARNING: Could not find type declaration for {technique_name}")
        return definition
    
    # Generate the label
    label = generate_technique_label(technique_name)
    label_line = f'                     rdfs:label "{label}" ;'
    
    # Insert the label after the type declaration
    lines.insert(type_line_idx + 1, label_line)
    
    return '\n'.join(lines)


def merge_technique_labels(ontology_path: str, backup: bool = True):
    """
    Add rdfs:label properties to ContainerAttackTechnique instances in the ontology.
    
    Args:
        ontology_path: Path to the main csro.ttl file
        backup: Whether to create a backup of the original ontology
    """
    ontology_file = Path(ontology_path)
    
    # Validate file exists
    if not ontology_file.exists():
        print(f"ERROR: Ontology file not found: {ontology_path}")
        sys.exit(1)
    
    print(f"Reading ontology from: {ontology_path}")
    with open(ontology_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup if requested
    if backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = ontology_file.with_suffix(f'.ttl.backup_{timestamp}')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created backup: {backup_path}")
    
    # Find all technique instances
    techniques = find_technique_instances(content)
    print(f"\nFound {len(techniques)} ContainerAttackTechnique instances")
    
    # Filter techniques that need labels
    techniques_needing_labels = [t for t in techniques if not t['has_label']]
    techniques_with_labels = [t for t in techniques if t['has_label']]
    
    print(f"  - {len(techniques_with_labels)} already have rdfs:label")
    print(f"  - {len(techniques_needing_labels)} need rdfs:label")
    
    if not techniques_needing_labels:
        print("\nAll techniques already have labels. Nothing to do.")
        return
    
    # Process techniques in reverse order (to maintain positions)
    modified_content = content
    offset = 0
    
    for technique in reversed(techniques_needing_labels):
        old_definition = technique['definition']
        new_definition = add_label_to_technique(old_definition, technique['name'])
        
        # Calculate adjusted positions
        start_pos = technique['start_pos'] + offset
        end_pos = technique['end_pos'] + offset
        
        # Replace in content
        modified_content = (
            modified_content[:start_pos] + 
            new_definition + 
            modified_content[end_pos:]
        )
        
        # Update offset for next replacement
        offset += len(new_definition) - len(old_definition)
        
        label = generate_technique_label(technique['name'])
        print(f"  ✓ Added label to {technique['name']}: '{label}'")
    
    # Write the modified content back
    with open(ontology_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"\n✅ Successfully added labels to {len(techniques_needing_labels)} techniques")
    print(f"Updated ontology saved to: {ontology_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Add rdfs:label properties to ContainerAttackTechnique instances',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--ontology',
        default='../../csro.ttl',
        help='Path to CSRO ontology file (default: ../../csro.ttl)'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create a backup of the original ontology file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making modifications'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        
        # Read and analyze file
        with open(args.ontology, 'r', encoding='utf-8') as f:
            content = f.read()
        
        techniques = find_technique_instances(content)
        techniques_needing_labels = [t for t in techniques if not t['has_label']]
        
        print(f"\nWould add labels to {len(techniques_needing_labels)} techniques:")
        for technique in techniques_needing_labels:
            label = generate_technique_label(technique['name'])
            print(f"  - {technique['name']} -> '{label}'")
    else:
        merge_technique_labels(args.ontology, args.backup)


if __name__ == "__main__":
    main()