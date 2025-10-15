#!/usr/bin/env python3
"""
CSRO Scenario Merger

Merges generated ContextScenario instances into the main CSRO ontology file.
This script preserves existing scenarios and only adds new ones from the generated file.

Usage:
    python merge_scenarios_to_ontology.py
    python merge_scenarios_to_ontology.py --ontology ../../csro.ttl --scenarios ../configs/generated_scenarios.ttl
"""

import argparse
import sys
import re
from pathlib import Path


def extract_scenario_names(content: str) -> set:
    """Extract all scenario names from content."""
    # Match both formats:
    # 1. "csro:ScenarioName rdf:type owl:NamedIndividual , csro:ContextScenario"
    # 2. "csro:ScenarioName a csro:ContextScenario"
    pattern1 = r'csro:(\w+Scenario)\s+rdf:type\s+owl:NamedIndividual\s*,\s*csro:ContextScenario'
    pattern2 = r'csro:(\w+Scenario)\s+a\s+csro:ContextScenario'
    
    matches1 = re.findall(pattern1, content)
    matches2 = re.findall(pattern2, content)
    
    return set(matches1 + matches2)


def extract_scenario_definition(content: str, scenario_name: str) -> str:
    """Extract just the scenario definition (not the AssumptionInScenario instances)."""
    lines = content.split('\n')
    scenario_block = []
    in_scenario = False
    
    for i, line in enumerate(lines):
        # Start of the scenario definition (both formats)
        if f'csro:{scenario_name}' in line and ('rdf:type owl:NamedIndividual' in line or f'a csro:ContextScenario' in line):
            in_scenario = True
            # Add comment marker before scenario if it exists
            if i > 0 and lines[i-1].startswith('###'):
                scenario_block.append(lines[i-1])
            scenario_block.append(line)
            continue
        
        # Collect scenario definition lines
        if in_scenario:
            scenario_block.append(line)
            # End of scenario definition (line ends with period)
            if line.strip().endswith('.'):
                break
    
    return '\n'.join(scenario_block)


def extract_assumption_instances(content: str, scenario_names: set) -> str:
    """Extract all AssumptionInScenario instances for the given scenarios."""
    lines = content.split('\n')
    assumption_blocks = []
    current_block = []
    in_assumption = False
    current_scenario = None
    
    for i, line in enumerate(lines):
        # Check if this line starts an AssumptionInScenario for one of our scenarios
        for scenario_name in scenario_names:
            if f'csro:{scenario_name}_' in line and 'a csro:AssumptionInScenario' in line:
                # Save previous block if any
                if current_block:
                    assumption_blocks.append('\n'.join(current_block))
                # Start new block
                current_block = [line]
                in_assumption = True
                current_scenario = scenario_name
                break
        else:
            # Not starting a new assumption
            if in_assumption:
                # Continue collecting lines for current assumption
                if line.strip() and not line.startswith('csro:'):
                    # This is a property line (forAssumption, hasSatisfactionState)
                    current_block.append(line)
                elif line.strip().endswith('.'):
                    # End of current assumption
                    current_block.append(line)
                    assumption_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_assumption = False
                    current_scenario = None
                elif not line.strip():
                    # Empty line, might be end of assumption or just whitespace
                    if current_block and current_block[-1].strip().endswith('.'):
                        assumption_blocks.append('\n'.join(current_block))
                        current_block = []
                        in_assumption = False
                        current_scenario = None
    
    # Add last block if any
    if current_block:
        assumption_blocks.append('\n'.join(current_block))
    
    return '\n\n'.join(assumption_blocks)


def merge_scenarios_to_ontology(ontology_path: str, scenarios_path: str, backup: bool = True):
    """
    Merge generated scenario instances into the main ontology file.
    Preserves existing scenarios and only adds new ones.
    
    Args:
        ontology_path: Path to the main csro.ttl file
        scenarios_path: Path to the generated scenarios file
        backup: Whether to create a backup of the original ontology
    """
    ontology_file = Path(ontology_path)
    scenarios_file = Path(scenarios_path)
    
    # Validate files exist
    if not ontology_file.exists():
        print(f"ERROR: Ontology file not found: {ontology_path}")
        sys.exit(1)
    
    if not scenarios_file.exists():
        print(f"ERROR: Scenarios file not found: {scenarios_path}")
        sys.exit(1)
    
    print(f"Reading ontology from: {ontology_path}")
    with open(ontology_file, 'r', encoding='utf-8') as f:
        ontology_content = f.read()
    
    print(f"Reading generated scenarios from: {scenarios_path}")
    with open(scenarios_file, 'r', encoding='utf-8') as f:
        scenarios_content = f.read()
    
    # Extract scenario names from both files
    existing_scenarios = extract_scenario_names(ontology_content)
    new_scenarios = extract_scenario_names(scenarios_content)
    
    print(f"\nFound {len(existing_scenarios)} existing scenarios in ontology:")
    for scenario in sorted(existing_scenarios):
        print(f"  - {scenario}")
    
    print(f"\nFound {len(new_scenarios)} scenarios in generated file:")
    for scenario in sorted(new_scenarios):
        print(f"  - {scenario}")
    
    # Determine which scenarios to add
    scenarios_to_add = new_scenarios - existing_scenarios
    scenarios_to_preserve = existing_scenarios - new_scenarios
    scenarios_already_exist = new_scenarios & existing_scenarios
    
    # Check if AssumptionInScenario instances exist for scenarios that are already in the ontology
    print("\nChecking for AssumptionInScenario instances in ontology...")
    scenarios_missing_assumptions = set()
    for scenario_name in scenarios_already_exist:
        # Check if at least one AssumptionInScenario instance DEFINITION exists for this scenario
        # Look for pattern like "csro:ScenarioName_AUTH_1 a csro:AssumptionInScenario" or "rdf:type owl:NamedIndividual , csro:AssumptionInScenario"
        assumption_def_pattern1 = f'csro:{scenario_name}_AUTH_1 a csro:AssumptionInScenario'
        assumption_def_pattern2 = f'csro:{scenario_name}_AUTH_1 rdf:type owl:NamedIndividual'
        
        if assumption_def_pattern1 in ontology_content or assumption_def_pattern2 in ontology_content:
            print(f"  ✓ {scenario_name}: Has AssumptionInScenario instances")
        else:
            scenarios_missing_assumptions.add(scenario_name)
            print(f"  ⚠ {scenario_name}: Missing AssumptionInScenario instances")
    
    if scenarios_missing_assumptions:
        print(f"\n⚠ Found {len(scenarios_missing_assumptions)} scenarios with missing AssumptionInScenario instances")
        print("These will be added even though scenario definitions exist.")
        # Add scenarios with missing assumptions to the scenarios_to_add list
        scenarios_to_add = scenarios_to_add.union(scenarios_missing_assumptions)
        scenarios_already_exist = scenarios_already_exist - scenarios_missing_assumptions
    
    if scenarios_already_exist:
        print(f"\nSkipping {len(scenarios_already_exist)} scenarios (already complete):")
        for scenario in sorted(scenarios_already_exist):
            print(f"  - {scenario}")
    
    if not scenarios_to_add:
        print("\n" + "="*80)
        print("NO NEW CONTENT TO ADD")
        print("="*80)
        print("All scenarios and their AssumptionInScenario instances already exist.")
        print("No changes made.")
        return
    
    print(f"\nWill add {len(scenarios_to_add)} new scenarios:")
    for scenario in sorted(scenarios_to_add):
        print(f"  + {scenario}")
    
    # Create backup if requested
    if backup:
        backup_path = ontology_file.with_suffix('.ttl.backup')
        print(f"\nCreating backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(ontology_content)
    
    # Separate scenarios that need definitions from those that just need assumptions
    scenarios_needing_definitions = scenarios_to_add - scenarios_missing_assumptions if 'scenarios_missing_assumptions' in dir() else scenarios_to_add
    scenarios_needing_only_assumptions = scenarios_missing_assumptions if 'scenarios_missing_assumptions' in dir() else set()
    
    # Extract definitions only for scenarios that don't have them
    new_scenario_definitions = []
    if scenarios_needing_definitions:
        print("\nExtracting new scenario definitions...")
        for scenario_name in sorted(scenarios_needing_definitions):
            definition = extract_scenario_definition(scenarios_content, scenario_name)
            if definition.strip():
                new_scenario_definitions.append(definition)
                print(f"  ✓ Extracted {scenario_name} definition")
    
    # Extract AssumptionInScenario instances for ALL scenarios being added
    print("\nExtracting AssumptionInScenario instances...")
    new_assumptions = extract_assumption_instances(scenarios_content, scenarios_to_add)
    assumption_count = new_assumptions.count('a csro:AssumptionInScenario')
    print(f"  ✓ Extracted {assumption_count} AssumptionInScenario instances")
    
    if not new_scenario_definitions and not scenarios_needing_only_assumptions:
        print("\nERROR: Could not extract scenario definitions from generated file.")
        sys.exit(1)
    
    if not new_assumptions.strip():
        print("\nWARNING: No AssumptionInScenario instances found for scenarios.")
        print("Risk calculations will not work properly without these instances!")
    
    # Find the ContextScenario section in the ontology
    lines = ontology_content.split('\n')
    scenario_section_start = None
    
    # Find existing scenario section
    for i, line in enumerate(lines):
        if 'ContextScenario' in line and ('###' in line or '##' in line):
            scenario_section_start = i
            break
    
    # If no section found, look for the first ContextScenario instance
    if scenario_section_start is None:
        for i, line in enumerate(lines):
            if 'csro:ContextScenario' in line and 'rdf:type' in lines[i-1] if i > 0 else False:
                scenario_section_start = i - 2  # Include the ### comment before it
                break
    
    if scenario_section_start is None:
        print("\nERROR: Could not find ContextScenario section in ontology.")
        print("Please ensure the ontology contains at least one ContextScenario instance.")
        sys.exit(1)
    
    print(f"\nFound ContextScenario section at line {scenario_section_start}")
    
    # Find the end of the ContextScenario section (next major section or end of file)
    scenario_section_end = len(lines)
    for i in range(scenario_section_start + 1, len(lines)):
        line = lines[i]
        # Look for next major section that's not a scenario
        if line.startswith('###') and 'Scenario' not in line:
            scenario_section_end = i
            break
    
    print(f"ContextScenario section ends at line {scenario_section_end}")
    
    # Insert new scenarios at the end of the section
    print(f"\nInserting {len(new_scenario_definitions)} new scenario definitions...")
    
    # Build merged content
    before_insertion = '\n'.join(lines[:scenario_section_end])
    after_insertion = '\n'.join(lines[scenario_section_end:]) if scenario_section_end < len(lines) else ''
    
    # Combine
    merged_content = before_insertion.rstrip() + '\n\n'
    
    # Add new scenario definitions
    for definition in new_scenario_definitions:
        merged_content += definition + '\n\n'
    
    # Add AssumptionInScenario instances
    if new_assumptions.strip():
        print(f"Inserting {assumption_count} AssumptionInScenario instances...")
        merged_content += new_assumptions + '\n\n'
    
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
    print(f"✓ Successfully merged scenario instances into {ontology_path}")
    print(f"✓ Preserved {len(scenarios_to_preserve)} existing scenarios")
    print(f"✓ Added {len(scenarios_to_add)} new ContextScenario instances:")
    for scenario in sorted(scenarios_to_add):
        print(f"    + {scenario}")
    print(f"✓ Added {assumption_count} new AssumptionInScenario instances")
    if backup:
        print(f"✓ Backup saved to: {backup_path}")
    else:
        print("✓ No backup created")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Merge generated scenario instances into CSRO ontology',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--ontology',
        default='../../csro.ttl',
        help='Path to CSRO ontology file (default: ../../csro.ttl)'
    )
    parser.add_argument(
        '--scenarios',
        default='../configs/generated_scenarios.ttl',
        help='Path to generated scenarios file (default: ../configs/generated_scenarios.ttl)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create a backup of the original ontology'
    )
    
    args = parser.parse_args()
    
    merge_scenarios_to_ontology(
        ontology_path=args.ontology,
        scenarios_path=args.scenarios,
        backup=not args.no_backup
    )


if __name__ == "__main__":
    main()
