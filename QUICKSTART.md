# Quick Start Guide: Adding Attack Techniques and Scenarios

## Prerequisites
```bash
pip install rdflib
```

## Quick Start: 3 Steps

### Step 1: Generate Example Scenarios (30 seconds)
```bash
python generate_scenarios.py
```
This creates `generated_scenarios.ttl` with an example scenario.

### Step 2: Generate Attack Actions (30 seconds)
```bash
python generate_attack_actions.py
```
This creates `generated_attack_actions.ttl` for all technique-scenario combos.

### Step 3: Review and Integrate (5 minutes)
- Open the generated .ttl files
- Review the content
- Copy into csro.ttl or merge programmatically

## Common Tasks

### Task: Create Multiple Scenarios from Config

1. **Edit** `scenario_configs/example_scenarios.json`:
```json
{
  "scenarios": [
    {
      "name": "MyNewScenario",
      "description": "My custom scenario",
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

2. **Generate**:
```bash
python generate_scenarios.py --config scenario_configs/example_scenarios.json --output my_scenarios.ttl
```

3. **Result**: All 48 assumptions are included with satisfaction states based on your rules!

### Task: Generate AttackActions for New Scenarios

After adding new scenarios to csro.ttl:

```bash
python generate_attack_actions.py --ontology csro.ttl --output new_actions.ttl
```

### Task: Validate Your Ontology

Use SPARQL queries in `sparql_queries/`:

1. Check scenario completeness:
   - Run `validate_scenario_completeness.sparql`
   - Each scenario should have all 48 assumptions

2. Check attack action coverage:
   - Run `validate_attack_action_coverage.sparql`
   - Should show TRUE for all technique-scenario combinations

### Task: List All Assumptions by Category

Run `list_assumptions_by_category.sparql` to see what assumptions exist.

### Task: Analyze Weights for a Technique

Edit `analyze_technique_weights.sparql`:
- Change `csro:ContainerExploitPublicFacingApp` to your technique
- Run query to see which assumptions affect it

## Category Prefixes Reference

Use these in scenario configuration:

- **IMG**: Container Image Security (6 assumptions)
- **RTS**: Runtime Security (7 assumptions)
- **NET**: Network Security (4 assumptions)
- **AUTH**: Authentication & Access (3 assumptions)
- **SCM**: Secrets & Config Management (4 assumptions)
- **HIS**: Host & Infrastructure Security (3 assumptions)
- **MON**: Monitoring, Detection & Response (8 assumptions)
- **CIC**: CI/CD & Supply Chain (6 assumptions)
- **CRM**: Compliance & Risk Management (4 assumptions)

## Satisfaction States

- **Satisfied**: Control is implemented
- **Dissatisfied**: Control is NOT implemented
- **Unknown**: State is unknown or partially implemented

## Example Scenario Configurations

### Production-Like
```json
{
  "name": "ProductionScenario",
  "rules": {
    "IMG": "Satisfied", "RTS": "Satisfied", "NET": "Satisfied",
    "AUTH": "Satisfied", "SCM": "Satisfied", "HIS": "Satisfied",
    "MON": "Satisfied", "CIC": "Satisfied", "CRM": "Satisfied"
  }
}
```

### Development-Like
```json
{
  "name": "DevelopmentScenario",
  "rules": {
    "IMG": "Dissatisfied", "RTS": "Dissatisfied", "NET": "Dissatisfied"
  },
  "default": "Dissatisfied"
}
```

### Network Hardened Only
```json
{
  "name": "NetworkHardenedScenario",
  "rules": {
    "NET": "Satisfied", "AUTH": "Satisfied"
  },
  "default": "Dissatisfied"
}
```

### Minimal Security (Specific Assumptions)
```json
{
  "name": "MinimalSecurityScenario",
  "satisfaction_map": {
    "IMG-1": "Satisfied",
    "RTS-1": "Satisfied",
    "NET-2": "Satisfied",
    "SCM-1": "Satisfied"
  },
  "default": "Dissatisfied"
}
```

## Workflow for Adding New Attack Technique

### 1. Define Technique (Manual - csro.ttl)
```turtle
csro:NewAttack rdf:type owl:NamedIndividual ,
                        csro:ContainerAttackTechnique ;
               csro:hasBaseDifficulty csro:Medium ;
               csro:referencesAttackTechnique d3f:TXXXX ;
               csro:requiresTrait csro:some_trait ;
               csro:description "..." .
```

### 2. Define Weights (Manual - csro.ttl)
For each relevant assumption, create weight:
```turtle
csro:NewAttack_IMG_1_Weight rdf:type owl:NamedIndividual ,
                                     csro:AssumptionWeight ;
                            csro:refersToAssumption csro:IMG_1 ;
                            csro:weightValue 3.0 ;
                            csro:effectDescription "High effect..." .
```

### 3. Define Calculation Rules (Manual - csro.ttl)
```turtle
csro:NewAttackExploitabilityRule rdf:type owl:NamedIndividual ,
                                          csro:ExploitabilityCalculationRule ;
                                 csro:appliesTo csro:NewAttack ;
                                 csro:hasWeight csro:NewAttack_IMG_1_Weight ,
                                                csro:NewAttack_RTS_1_Weight ;
                                 csro:description "..." .
```

### 4. Generate Attack Actions (Automated)
```bash
python generate_attack_actions.py
```

### 5. Add Manual Properties (Quick editing)
For each generated AttackAction, add:
- `csro:affects` - which components
- `csro:causesImpact` - which impact

## Troubleshooting

### "Import rdflib could not be resolved"
```bash
pip install rdflib
```

### "File not found: csro.ttl"
Run scripts from the CSRO root directory:
```bash
cd C:\Users\landeck\git\CSRO
python generate_scenarios.py
```

### Scenario has fewer than 48 assumptions
Check that all ContainerSecurityAssumption instances have `csro:assumptionId` property.

### Attack actions already exist
The script skips existing attack actions. To regenerate, remove them from csro.ttl first.

## File Structure

```
CSRO/
├── csro.ttl                              # Main ontology
├── generate_scenarios.py                 # Scenario generator
├── generate_attack_actions.py            # AttackAction generator
├── AUTOMATION_SUMMARY.md                 # Full documentation
├── QUICKSTART.md                         # This file
├── scenario_generation_strategy.md       # Detailed strategy
├── scenario_configs/
│   └── example_scenarios.json           # Example configs
└── sparql_queries/
    ├── generate_scenario_template.sparql
    ├── generate_scenario_definition.sparql
    ├── generate_attack_actions.sparql
    ├── list_assumptions_by_category.sparql
    ├── analyze_technique_weights.sparql
    ├── validate_scenario_completeness.sparql
    └── validate_attack_action_coverage.sparql
```

## Need Help?

1. Read `AUTOMATION_SUMMARY.md` for full details
2. Read `scenario_generation_strategy.md` for strategy guidance
3. Check example files in `scenario_configs/`
4. Review SPARQL queries for templates and validation

## Tips

- **Start small**: Generate 2-3 scenarios first, test workflow
- **Use templates**: Copy example_scenarios.json and modify
- **Validate often**: Run validation queries after changes
- **Version control**: Commit before running generators
- **Review output**: Always review generated .ttl before integrating
