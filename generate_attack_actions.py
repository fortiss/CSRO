#!/usr/bin/env python3
"""
CSRO AttackAction Generator

Automatically generates AttackAction instances for all technique-scenario combinations.

Usage:
    python generate_attack_actions.py --ontology csro.ttl --output attack_actions.ttl
"""

import argparse
from rdflib import Graph, Namespace, URIRef, Literal, RDF

CSRO = Namespace("https://w3id.org/csro/ontology#")


def generate_attack_actions(ontology_path: str, output_path: str):
    """Generate AttackAction instances for all technique-scenario combinations."""
    
    # Load ontology
    g = Graph()
    g.bind("csro", CSRO)
    g.parse(ontology_path, format="turtle")
    print(f"Loaded ontology from {ontology_path}")
    
    # Get all attack techniques
    techniques = list(g.subjects(RDF.type, CSRO.ContainerAttackTechnique))
    print(f"Found {len(techniques)} attack techniques")
    
    # Get all scenarios
    scenarios = list(g.subjects(RDF.type, CSRO.ContextScenario))
    print(f"Found {len(scenarios)} scenarios")
    
    # Create output graph
    output_g = Graph()
    output_g.bind("csro", CSRO)
    
    # Generate AttackActions
    count = 0
    for technique in techniques:
        technique_name = str(technique).split('#')[-1]
        
        for scenario in scenarios:
            scenario_name = str(scenario).split('#')[-1]
            
            # Create AttackAction instance
            action_name = f"{technique_name}Attack_{scenario_name}"
            action_uri = CSRO[action_name]
            
            # Check if already exists
            existing = list(g.subjects(CSRO.appliesTechnique, technique))
            existing = [a for a in existing if (a, CSRO.inContext, scenario) in g]
            
            if existing:
                print(f"  Skipping {action_name} (already exists)")
                continue
            
            # Add triples
            output_g.add((action_uri, RDF.type, CSRO.AttackAction))
            output_g.add((action_uri, CSRO.appliesTechnique, technique))
            output_g.add((action_uri, CSRO.inContext, scenario))
            output_g.add((action_uri, CSRO.description, 
                         Literal(f"{technique_name} attack applied in {scenario_name} scenario")))
            
            # Note: csro:affects and csro:causesImpact need to be added manually
            # as they depend on domain knowledge
            
            count += 1
            print(f"  Generated: {action_name}")
    
    # Save output
    output_g.serialize(destination=output_path, format="turtle")
    print(f"\nGenerated {count} AttackAction instances")
    print(f"Saved to: {output_path}")
    print("\nNOTE: You need to manually add:")
    print("  - csro:affects properties (which components are affected)")
    print("  - csro:causesImpact property (which impact is caused)")


def main():
    parser = argparse.ArgumentParser(description='Generate CSRO AttackAction instances')
    parser.add_argument('--ontology', default='csro.ttl',
                       help='Path to CSRO ontology file (default: csro.ttl)')
    parser.add_argument('--output', default='generated_attack_actions.ttl',
                       help='Output file path (default: generated_attack_actions.ttl)')
    
    args = parser.parse_args()
    
    generate_attack_actions(args.ontology, args.output)


if __name__ == "__main__":
    main()
