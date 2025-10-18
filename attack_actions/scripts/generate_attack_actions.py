#!/usr/bin/env python3
"""
CSRO Attack Action Generator

Generates AttackAction instances from configuration metadata for all technique-scenario combinations.

Usage:
    python generate_attack_actions.py
    python generate_attack_actions.py --config ../configs/attack_action_metadata.json
    python generate_attack_actions.py --validate-only
"""

import argparse
import json
import sys
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

# Define namespaces
CSRO = Namespace("https://w3id.org/csro/ontology#")

# Valid impact ratings
VALID_IMPACT_RATINGS = {'Negligible', 'Moderate', 'Critical', 'Disastrous'}

# Valid component names
VALID_COMPONENTS = {
    'Application',
    'Device', 
    'DeviceOperatingSystem',
    'DeviceContainerRuntime',
    'OtherApplications'
}


class AttackActionGenerator:
    """Generator for AttackAction instances from configuration."""
    
    def __init__(self, ontology_path: str, config_path: str):
        """Initialize generator with paths."""
        self.ontology_path = Path(ontology_path)
        self.config_path = Path(config_path)
        self.ontology = None
        self.config = None
        self.techniques = set()
        self.scenarios = set()
        self.components = set()
        
    def load_ontology(self):
        """Load the CSRO ontology."""
        print(f"Loading ontology from: {self.ontology_path}")
        self.ontology = Graph()
        self.ontology.bind("csro", CSRO)
        self.ontology.parse(str(self.ontology_path), format="turtle")
        
        # Extract available techniques
        self.techniques = {
            str(s).split('#')[-1]
            for s in self.ontology.subjects(RDF.type, CSRO.ContainerAttackTechnique)
        }
        print(f"  Found {len(self.techniques)} ContainerAttackTechnique instances")
        
        # Extract available scenarios
        self.scenarios = {
            str(s).split('#')[-1]
            for s in self.ontology.subjects(RDF.type, CSRO.ContextScenario)
        }
        print(f"  Found {len(self.scenarios)} ContextScenario instances")
        
        # Extract available components
        self.components = {
            str(s).split('#')[-1]
            for s in self.ontology.subjects(RDF.type, CSRO.Component)
        }
        print(f"  Found {len(self.components)} Component instances")
        
    def load_config(self):
        """Load configuration from JSON file."""
        print(f"\nLoading configuration from: {self.config_path}")
        
        if not self.config_path.exists():
            print(f"ERROR: Configuration file not found: {self.config_path}")
            sys.exit(1)
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        techniques_count = len(self.config.get('attack_techniques', []))
        print(f"  Found {techniques_count} technique configurations")
        
    def validate_config(self):
        """Validate the configuration."""
        print("\nValidating configuration...")
        errors = []
        warnings = []
        
        if 'attack_techniques' not in self.config:
            errors.append("Missing 'attack_techniques' key in configuration")
            return errors, warnings
            
        seen_impact_ids = set()
        seen_risk_ids = set()
        
        for idx, technique_config in enumerate(self.config['attack_techniques']):
            tech_id = technique_config.get('technique_id', f'[missing at index {idx}]')
            
            # Validate technique exists
            if 'technique_id' not in technique_config:
                errors.append(f"Technique at index {idx}: Missing 'technique_id'")
                continue
                
            if tech_id not in self.techniques:
                errors.append(f"Technique '{tech_id}': Not found in ontology")
                
            # Validate affected_components
            if 'affected_components' not in technique_config:
                errors.append(f"Technique '{tech_id}': Missing 'affected_components'")
            else:
                components = technique_config['affected_components']
                if not components:
                    warnings.append(f"Technique '{tech_id}': No affected components specified")
                    
                for component in components:
                    if component not in VALID_COMPONENTS:
                        errors.append(
                            f"Technique '{tech_id}': Invalid component '{component}'. "
                            f"Must be one of: {', '.join(sorted(VALID_COMPONENTS))}"
                        )
                    elif component not in self.components:
                        warnings.append(
                            f"Technique '{tech_id}': Component '{component}' not found in ontology "
                            f"(valid but may need to be added)"
                        )
                        
            # Validate impacts
            if 'impacts' not in technique_config:
                errors.append(f"Technique '{tech_id}': Missing 'impacts'")
            else:
                impacts = technique_config['impacts']
                if not impacts:
                    warnings.append(f"Technique '{tech_id}': No impacts specified")
                    
                for impact_idx, impact in enumerate(impacts):
                    # Validate impact structure
                    required_fields = ['impact_id', 'description', 'impact_rating', 'risk_id', 'risk_description']
                    for field in required_fields:
                        if field not in impact:
                            errors.append(f"Technique '{tech_id}', Impact {impact_idx}: Missing '{field}'")
                            
                    # Validate impact_id uniqueness
                    impact_id = impact.get('impact_id')
                    if impact_id:
                        if impact_id in seen_impact_ids:
                            errors.append(f"Technique '{tech_id}': Duplicate impact_id '{impact_id}'")
                        seen_impact_ids.add(impact_id)
                        
                    # Validate risk_id uniqueness
                    risk_id = impact.get('risk_id')
                    if risk_id:
                        if risk_id in seen_risk_ids:
                            errors.append(f"Technique '{tech_id}': Duplicate risk_id '{risk_id}'")
                        seen_risk_ids.add(risk_id)
                        
                    # Validate impact_rating
                    rating = impact.get('impact_rating')
                    if rating and rating not in VALID_IMPACT_RATINGS:
                        errors.append(
                            f"Technique '{tech_id}', Impact '{impact_id}': "
                            f"Invalid impact_rating '{rating}'. "
                            f"Must be one of: {', '.join(sorted(VALID_IMPACT_RATINGS))}"
                        )
                        
        return errors, warnings
        
    def generate_instances(self, output_path: str):
        """Generate all AttackAction instances."""
        print("\nGenerating instances...")
        
        # Create output graph
        output_graph = Graph()
        output_graph.bind("csro", CSRO)
        
        stats = {
            'attack_actions': 0,
            'impacts': 0,
            'risks': 0
        }
        
        for technique_config in self.config['attack_techniques']:
            tech_id = technique_config['technique_id']
            affected_components = technique_config.get('affected_components', [])
            impacts = technique_config.get('impacts', [])
            
            # Generate shared Impact and Risk instances for this technique
            for impact in impacts:
                impact_uri = CSRO[impact['impact_id']]
                risk_uri = CSRO[impact['risk_id']]
                rating_uri = CSRO[impact['impact_rating']]
                
                # Create Impact instance
                output_graph.add((impact_uri, RDF.type, CSRO.Impact))
                output_graph.add((impact_uri, CSRO.description, Literal(impact['description'])))
                output_graph.add((impact_uri, CSRO.hasImpactRating, rating_uri))
                output_graph.add((impact_uri, CSRO.indicates, risk_uri))
                stats['impacts'] += 1
                
                # Create Risk instance
                output_graph.add((risk_uri, RDF.type, CSRO.Risk))
                output_graph.add((risk_uri, CSRO.description, Literal(impact['risk_description'])))
                stats['risks'] += 1
                
            # Generate AttackAction instances for each scenario
            for scenario_name in sorted(self.scenarios):
                action_name = f"{tech_id}Attack_{scenario_name}"
                action_uri = CSRO[action_name]
                
                # Create AttackAction instance
                output_graph.add((action_uri, RDF.type, CSRO.AttackAction))
                output_graph.add((action_uri, CSRO.appliesTechnique, CSRO[tech_id]))
                output_graph.add((action_uri, CSRO.inContext, CSRO[scenario_name]))
                output_graph.add((action_uri, CSRO.description, 
                                Literal(f"{tech_id} attack applied in {scenario_name} context")))
                
                # Add affected components
                for component_name in affected_components:
                    output_graph.add((action_uri, CSRO.affects, CSRO[component_name]))
                    
                # Add caused impacts
                for impact in impacts:
                    output_graph.add((action_uri, CSRO.causesImpact, CSRO[impact['impact_id']]))
                    
                stats['attack_actions'] += 1
                
            print(f"  ✓ Generated {len(self.scenarios)} AttackActions for {tech_id}")
            
        # Save output
        output_path = Path(output_path)
        print(f"\nSaving to: {output_path}")
        output_graph.serialize(destination=str(output_path), format="turtle")
        
        # Print summary
        print("\n" + "="*80)
        print("GENERATION SUMMARY")
        print("="*80)
        print(f"✓ Generated {stats['attack_actions']} AttackAction instances")
        print(f"  ({len(self.config['attack_techniques'])} techniques × {len(self.scenarios)} scenarios)")
        print(f"✓ Generated {stats['impacts']} Impact instances")
        print(f"✓ Generated {stats['risks']} Risk instances")
        print(f"✓ Output saved to: {output_path}")
        print("="*80)
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description='Generate CSRO AttackAction instances from configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--ontology',
        default='../../csro.ttl',
        help='Path to CSRO ontology file (default: ../../csro.ttl)'
    )
    parser.add_argument(
        '--config',
        default='../configs/attack_action_metadata.json',
        help='Path to configuration file (default: ../configs/attack_action_metadata.json)'
    )
    parser.add_argument(
        '--output',
        default='../configs/generated_attack_actions.ttl',
        help='Output file path (default: ../configs/generated_attack_actions.ttl)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configuration without generating instances'
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = AttackActionGenerator(args.ontology, args.config)
    
    # Load ontology and config
    generator.load_ontology()
    generator.load_config()
    
    # Validate
    errors, warnings = generator.validate_config()
    
    # Print warnings
    if warnings:
        print("\n" + "="*80)
        print("WARNINGS")
        print("="*80)
        for warning in warnings:
            print(f"⚠ {warning}")
            
    # Print errors
    if errors:
        print("\n" + "="*80)
        print("VALIDATION ERRORS")
        print("="*80)
        for error in errors:
            print(f"✗ {error}")
        print("="*80)
        print(f"\n{len(errors)} error(s) found. Please fix configuration and try again.")
        sys.exit(1)
        
    print("\n✓ Configuration validation passed")
    
    if args.validate_only:
        print("\nValidation complete (--validate-only mode, no instances generated)")
        return
        
    # Generate instances
    generator.generate_instances(args.output)


if __name__ == "__main__":
    main()
