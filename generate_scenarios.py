#!/usr/bin/env python3
"""
CSRO Scenario Generator

This script automates the generation of ContextScenario instances with all required
AssumptionInScenario instances for the CSRO ontology.

Usage:
    python generate_scenarios.py --help
    python generate_scenarios.py --config config.json --output new_scenarios.ttl

Configuration JSON format:
{
  "scenarios": [
    {
      "name": "ProductionScenario",
      "description": "Typical production deployment with security best practices",
      "rules": {
        "IMG": "Satisfied",
        "RTS": "Satisfied",
        "NET": "Satisfied",
        "default": "Dissatisfied"
      }
    },
    {
      "name": "DevelopmentScenario",
      "description": "Development environment with relaxed security",
      "satisfaction_map": {
        "IMG-1": "Dissatisfied",
        "RTS-1": "Unknown",
        ...
      }
    }
  ]
}
"""

import argparse
import json
from typing import Dict, List, Optional
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

# Define namespaces
CSRO = Namespace("https://w3id.org/csro/ontology#")


class ScenarioGenerator:
    """Generate CSRO ContextScenario instances programmatically."""
    
    def __init__(self, ontology_path: str):
        """Load the existing CSRO ontology."""
        self.graph = Graph()
        self.graph.bind("csro", CSRO)
        self.graph.parse(ontology_path, format="turtle")
        print(f"Loaded ontology from {ontology_path}")
        
        # Get all assumptions
        self.assumptions = self._load_assumptions()
        print(f"Found {len(self.assumptions)} security assumptions")
    
    def _load_assumptions(self) -> List[Dict]:
        """Load all ContainerSecurityAssumption instances."""
        assumptions = []
        
        query = """
        PREFIX csro: <https://w3id.org/csro/ontology#>
        SELECT ?assumption ?assumptionId
        WHERE {
            ?assumption a csro:ContainerSecurityAssumption ;
                       csro:assumptionId ?assumptionId .
        }
        ORDER BY ?assumptionId
        """
        
        results = self.graph.query(query)
        for row in results:
            assumptions.append({
                'uri': row.assumption,
                'id': str(row.assumptionId)
            })
        
        return assumptions
    
    def generate_scenario(self, 
                         name: str, 
                         description: str,
                         satisfaction_map: Optional[Dict[str, str]] = None,
                         category_rules: Optional[Dict[str, str]] = None,
                         default_state: str = "Unknown") -> Graph:
        """
        Generate a new scenario with AssumptionInScenario instances.
        
        Args:
            name: Scenario name (e.g., "ProductionScenario")
            description: Human-readable description
            satisfaction_map: Dict mapping assumption IDs to satisfaction states
            category_rules: Dict mapping category prefixes to satisfaction states
            default_state: Default satisfaction state if not specified
        
        Returns:
            Graph containing the new scenario triples
        """
        scenario_graph = Graph()
        scenario_graph.bind("csro", CSRO)
        
        scenario_uri = CSRO[name]
        
        # Add scenario instance
        scenario_graph.add((scenario_uri, RDF.type, CSRO.ContextScenario))
        scenario_graph.add((scenario_uri, CSRO.description, Literal(description)))
        
        # Add standard components
        components = [
            CSRO.Application,
            CSRO.Device,
            CSRO.DeviceContainerRuntime,
            CSRO.DeviceOperatingSystem,
            CSRO.OtherApplications
        ]
        for component in components:
            scenario_graph.add((scenario_uri, CSRO.includes, component))
        
        # Generate AssumptionInScenario instances
        for assumption in self.assumptions:
            assumption_id = assumption['id']
            assumption_uri = assumption['uri']
            
            # Determine satisfaction state
            satisfaction = self._get_satisfaction_state(
                assumption_id,
                satisfaction_map,
                category_rules,
                default_state
            )
            
            # Create AssumptionInScenario instance
            ais_name = f"{name}_{assumption_id.replace('-', '_')}"
            ais_uri = CSRO[ais_name]
            
            scenario_graph.add((ais_uri, RDF.type, CSRO.AssumptionInScenario))
            scenario_graph.add((ais_uri, CSRO.forAssumption, assumption_uri))
            scenario_graph.add((ais_uri, CSRO.hasSatisfactionState, CSRO[satisfaction]))
            
            # Link to scenario
            scenario_graph.add((scenario_uri, CSRO.includesAssumption, ais_uri))
        
        print(f"Generated scenario: {name} with {len(self.assumptions)} assumptions")
        return scenario_graph
    
    def _get_satisfaction_state(self,
                               assumption_id: str,
                               satisfaction_map: Optional[Dict[str, str]],
                               category_rules: Optional[Dict[str, str]],
                               default_state: str) -> str:
        """Determine the satisfaction state for an assumption."""
        # Priority 1: Explicit mapping
        if satisfaction_map and assumption_id in satisfaction_map:
            return satisfaction_map[assumption_id]
        
        # Priority 2: Category rules
        if category_rules:
            category = assumption_id.split('-')[0]
            if category in category_rules:
                return category_rules[category]
        
        # Priority 3: Default
        return default_state
    
    def generate_from_config(self, config_path: str) -> Graph:
        """Generate multiple scenarios from a JSON configuration file."""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        combined_graph = Graph()
        combined_graph.bind("csro", CSRO)
        
        for scenario_config in config.get('scenarios', []):
            name = scenario_config['name']
            description = scenario_config['description']
            satisfaction_map = scenario_config.get('satisfaction_map')
            category_rules = scenario_config.get('rules')
            default_state = scenario_config.get('default', 'Unknown')
            
            scenario_graph = self.generate_scenario(
                name=name,
                description=description,
                satisfaction_map=satisfaction_map,
                category_rules=category_rules,
                default_state=default_state
            )
            
            # Merge into combined graph
            combined_graph += scenario_graph
        
        return combined_graph


def main():
    parser = argparse.ArgumentParser(
        description='Generate CSRO ContextScenario instances',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--ontology',
        default='csro.ttl',
        help='Path to CSRO ontology file (default: csro.ttl)'
    )
    parser.add_argument(
        '--config',
        help='Path to JSON configuration file'
    )
    parser.add_argument(
        '--output',
        default='generated_scenarios.ttl',
        help='Output file path (default: generated_scenarios.ttl)'
    )
    parser.add_argument(
        '--format',
        default='turtle',
        choices=['turtle', 'xml', 'n3', 'nt'],
        help='Output format (default: turtle)'
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = ScenarioGenerator(args.ontology)
    
    if args.config:
        # Generate from config file
        graph = generator.generate_from_config(args.config)
    else:
        # Generate example scenario
        print("No config provided. Generating example scenario...")
        graph = generator.generate_scenario(
            name="ExampleScenario",
            description="Example scenario with category-based rules",
            category_rules={
                "IMG": "Satisfied",
                "RTS": "Satisfied",
                "NET": "Dissatisfied",
                "AUTH": "Unknown"
            },
            default_state="Dissatisfied"
        )
    
    # Save output
    graph.serialize(destination=args.output, format=args.format)
    print(f"\nGenerated scenarios saved to: {args.output}")
    print(f"Format: {args.format}")


if __name__ == "__main__":
    main()
