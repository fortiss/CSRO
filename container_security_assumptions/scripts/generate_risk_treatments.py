#!/usr/bin/env python3
"""
Generate RiskTreatment instances from container security assumptions CSV.

This script reads the container_security_assumptions.csv file and generates
RiskTreatment individuals with appropriate relationships to ContainerSecurityAssumption
instances.

Usage:
    python generate_risk_treatments.py [--output OUTPUT_FILE]

Example:
    python generate_risk_treatments.py
    python generate_risk_treatments.py --output ../configs/generated_risk_treatments.ttl
"""

import csv
import argparse
from pathlib import Path
from typing import List, Dict


def read_assumptions_csv(csv_path: Path) -> List[Dict[str, str]]:
    """Read assumptions and treatments from CSV file."""
    assumptions = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:  # Handle BOM
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Strip whitespace from keys
            cleaned_row = {k.strip(): v for k, v in row.items()}
            assumptions.append(cleaned_row)
    return assumptions


def generate_treatment_ttl(assumption: Dict[str, str]) -> str:
    """Generate Turtle RDF for a single RiskTreatment instance."""
    assumption_id = assumption['Assumption ID']
    treatment_id = assumption['Treatment ID']
    treatment_desc = assumption['Treatment Description']
    
    # Create the treatment label from the ID (add spaces before capitals)
    label = ''.join([' ' + c if c.isupper() else c for c in treatment_id]).strip()
    
    ttl = f"""###  https://w3id.org/csro/ontology#{treatment_id}
csro:{treatment_id} rdf:type owl:NamedIndividual ,
                             csro:RiskTreatment ;
                    csro:addresses csro:{assumption_id.replace('-', '_')} ;
                    csro:description "{treatment_desc}" ;
                    rdfs:label "{label}" .

"""
    return ttl


def generate_header() -> str:
    """Generate the TTL file header."""
    return """@prefix : <https://w3id.org/csro/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix csro: <https://w3id.org/csro/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <https://w3id.org/csro/ontology#> .

################################################################################
#    RiskTreatment Individuals (Generated from container_security_assumptions.csv)
################################################################################

"""


def main():
    parser = argparse.ArgumentParser(
        description='Generate RiskTreatment instances from security assumptions CSV'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=Path,
        default=Path(__file__).parent.parent / 'configs' / 'generated_risk_treatments.ttl',
        help='Output TTL file path (default: ../configs/generated_risk_treatments.ttl)'
    )
    parser.add_argument(
        '--csv',
        '-c',
        type=Path,
        default=Path(__file__).parent.parent / 'container_security_assumptions.csv',
        help='Input CSV file path (default: ../container_security_assumptions.csv)'
    )
    
    args = parser.parse_args()
    
    # Read CSV
    print(f"Reading assumptions from {args.csv}...")
    assumptions = read_assumptions_csv(args.csv)
    print(f"Found {len(assumptions)} assumptions")
    
    # Generate TTL
    print(f"\nGenerating RiskTreatment instances...")
    output_content = generate_header()
    
    for assumption in assumptions:
        output_content += generate_treatment_ttl(assumption)
    
    # Write output
    print(f"\nWriting output to {args.output}...")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\n✓ Successfully generated {len(assumptions)} RiskTreatment instances")
    print(f"✓ Output written to: {args.output}")
    
    # Summary
    print(f"\nSummary:")
    print(f"  Total treatments: {len(assumptions)}")
    
    # Count by category
    categories = {}
    for assumption in assumptions:
        cat = assumption['Security Assumption Category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n  By category:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat}: {count}")


if __name__ == '__main__':
    main()
