# Attack Actions Workflow

This folder contains tools, configuration, and documentation for generating AttackAction instances from ContainerAttackTechnique definitions and ContextScenario configurations.

## 📁 Folder Structure

```
attack_actions/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── configs/
│   ├── attack_action_metadata.json    # Main configuration file
│   ├── example_attack_action.json     # Documentation example
│   └── generated_attack_actions.ttl   # Generated output (not in git)
├── scripts/
│   ├── generate_attack_actions.py     # Generation script
│   └── merge_attack_actions_to_ontology.py  # Merge script
└── docs/
    └── attack_action_generation_guide.md    # Detailed documentation
```

## 🔄 Workflow Overview

### Step 1: Configure Attack Metadata

Edit `configs/attack_action_metadata.json` to define:
- **Affected Components**: Which system components each technique targets
- **Impacts**: Security impacts with their severity ratings
- **Risks**: Associated risks for each impact

### Step 2: Generate AttackAction Instances

Run the generation script to create all technique × scenario combinations:

```bash
cd scripts
python generate_attack_actions.py
```

This generates:
- **13 techniques × 22 scenarios = 286 AttackAction instances**
- Shared Impact and Risk instances (one set per technique)
- Output saved to `configs/generated_attack_actions.ttl`

### Step 3: Merge into Ontology

Run the merge script to add instances to `csro.ttl`:

```bash
python merge_attack_actions_to_ontology.py
```

The script:
- Preserves existing AttackAction instances
- Only adds new ones from the generated file
- Creates automatic backup
- Validates component references

## 📝 Configuration Format

The `attack_action_metadata.json` file structure:

```json
{
  "attack_techniques": [
    {
      "technique_id": "ContainerDataFromLocalSystem",
      "affected_components": ["DeviceOperatingSystem", "Application"],
      "impacts": [
        {
          "impact_id": "HostDataExfiltration",
          "description": "Container accesses and exfiltrates sensitive host data",
          "impact_rating": "Critical",
          "risk_id": "DataExfiltrationRisk",
          "risk_description": "Risk of sensitive data being stolen from host system"
        }
      ]
    }
  ]
}
```

### Field Descriptions:

- **technique_id**: Must match a `ContainerAttackTechnique` individual in the ontology
- **affected_components**: List of `Component` individuals (e.g., `Device`, `Application`, `DeviceOperatingSystem`)
- **impacts**: Array of security impacts caused by the technique
  - **impact_id**: Unique identifier for the Impact individual
  - **description**: Human-readable impact description
  - **impact_rating**: One of: `Negligible`, `Moderate`, `Critical`, `Disastrous`
  - **risk_id**: Unique identifier for the associated Risk individual
  - **risk_description**: Human-readable risk description

## 🎯 Key Points

1. **Technique-Level Metadata**: Components, Impacts, and Risks are defined once per technique
2. **Scenario-Independent**: Impact ratings don't change based on context
3. **Automatic Generation**: Script creates all AttackAction instances automatically
4. **Dynamic Risk Calculation**: SPARQL query `calculate_risk_ratings.sparql` constructs context-specific instances
5. **Reusable Workflow**: Easy to add new techniques by updating the JSON config

## 📊 Generated Instances

For each technique in the config, the script generates:

### Shared Instances (per technique):
- **Impact** instances with `hasImpactRating`
- **Risk** instances linked via `indicates` from Impact

### Per-Scenario Instances:
- **AttackAction** instances (e.g., `ContainerDataFromLocalSystem_ProductionScenario`)
  - Links to technique via `appliesTechnique`
  - Links to scenario via `inContext`
  - Links to components via `affects` (one triple per component)
  - Links to impacts via `causesImpact` (one triple per impact)

## 🔍 Validation

The generation script validates:
- ✅ All `technique_id` values exist in the ontology
- ✅ All `affected_components` exist in the ontology
- ✅ All `impact_rating` values are valid enum members
- ✅ No duplicate Impact or Risk IDs across techniques

## 📖 Next Steps

1. **Fill in the configuration**: See `docs/attack_action_generation_guide.md` for detailed guidance
2. **Example available**: Check `configs/example_attack_action.json` for reference
3. **Generate instances**: Run the scripts when configuration is complete
4. **Add RiskTreatment**: Will be addressed systematically in a future workflow

## 🔗 Related Workflows

- **Attack Techniques**: `attack_techniques/` - Define and weight techniques
- **Context Scenarios**: `context_scenarios/` - Define security postures
- **Risk Calculations**: `sparql_queries/calculate_risk_ratings.sparql` - Dynamic risk assessment
