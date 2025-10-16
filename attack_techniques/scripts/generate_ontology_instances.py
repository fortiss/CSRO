"""
Generate AssumptionWeight instances and CalculationRule instances for CSRO ontology
from the assumption_weights_rationales.csv file. Can also generate ContainerAttackTechnique
instances with rdfs:label properties.
"""

import csv
import re
from collections import defaultdict

# File paths
RATIONALES_CSV = '../weights/assumption_weights_rationales.csv'
OUTPUT_FILE = '../weights/generated_ontology_instances.ttl'

def safe_id(text):
    """Convert text to a safe identifier by replacing special characters."""
    return text.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace('/', '_')

def escape_ttl_string(text):
    """Escape special characters in TTL strings."""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def generate_weight_instance(technique, assumption_id, weight_type, value, rationale):
    """Generate a single AssumptionWeight instance in Turtle format."""
    # Create unique ID for this weight
    weight_id = f"{technique}_{weight_type}_{assumption_id}_Weight"
    
    # Escape the rationale for TTL format
    escaped_rationale = escape_ttl_string(rationale)
    
    # Generate the instance
    ttl = f"""
###  https://w3id.org/csro/ontology#{weight_id}
csro:{weight_id} rdf:type owl:NamedIndividual ,
                         csro:AssumptionWeight ;
                csro:refersToAssumption csro:{assumption_id.replace('-', '_')} ;
                csro:weightValue {value}.0 ;
                csro:effectDescription "{escaped_rationale}" .
"""
    return weight_id, ttl

def generate_calculation_rule(technique, weight_type, weight_ids):
    """Generate an ExploitabilityCalculationRule or ExposureCalculationRule instance."""
    rule_class = f"{weight_type}CalculationRule"
    rule_id = f"{technique}{weight_type}Rule"
    
    # Create the hasWeight list
    weight_refs = ' ,\n                           '.join([f"csro:{wid}" for wid in sorted(weight_ids)])
    
    ttl = f"""
###  https://w3id.org/csro/ontology#{rule_id}
csro:{rule_id} rdf:type owl:NamedIndividual ,
                        csro:{rule_class} ;
               csro:appliesTo csro:{technique} ;
               csro:hasWeight {weight_refs} ;
               csro:description "Calculation rule for {weight_type.lower()} rating of {technique} attack technique" .
"""
    return ttl

def generate_technique_label(technique_name: str) -> str:
    """Generate a human-readable label for a technique."""
    # Remove 'Container' prefix if present
    if technique_name.startswith('Container'):
        technique_name = technique_name[9:]  # Remove 'Container'
    
    # Convert CamelCase to space-separated words
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', technique_name)
    return f"Container {spaced}"

def generate_technique_instance(technique_name: str, description: str = None) -> str:
    """Generate a ContainerAttackTechnique instance with rdfs:label."""
    label = generate_technique_label(technique_name)
    
    # Basic template - can be expanded with more properties
    ttl = f"""
###  https://w3id.org/csro/ontology#{technique_name}
csro:{technique_name} rdf:type owl:NamedIndividual ,
                             csro:ContainerAttackTechnique ;
                     rdfs:label "{label}" ;"""
    
    if description:
        escaped_desc = escape_ttl_string(description)
        ttl += f'\n                     csro:description "{escaped_desc}" ;'
    
    ttl += "\n                     .\n"
    return ttl

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate ontology instances for CSRO',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--include-technique-templates',
        action='store_true',
        help='Generate ContainerAttackTechnique templates with labels'
    )
    parser.add_argument(
        '--rationales',
        default=RATIONALES_CSV,
        help=f'Path to rationales CSV file (default: {RATIONALES_CSV})'
    )
    parser.add_argument(
        '--output',
        default=OUTPUT_FILE,
        help=f'Output file path (default: {OUTPUT_FILE})'
    )
    
    args = parser.parse_args()
    
    print("Loading rationales CSV...")
    
    # Data structures to organize the information
    weights_by_technique = defaultdict(lambda: {'Exploitability': [], 'Exposure': []})
    weight_instances = []
    techniques_found = set()
    
    # Read the CSV and generate weight instances
    with open(args.rationales, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            technique = row['Technique']
            assumption_id = row['Assumption ID']
            weight_type = row['Weight Type']
            value = row['Value']
            rationale = row['Rationale']
            
            # Track unique techniques
            techniques_found.add(technique)
            
            # Generate weight instance
            weight_id, weight_ttl = generate_weight_instance(
                technique, assumption_id, weight_type, value, rationale
            )
            
            weight_instances.append(weight_ttl)
            weights_by_technique[technique][weight_type].append(weight_id)
    
    print(f"Generated {len(weight_instances)} AssumptionWeight instances")
    
    # Generate calculation rules
    calculation_rules = []
    for technique, weight_types in sorted(weights_by_technique.items()):
        # Generate Exploitability rule
        if weight_types['Exploitability']:
            rule_ttl = generate_calculation_rule(
                technique, 'Exploitability', weight_types['Exploitability']
            )
            calculation_rules.append(rule_ttl)
        
        # Generate Exposure rule
        if weight_types['Exposure']:
            rule_ttl = generate_calculation_rule(
                technique, 'Exposure', weight_types['Exposure']
            )
            calculation_rules.append(rule_ttl)
    
    print(f"Generated {len(calculation_rules)} CalculationRule instances")
    
    # Generate technique templates if requested
    technique_templates = []
    if args.include_technique_templates:
        print(f"Generating ContainerAttackTechnique templates...")
        for technique in sorted(techniques_found):
            template = generate_technique_instance(technique)
            technique_templates.append(template)
        print(f"Generated {len(technique_templates)} technique templates")
    
    # Write output file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("@prefix csro: <https://w3id.org/csro/ontology#> .\n")
        f.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n")
        f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
        f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")
        
        # Write technique templates if generated
        if technique_templates:
            f.write("#" * 80 + "\n")
            f.write("#    ContainerAttackTechnique Templates (with labels)\n")
            f.write("#" * 80 + "\n")
            for template in technique_templates:
                f.write(template)
        
        f.write("#" * 80 + "\n")
        f.write("#    AssumptionWeight Individuals\n")
        f.write("#" * 80 + "\n")
        
        # Write all weight instances
        for weight_ttl in weight_instances:
            f.write(weight_ttl)
        
        f.write("\n" + "#" * 80 + "\n")
        f.write("#    CalculationRule Individuals\n")
        f.write("#" * 80 + "\n")
        
        # Write all calculation rules
        for rule_ttl in calculation_rules:
            f.write(rule_ttl)
    
    print(f"\n✅ Successfully generated {args.output}")
    if technique_templates:
        print(f"   - {len(technique_templates)} ContainerAttackTechnique templates")
    print(f"   - {len(weight_instances)} AssumptionWeight instances")
    print(f"   - {len(calculation_rules)} CalculationRule instances")
    print(f"\nNext steps:")
    print(f"1. Review the generated file: {args.output}")
    if technique_templates:
        print(f"2. Use merge_technique_labels.py to add labels to existing techniques in csro.ttl")
        print(f"3. Or manually merge technique templates into csro.ttl")
    else:
        print(f"2. Insert the content into csro.ttl at the appropriate location")
    print(f"3. Validate the ontology with a reasoner")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY BY TECHNIQUE")
    print("=" * 80)
    for technique in sorted(weights_by_technique.keys()):
        exp_count = len(weights_by_technique[technique]['Exploitability'])
        exp_count = len(weights_by_technique[technique]['Exposure'])
        print(f"{technique}:")
        print(f"  - Exploitability weights: {exp_count}")
        print(f"  - Exposure weights: {exp_count}")
        if args.include_technique_templates:
            label = generate_technique_label(technique)
            print(f"  - Generated label: '{label}'")

if __name__ == '__main__':
    main()
