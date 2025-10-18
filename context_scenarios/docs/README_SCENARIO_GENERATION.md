# CSRO Scenario Generation Tools

This directory contains tools for automating the generation of ContextScenario instances.

## Files

- **generate_scenarios.py**: Python script for automated scenario generation
- **scenario_configs/**: Directory containing JSON configuration files for scenarios
- **example_scenarios.json**: Example configuration with 8 different scenario types

## Requirements

```bash
pip install rdflib
```

## Usage

### Generate scenarios from configuration file

```bash
python generate_scenarios.py --config scenario_configs/example_scenarios.json --output new_scenarios.ttl
```

### Generate a single example scenario

```bash
python generate_scenarios.py
```

### Specify custom ontology location

```bash
python generate_scenarios.py --ontology path/to/csro.ttl --config config.json
```

### Change output format

```bash
python generate_scenarios.py --config config.json --format xml
```

## Configuration Format

JSON configuration files define scenarios with their assumption satisfaction states:

```json
{
  "scenarios": [
    {
      "name": "MyScenario",
      "description": "Description of the scenario",
      "rules": {
        "IMG": "Satisfied",
        "RTS": "Dissatisfied",
        "NET": "Unknown"
      },
      "default": "Dissatisfied"
    }
  ]
}
```

### Configuration Options

- **name**: Scenario name (will be used as URI local name)
- **description**: Human-readable description
- **rules**: Category-based satisfaction rules (keys are assumption category prefixes)
- **satisfaction_map**: Explicit mapping of specific assumption IDs to states (overrides category rules)
- **default**: Default satisfaction state for assumptions not covered by rules

### Satisfaction States

- `Satisfied`: The security assumption is implemented/satisfied
- `Dissatisfied`: The security assumption is not implemented
- `Unknown`: The satisfaction state is unknown or partially satisfied

## Workflow

1. **Create configuration file** defining your scenarios
2. **Run script** to generate Turtle syntax
3. **Review output** in generated file
4. **Manually add** the generated content to csro.ttl (or merge with RDFLib)
5. **Generate AttackActions** using the SPARQL query in `sparql_queries/generate_attack_actions.sparql`

## Example Scenarios

The `example_scenarios.json` file includes:

1. **ProductionScenario**: Full security controls
2. **DevelopmentScenario**: Minimal security for development
3. **NetworkHardenedScenario**: Strong network security
4. **RuntimeHardenedScenario**: Strong runtime security
5. **CISCompliantScenario**: CIS Docker Benchmark compliance
6. **MinimalSecurityScenario**: Only critical controls
7. **HighRiskScenario**: High-risk configuration
8. **ImageSecurityFocusedScenario**: Focus on image security

## Integration with SPARQL Queries

After generating scenarios with this script, use the SPARQL queries in `sparql_queries/` to:

1. Validate scenario completeness
2. Generate AttackAction instances
3. Analyze assumption coverage

## Advanced Usage: Category-Based Rules

Category prefixes from your ontology:
- IMG: Container Image Security
- RTS: Runtime Security
- NET: Network Security
- AUTH: Authentication & Access
- SCM: Secrets & Config Management
- HIS: Host & Infrastructure Security
- MON: Monitoring, Detection & Response
- CIC: CI/CD & Supply Chain
- CRM: Compliance & Risk Management

Set rules by category for quick configuration:

```json
"rules": {
  "IMG": "Satisfied",
  "RTS": "Satisfied",
  "NET": "Unknown"
}
```

## Advanced Usage: Explicit Mapping

For fine-grained control, specify individual assumptions:

```json
"satisfaction_map": {
  "IMG-1": "Satisfied",
  "IMG-2": "Dissatisfied",
  "RTS-1": "Satisfied",
  "NET-1": "Unknown"
}
```

## Tips

- Start with category-based rules for quick scenario creation
- Use explicit mapping for specific edge cases
- Generate 5-10 meaningful scenarios rather than trying to cover all combinations
- Always validate generated scenarios with the SPARQL validation queries
- Review and adjust satisfaction states based on domain knowledge
