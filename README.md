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

- `csro.ttl` — The main ontology file in Turtle format.
- `sparql_queries/`
  - `calculation_example.sparql` — Example query for risk calculation.
  - `calculation_rules_export.sparql` — Query to export calculation rules.
  - `csro_export.sparql` — Query to export the ontology.
- `container_security_assumptions/`
  - `container_security_assumptions.csv` — Curated list of container security assumptions from standards such as NIST SP 800-190.

## Usage

1. **Ontology**
   - Import `csro.ttl` into your triple store or ontology editor (e.g., Protégé).
   - Use the defined classes and properties to model container security scenarios.

2. **SPARQL Queries**
   - Run the queries in the `sparql_queries` folder against a CSRO-compliant dataset.
   - Adapt queries as needed for your use case.

3. **Container Security Assumptions**
   - Access the curated list of container security assumptions from established standards.
   - Use these assumptions as reference for security assessments and risk modeling.

## Classes and Properties

The ontology includes:
- **Classes:** SecurityAssumption, Risk, RiskLevel, AttackAction, Component, Standard, etc.
- **Object Properties:** hasRiskLevel, appliesTechnique, isTreatedBy, etc.
- **Data Properties:** description, publicationYear, weightValue, etc.

See `csro.ttl` for the full list.

## How to Cite

If you use CSRO, please cite the ontology using its IRI:  
`https://w3id.org/csro/ontology`

## License

This ontology is licensed under Creative Commons. See the ontology metadata for details.

## Contact

For questions or contributions, please contact Yannick Landeck.
