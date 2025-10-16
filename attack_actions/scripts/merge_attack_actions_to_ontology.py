#!/usr/bin/env python3
"""
CSRO Attack Action Merger

Merges generated AttackAction instances into the main CSRO ontology file.
Preserves existing instances and only adds new ones from the generated file.

Usage:
    python merge_attack_actions_to_ontology.py
    python merge_attack_actions_to_ontology.py --ontology ../../csro.ttl --actions ../configs/generated_attack_actions.ttl
"""

import argparse
import sys
import re
from pathlib import Path


def extract_instance_names(content: str, instance_type: str) -> set:
    """Extract all instance names of a specific type from content."""
    # Match both formats:
    # 1. "csro:InstanceName rdf:type owl:NamedIndividual , csro:InstanceType"
    # 2. "csro:InstanceName a csro:InstanceType"
    # Use word boundaries (\b) and more specific patterns to avoid matching:
    # - Class definitions (csro:Risk rdf:type owl:Class)
    # - Property domains/ranges (rdfs:domain csro:Risk)
    # - Words containing the instance_type as substring (RiskLevel, RiskTreatment)
    
    # Pattern 1: Match "csro:Name rdf:type owl:NamedIndividual , csro:Type ;"
    # This ensures we match instances, not classes
    pattern1 = rf'csro:(\w+)\s+rdf:type\s+owl:NamedIndividual\s*,\s*csro:{instance_type}\s*[;\.]'
    
    # Pattern 2: Match "csro:Name a csro:Type ;" (Turtle shorthand)
    # Use word boundary after instance_type to avoid substring matches
    pattern2 = rf'csro:(\w+)\s+a\s+csro:{instance_type}\b\s*[;\.]'
    
    matches1 = re.findall(pattern1, content)
    matches2 = re.findall(pattern2, content)
    
    return set(matches1 + matches2)


def extract_instance_block(content: str, instance_name: str) -> str:
    """Extract a complete instance block including all its properties."""
    lines = content.split('\n')
    instance_block = []
    in_instance = False
    
    for i, line in enumerate(lines):
        # Start of the instance definition
        if f'csro:{instance_name}' in line and ('rdf:type' in line or ' a csro:' in line):
            in_instance = True
            # Add comment marker before instance if it exists
            if i > 0 and lines[i-1].startswith('###'):
                instance_block.append(lines[i-1])
            instance_block.append(line)
            continue
        
        # Collect instance property lines
        if in_instance:
            instance_block.append(line)
            # End of instance definition (line ends with period)
            if line.strip().endswith('.'):
                break
    
    return '\n'.join(instance_block)


def merge_instances_to_ontology(ontology_path: str, instances_path: str, backup: bool = True):
    """
    Merge generated instances into the main ontology file.
    Preserves existing instances and only adds new ones.
    
    Args:
        ontology_path: Path to the main csro.ttl file
        instances_path: Path to the generated instances file
        backup: Whether to create a backup of the original ontology
    """
    ontology_file = Path(ontology_path)
    instances_file = Path(instances_path)
    
    # Validate files exist
    if not ontology_file.exists():
        print(f"ERROR: Ontology file not found: {ontology_path}")
        sys.exit(1)
    
    if not instances_file.exists():
        print(f"ERROR: Generated instances file not found: {instances_path}")
        sys.exit(1)
    
    print(f"Reading ontology from: {ontology_path}")
    with open(ontology_file, 'r', encoding='utf-8') as f:
        ontology_content = f.read()
    
    print(f"Reading generated instances from: {instances_path}")
    with open(instances_file, 'r', encoding='utf-8') as f:
        instances_content = f.read()
    
    # Extract instance names by type
    existing_actions = extract_instance_names(ontology_content, 'AttackAction')
    existing_impacts = extract_instance_names(ontology_content, 'Impact')
    existing_risks = extract_instance_names(ontology_content, 'Risk')
    
    new_actions = extract_instance_names(instances_content, 'AttackAction')
    new_impacts = extract_instance_names(instances_content, 'Impact')
    new_risks = extract_instance_names(instances_content, 'Risk')
    
    print(f"\nExisting instances in ontology:")
    print(f"  - {len(existing_actions)} AttackAction instances")
    print(f"  - {len(existing_impacts)} Impact instances")
    print(f"  - {len(existing_risks)} Risk instances")
    
    print(f"\nNew instances in generated file:")
    print(f"  - {len(new_actions)} AttackAction instances")
    print(f"  - {len(new_impacts)} Impact instances")
    print(f"  - {len(new_risks)} Risk instances")
    
    # Determine which instances to add
    actions_to_add = new_actions - existing_actions
    impacts_to_add = new_impacts - existing_impacts
    risks_to_add = new_risks - existing_risks
    
    actions_to_skip = new_actions & existing_actions
    impacts_to_skip = new_impacts & existing_impacts
    risks_to_skip = new_risks & existing_risks
    
    if actions_to_skip:
        print(f"\nSkipping {len(actions_to_skip)} AttackActions (already exist)")
    if impacts_to_skip:
        print(f"Skipping {len(impacts_to_skip)} Impacts (already exist)")
    if risks_to_skip:
        print(f"Skipping {len(risks_to_skip)} Risks (already exist)")
    
    if not (actions_to_add or impacts_to_add or risks_to_add):
        print("\n" + "="*80)
        print("NO NEW INSTANCES TO ADD")
        print("="*80)
        print("All instances in the generated file already exist in the ontology.")
        print("No changes made.")
        return
    
    print(f"\nWill add:")
    print(f"  + {len(actions_to_add)} new AttackAction instances")
    print(f"  + {len(impacts_to_add)} new Impact instances")
    print(f"  + {len(risks_to_add)} new Risk instances")
    
    # Create backup if requested
    if backup:
        backup_path = ontology_file.with_suffix('.ttl.backup')
        print(f"\nCreating backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(ontology_content)
    
    # Extract blocks for new instances
    print("\nExtracting new instance blocks...")
    
    new_action_blocks = []
    for action_name in sorted(actions_to_add):
        block = extract_instance_block(instances_content, action_name)
        if block.strip():
            new_action_blocks.append(block)
    print(f"  ✓ Extracted {len(new_action_blocks)} AttackAction blocks")
    
    new_impact_blocks = []
    for impact_name in sorted(impacts_to_add):
        block = extract_instance_block(instances_content, impact_name)
        if block.strip():
            new_impact_blocks.append(block)
    print(f"  ✓ Extracted {len(new_impact_blocks)} Impact blocks")
    
    new_risk_blocks = []
    for risk_name in sorted(risks_to_add):
        block = extract_instance_block(instances_content, risk_name)
        if block.strip():
            new_risk_blocks.append(block)
    print(f"  ✓ Extracted {len(new_risk_blocks)} Risk blocks")
    
    if not (new_action_blocks or new_impact_blocks or new_risk_blocks):
        print("\nERROR: Could not extract instance blocks from generated file.")
        sys.exit(1)
    
    # Find appropriate insertion points in the ontology
    lines = ontology_content.split('\n')
    
    # Find end of file (before any trailing comments)
    insertion_point = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() and not lines[i].strip().startswith('#'):
            insertion_point = i + 1
            break
    
    print(f"\nInserting at line {insertion_point}...")
    
    # Build merged content
    before_insertion = '\n'.join(lines[:insertion_point])
    after_insertion = '\n'.join(lines[insertion_point:]) if insertion_point < len(lines) else ''
    
    merged_content = before_insertion.rstrip() + '\n\n'
    
    # Add new instances by type
    if new_impact_blocks:
        merged_content += "###  Impact Instances\n\n"
        for block in new_impact_blocks:
            merged_content += block + '\n\n'
    
    if new_risk_blocks:
        merged_content += "###  Risk Instances\n\n"
        for block in new_risk_blocks:
            merged_content += block + '\n\n'
    
    if new_action_blocks:
        merged_content += "###  AttackAction Instances\n\n"
        for block in new_action_blocks:
            merged_content += block + '\n\n'
    
    # Add remaining content
    if after_insertion.strip():
        merged_content += after_insertion.lstrip()
    
    # Write the merged content
    print(f"Writing merged ontology to: {ontology_path}")
    with open(ontology_file, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    print("\n" + "="*80)
    print("MERGE SUMMARY")
    print("="*80)
    print(f"✓ Successfully merged instances into {ontology_path}")
    print(f"✓ Added {len(actions_to_add)} new AttackAction instances")
    print(f"✓ Added {len(impacts_to_add)} new Impact instances")
    print(f"✓ Added {len(risks_to_add)} new Risk instances")
    if backup:
        print(f"✓ Backup saved to: {backup_path}")
    else:
        print("✓ No backup created")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Merge generated AttackAction instances into CSRO ontology',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--ontology',
        default='../../csro.ttl',
        help='Path to CSRO ontology file (default: ../../csro.ttl)'
    )
    parser.add_argument(
        '--actions',
        default='../configs/generated_attack_actions.ttl',
        help='Path to generated instances file (default: ../configs/generated_attack_actions.ttl)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create a backup of the original ontology'
    )
    
    args = parser.parse_args()
    
    merge_instances_to_ontology(
        ontology_path=args.ontology,
        instances_path=args.actions,
        backup=not args.no_backup
    )


if __name__ == "__main__":
    main()
