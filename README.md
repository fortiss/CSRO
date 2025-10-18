# CSRO: Container Security Risk Ontology

## Overview

The Container Security Risk Ontology (CSRO) provides a formal representation for security risk assessment in containerized environments. It defines concepts, relationships, and calculation rules relevant to container security, supporting automated reasoning and risk analysis.

## Ontology Metadata

- **IRI:** https://w3id.org/csro/ontology
- **Namespace Prefix:** `csro`
- **License:** [Creative Commons](http://creativecommons.org/ns#license)
- **Contributor:** [Yannick Landeck](https://github.com/YannickLand)
- **Description:** The ontology models security assumptions, risk factors, calculation rules, and standards for containers.

## Repository Structure

- `csro.ttl` — The main ontology file in Turtle format
- `attack_actions/` — Attack action generation and configuration
- `attack_techniques/` — Attack technique definitions and weight matrices  
- `container_security_assumptions/` — Container security assumptions from established standards
- `context_scenarios/` — Context scenario generation and configuration
- `sparql_queries/` — SPARQL queries for risk calculation and data export
- `docs/` — Detailed documentation and automation guides

## Quick Start

1. **Import the Ontology**
   ```turtle
   # Import csro.ttl into your triple store or ontology editor (e.g., Protégé, GraphDB)
   ```

2. **Run Risk Calculations**
   ```sparql
   # Execute sparql_queries/calculate_risk_ratings.sparql for comprehensive risk assessment
   ```

3. **Explore Components**
   - See individual README files in each directory for detailed usage instructions
   - Check `docs/` for automation guides and detailed documentation

## Key Features

- **Dynamic Risk Calculation**: Context-aware risk assessment based on security assumption satisfaction
- **Attack Technique Modeling**: Integration with MITRE ATT&CK framework via D3FEND ontology
- **Treatment Recommendations**: Automatic selection of relevant security treatments based on calculation rules
- **Scenario-Based Analysis**: Support for different deployment scenarios and security postures

## Core Concepts

The ontology includes key classes such as:
- `ContainerSecurityAssumption` — Security controls and their satisfaction states
- `ContainerAttackTechnique` — Attack methods with associated calculation rules  
- `AttackAction` — Specific attacks in given scenarios with calculated risk levels
- `RiskTreatment` — Security measures to mitigate identified risks
- `ContextScenario` — Deployment contexts with different security postures

See `csro.ttl` for complete class and property definitions.

## Citation

If you use CSRO, please cite the ontology using its IRI:  
`https://w3id.org/csro/ontology`

## License

This ontology is licensed under Creative Commons. See the ontology metadata for details.

## Contact

For questions or contributions, please contact [Yannick Landeck](https://github.com/YannickLand).
