#!/usr/bin/env python3
"""
Merge generated RiskTreatment instances into the main ontology file.

This script merges RiskTreatment instances from generated_risk_treatments.ttl
into csro.ttl, preserving existing treatments and their relationships.

For existing treatments:
- Preserves hasGuideline and isImplementedBy relationships
- Only updates the description and addresses if not present

Usage:
    python merge_risk_treatments_to_ontology.py [--ontology ONTOLOGY_FILE] [--treatments TREATMENTS_FILE]

Example:
    python merge_risk_treatments_to_ontology.py
    python merge_risk_treatments_to_ontology.py --ontology ../../csro.ttl
"""

import argparse
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, List, Tuple


def backup_file(file_path: Path) -> Path:
    """Create a backup of the ontology file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.with_suffix(f'.ttl.backup_{timestamp}')
    shutil.copy2(file_path, backup_path)
    return backup_path


def extract_existing_treatments(ontology_content: str) -> Dict[str, Dict[str, any]]:
    """
    Extract existing RiskTreatment instances with their properties.
    
    Returns a dict mapping treatment name to its properties:
    {
        'TreatmentName': {
            'full_definition': '...',  # Complete turtle definition
            'has_guideline': True/False,
            'has_implemented_by': True/False,
            'has_addresses': True/False,
            'start_pos': int,
            'end_pos': int
        }
    }
    """
    existing_treatments = {}
    
    # Pattern to match RiskTreatment individuals
    # Matches from ### to the blank line after the treatment definition
    pattern = r'###\s+https://w3id\.org/csro/ontology#(\w+)\s*\n(csro:\1\s+rdf:type\s+owl:NamedIndividual\s*,\s*csro:RiskTreatment\s*;[^#]*?)(?=\n\n###|\n\n\n|\Z)'
    
    for match in re.finditer(pattern, ontology_content, re.DOTALL | re.MULTILINE):
        treatment_name = match.group(1)
        full_definition = match.group(0)
        treatment_body = match.group(2)
        
        # Check for existing relationships
        has_guideline = 'csro:hasGuideline' in treatment_body
        has_implemented_by = 'csro:isImplementedBy' in treatment_body
        has_addresses = 'csro:addresses' in treatment_body
        
        existing_treatments[treatment_name] = {
            'full_definition': full_definition,
            'has_guideline': has_guideline,
            'has_implemented_by': has_implemented_by,
            'has_addresses': has_addresses,
            'start_pos': match.start(),
            'end_pos': match.end()
        }
    
    return existing_treatments


def parse_generated_treatments(treatments_content: str) -> Dict[str, str]:
    """
    Parse generated RiskTreatment instances.
    
    Returns a dict mapping treatment name to its full definition.
    """
    treatments = {}
    
    # Pattern to match treatment individuals
    pattern = r'###\s+https://w3id\.org/csro/ontology#(\w+)\s*\n(csro:\1\s+rdf:type[^#]+?)(?=\n###|\Z)'
    
    for match in re.finditer(pattern, treatments_content, re.DOTALL):
        treatment_name = match.group(1)
        full_definition = match.group(0).strip()
        treatments[treatment_name] = full_definition
    
    return treatments


def merge_treatment(existing_treatment: Dict[str, any], new_definition: str, treatment_name: str) -> str:
    """
    Merge new treatment definition with existing one, preserving relationships.
    
    If the existing treatment has hasGuideline or isImplementedBy, preserve them.
    Otherwise, use the new definition.
    """
    if not existing_treatment['has_guideline'] and not existing_treatment['has_implemented_by']:
        # No special relationships, use new definition
        return new_definition
    
    # Parse the new definition to extract components
    new_pattern = r'csro:' + treatment_name + r'\s+rdf:type\s+owl:NamedIndividual\s*,\s*csro:RiskTreatment\s*;(.*?)(?=\n###|\Z)'
    new_match = re.search(new_pattern, new_definition, re.DOTALL)
    
    if not new_match:
        # Can't parse new definition, keep existing
        return existing_treatment['full_definition']
    
    new_properties = new_match.group(1).strip()
    
    # Extract existing relationships to preserve
    existing_def = existing_treatment['full_definition']
    
    # Build merged properties list
    properties = []
    
    # Add addresses from new definition if not in existing
    if not existing_treatment['has_addresses']:
        addresses_match = re.search(r'csro:addresses\s+csro:\w+\s*;', new_properties)
        if addresses_match:
            properties.append(addresses_match.group(0))
    else:
        # Keep existing addresses
        addresses_match = re.search(r'csro:addresses\s+csro:\w+\s*;', existing_def)
        if addresses_match:
            properties.append(addresses_match.group(0))
    
    # Preserve existing hasGuideline
    if existing_treatment['has_guideline']:
        guideline_match = re.search(r'csro:hasGuideline\s+csro:\w+\s*;', existing_def)
        if guideline_match:
            properties.append(guideline_match.group(0))
    
    # Preserve existing isImplementedBy
    if existing_treatment['has_implemented_by']:
        impl_match = re.search(r'csro:isImplementedBy\s+[^;]+;', existing_def, re.DOTALL)
        if impl_match:
            properties.append(impl_match.group(0))
    
    # Add description from new definition
    desc_match = re.search(r'csro:description\s+"[^"]+"\s*;', new_properties)
    if desc_match:
        properties.append(desc_match.group(0))
    
    # Add label from new definition
    label_match = re.search(r'rdfs:label\s+"[^"]+"\s*\.', new_properties)
    if label_match:
        properties.append(label_match.group(0))
    
    # Construct merged definition
    merged = f"###  https://w3id.org/csro/ontology#{treatment_name}\n"
    merged += f"csro:{treatment_name} rdf:type owl:NamedIndividual ,\n"
    merged += f"                             csro:RiskTreatment ;\n"
    
    # Add properties with proper indentation
    for i, prop in enumerate(properties):
        if i < len(properties) - 1:
            # Not the last property, ensure it ends with ;
            prop = prop.rstrip().rstrip(';').rstrip('.') + ' ;'
        else:
            # Last property should end with .
            prop = prop.rstrip().rstrip(';').rstrip('.') + ' .'
        merged += f"                    {prop}\n"
    
    merged += "\n"
    return merged


def find_insertion_point(ontology_content: str) -> int:
    """
    Find the best insertion point for new RiskTreatment instances.
    Look for existing RiskTreatment instances or a suitable section.
    """
    # Try to find the last RiskTreatment instance
    risk_treatment_pattern = r'###\s+https://w3id\.org/csro/ontology#\w+\s*\ncsro:\w+\s+rdf:type\s+owl:NamedIndividual\s*,\s*csro:RiskTreatment\s*;[^#]*?(?=\n\n###|\n\n\n)'
    
    matches = list(re.finditer(risk_treatment_pattern, ontology_content, re.DOTALL))
    
    if matches:
        # Insert after the last RiskTreatment
        last_match = matches[-1]
        return last_match.end()
    
    # Fallback: insert before the end of the file
    # Find a good section marker or insert near the end
    return len(ontology_content.rstrip()) + 1


def merge_treatments(ontology_path: Path, treatments_path: Path) -> Tuple[int, int, int]:
    """
    Merge treatments into ontology.
    
    Returns: (new_count, updated_count, skipped_count)
    """
    # Read files
    with open(ontology_path, 'r', encoding='utf-8') as f:
        ontology_content = f.read()
    
    with open(treatments_path, 'r', encoding='utf-8') as f:
        treatments_content = f.read()
    
    # Extract existing and parse new treatments
    existing_treatments = extract_existing_treatments(ontology_content)
    new_treatments = parse_generated_treatments(treatments_content)
    
    print(f"Found {len(existing_treatments)} existing RiskTreatment instances")
    print(f"Parsed {len(new_treatments)} new RiskTreatment definitions")
    
    # Track statistics
    new_count = 0
    updated_count = 0
    skipped_count = 0
    
    # Process treatments
    treatments_to_add = []
    replacements = []  # List of (start, end, new_text) for existing treatments
    
    for treatment_name, new_definition in new_treatments.items():
        if treatment_name in existing_treatments:
            existing = existing_treatments[treatment_name]
            
            if existing['has_guideline'] or existing['has_implemented_by']:
                # Merge, preserving relationships
                merged_def = merge_treatment(existing, new_definition, treatment_name)
                replacements.append((
                    existing['start_pos'],
                    existing['end_pos'],
                    merged_def
                ))
                updated_count += 1
                print(f"  ✓ Updating {treatment_name} (preserving relationships)")
            else:
                # Replace completely
                replacements.append((
                    existing['start_pos'],
                    existing['end_pos'],
                    new_definition + "\n"
                ))
                updated_count += 1
                print(f"  ✓ Updating {treatment_name}")
        else:
            # New treatment
            treatments_to_add.append(new_definition)
            new_count += 1
            print(f"  + Adding new treatment: {treatment_name}")
    
    # Apply replacements (in reverse order to maintain positions)
    modified_content = ontology_content
    for start, end, new_text in sorted(replacements, key=lambda x: x[0], reverse=True):
        modified_content = modified_content[:start] + new_text + modified_content[end:]
    
    # Add new treatments
    if treatments_to_add:
        insertion_point = find_insertion_point(modified_content)
        
        # Ensure proper spacing
        new_section = "\n\n" + "\n".join(treatments_to_add) + "\n"
        
        modified_content = (
            modified_content[:insertion_point] +
            new_section +
            modified_content[insertion_point:]
        )
    
    # Write back
    with open(ontology_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    return new_count, updated_count, skipped_count


def main():
    parser = argparse.ArgumentParser(
        description='Merge RiskTreatment instances into the ontology'
    )
    parser.add_argument(
        '--ontology',
        '-o',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'csro.ttl',
        help='Path to the ontology file (default: ../../csro.ttl)'
    )
    parser.add_argument(
        '--treatments',
        '-t',
        type=Path,
        default=Path(__file__).parent.parent / 'configs' / 'generated_risk_treatments.ttl',
        help='Path to generated treatments file (default: ../configs/generated_risk_treatments.ttl)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating a backup of the ontology file'
    )
    
    args = parser.parse_args()
    
    # Validate files
    if not args.ontology.exists():
        print(f"Error: Ontology file not found: {args.ontology}")
        return 1
    
    if not args.treatments.exists():
        print(f"Error: Treatments file not found: {args.treatments}")
        return 1
    
    # Create backup
    if not args.no_backup:
        print(f"Creating backup of {args.ontology}...")
        backup_path = backup_file(args.ontology)
        print(f"✓ Backup created: {backup_path}")
    
    # Merge treatments
    print(f"\nMerging treatments from {args.treatments}...")
    print(f"Into ontology: {args.ontology}\n")
    
    new_count, updated_count, skipped_count = merge_treatments(
        args.ontology,
        args.treatments
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("Merge Summary:")
    print(f"{'='*60}")
    print(f"  New treatments added:      {new_count}")
    print(f"  Existing treatments updated: {updated_count}")
    print(f"  Treatments skipped:        {skipped_count}")
    print(f"  Total processed:           {new_count + updated_count + skipped_count}")
    print(f"{'='*60}")
    print(f"\n✓ Successfully merged RiskTreatment instances into {args.ontology}")
    
    return 0


if __name__ == '__main__':
    exit(main())
