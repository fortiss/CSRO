#!/usr/bin/env python3
"""
CSRO Attack Technique Generator

This script generates ContainerAttackTechnique instances with rdfs:label properties
for the CSRO ontology based on technique configurations.

Usage:
    python generate_attack_techniques.py --help
    python generate_attack_techniques.py --config config.json --output new_techniques.ttl

Configuration JSON format:
{
  "techniques": [
    {
      "name": "ContainerCgroupDoS",
      "description": "Manipulating cgroup limits to cause denial of service...",
      "difficulty": "Low",
      "attack_technique": "T1499",
      "required_traits": ["host_cgroup"]
    },
    {
      "name": "ContainerKernelModuleLoading",
      "description": "Loading malicious kernel modules...",
      "difficulty": "High",
      "attack_technique": "T1547.006",
      "required_traits": ["cap_add_CAP_SYS_MODULE"]
    }
  ]
}
"""

import argparse
import json
import re
from typing import Dict, List, Optional
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

# Define namespaces
CSRO = Namespace("https://w3id.org/csro/ontology#")
D3F = Namespace("https://d3fend.mitre.org/ontologies/d3fend.owl#")


class AttackTechniqueGenerator:
    """Generate CSRO ContainerAttackTechnique instances programmatically."""
    
    def __init__(self, ontology_path: Optional[str] = None):
        """Initialize the generator, optionally loading existing ontology."""
        self.graph = Graph()
        self.graph.bind("csro", CSRO)
        self.graph.bind("d3f", D3F)
        
        if ontology_path:
            self.graph.parse(ontology_path, format="turtle")
            print(f"Loaded ontology from {ontology_path}")
    
    def _generate_technique_label(self, technique_name: str) -> str:
        """Generate a human-readable label for a technique."""
        # Remove 'Container' prefix if present
        if technique_name.startswith('Container'):
            technique_name = technique_name[9:]  # Remove 'Container'
        
        # Convert CamelCase to space-separated words
        spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', technique_name)
        return f"Container {spaced}"
    
    def generate_technique(self,
                          name: str,
                          description: str,
                          difficulty: str = "Medium",
                          attack_technique: Optional[str] = None,
                          required_traits: Optional[List[str]] = None) -> Graph:
        """
        Generate a new ContainerAttackTechnique instance.
        
        Args:
            name: Technique name (e.g., "ContainerCgroupDoS")
            description: Human-readable description
            difficulty: Base difficulty level (Low, Medium, High)
            attack_technique: MITRE ATT&CK technique ID (e.g., "T1499")
            required_traits: List of required container deployment traits
        
        Returns:
            Graph containing the new technique triples
        """
        technique_graph = Graph()
        technique_graph.bind("csro", CSRO)
        technique_graph.bind("d3f", D3F)
        
        technique_uri = CSRO[name]
        
        # Add technique instance
        technique_graph.add((technique_uri, RDF.type, CSRO.ContainerAttackTechnique))
        technique_graph.add((technique_uri, CSRO.description, Literal(description)))
        
        # Generate and add human-readable label
        label = self._generate_technique_label(name)
        technique_graph.add((technique_uri, RDFS.label, Literal(label)))
        
        # Add base difficulty
        difficulty_uri = CSRO[difficulty]
        technique_graph.add((technique_uri, CSRO.hasBaseDifficulty, difficulty_uri))
        
        # Add ATT&CK technique reference if provided
        if attack_technique:
            attack_uri = D3F[attack_technique]
            technique_graph.add((technique_uri, CSRO.referencesAttackTechnique, attack_uri))
        
        # Add required traits if provided
        if required_traits:
            for trait in required_traits:
                trait_uri = CSRO[trait]
                technique_graph.add((technique_uri, CSRO.requiresTrait, trait_uri))
        
        print(f"Generated technique: {name} -> '{label}'")
        return technique_graph
    
    def generate_from_config(self, config_path: str) -> Graph:
        """Generate multiple techniques from a JSON configuration file."""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        combined_graph = Graph()
        combined_graph.bind("csro", CSRO)
        combined_graph.bind("d3f", D3F)
        
        for technique_config in config.get('techniques', []):
            name = technique_config['name']
            description = technique_config['description']
            difficulty = technique_config.get('difficulty', 'Medium')
            attack_technique = technique_config.get('attack_technique')
            required_traits = technique_config.get('required_traits', [])
            
            technique_graph = self.generate_technique(
                name=name,
                description=description,
                difficulty=difficulty,
                attack_technique=attack_technique,
                required_traits=required_traits
            )
            
            # Merge into combined graph
            for triple in technique_graph:
                combined_graph.add(triple)
        
        return combined_graph
    
    def add_labels_to_existing_techniques(self, ontology_path: str) -> Graph:
        """Add rdfs:label properties to existing ContainerAttackTechnique instances."""
        # Load the ontology
        graph = Graph()
        graph.bind("csro", CSRO)
        graph.parse(ontology_path, format="turtle")
        
        # Query for existing techniques without labels
        query = """
        PREFIX csro: <https://w3id.org/csro/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?technique
        WHERE {
            ?technique a csro:ContainerAttackTechnique .
            FILTER NOT EXISTS { ?technique rdfs:label ?label }
        }
        """
        
        results = graph.query(query)
        techniques_updated = 0
        
        for row in results:
            technique_uri = row.technique
            technique_name = str(technique_uri).split('#')[-1]
            
            # Generate label
            label = self._generate_technique_label(technique_name)
            
            # Add label to graph
            graph.add((technique_uri, RDFS.label, Literal(label)))
            techniques_updated += 1
            print(f"Added label to {technique_name}: '{label}'")
        
        print(f"\nAdded labels to {techniques_updated} techniques")
        return graph


def main():
    parser = argparse.ArgumentParser(
        description='Generate CSRO ContainerAttackTechnique instances',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--ontology',
        help='Path to existing CSRO ontology file'
    )
    parser.add_argument(
        '--config',
        help='Path to JSON configuration file with technique definitions'
    )
    parser.add_argument(
        '--output',
        default='../configs/generated_techniques.ttl',
        help='Output file path (default: ../configs/generated_techniques.ttl)'
    )
    parser.add_argument(
        '--format',
        default='turtle',
        choices=['turtle', 'xml', 'n3', 'nt'],
        help='Output format (default: turtle)'
    )
    parser.add_argument(
        '--add-labels',
        action='store_true',
        help='Add rdfs:label properties to existing techniques in ontology'
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = AttackTechniqueGenerator(args.ontology)
    
    if args.add_labels and args.ontology:
        # Add labels to existing techniques
        graph = generator.add_labels_to_existing_techniques(args.ontology)
    elif args.config:
        # Generate from config file
        graph = generator.generate_from_config(args.config)
    else:
        # Generate example technique
        print("No config provided. Generating example technique...")
        graph = generator.generate_technique(
            name="ExampleContainerTechnique",
            description="Example container attack technique for demonstration purposes",
            difficulty="Medium",
            attack_technique="T1234",
            required_traits=["host_network", "cap_add_CAP_NET_ADMIN"]
        )
    
    # Save output
    graph.serialize(destination=args.output, format=args.format)
    print(f"\nGenerated techniques saved to: {args.output}")
    print(f"Format: {args.format}")


if __name__ == "__main__":
    main()