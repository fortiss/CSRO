# CSRO Ontology: Understanding and Automation Summary

## Yes, I Understand Your Ontology Structure! 

Your CSRO (Container Security Risk Ontology) has a well-designed structure for modeling container security risks:

### Core Architecture

```
ContainerSecurityAssumption (48 assumptions across 8 categories)
    ↓ (via AssumptionInScenario with satisfaction states)
ContextScenario (3 currently: Basic, Hardened, Mixed)
    ↓ (combined with)
ContainerAttackTechnique (3 currently: ExploitPublicFacing, DataFromLocalSystem, PtraceInjection)
    ↓ (creates)
AttackAction (9 currently: 3 techniques × 3 scenarios)
    ↓ (causes)
Impact & Risk
```

### Key Insight: The Combinatorial Challenge

- **Current**: 3 scenarios × 3 techniques = 9 attack actions ✅ Manageable
- **With 48 assumptions**: Theoretically 3^48 possible combinations 😱 Not manageable
- **Solution**: Create representative scenarios, not exhaustive combinations

## What Can Be Automated? ✅

### Fully Automatable
1. **AssumptionInScenario generation** - Create instances linking scenarios to all assumptions
2. **AttackAction generation** - Create instances for all technique × scenario combinations
3. **Validation queries** - Check completeness and consistency

### Semi-Automatable (Templates + Manual Review)
4. **Scenario definitions** - Generate skeleton, manually configure satisfaction states
5. **Bulk scenario creation** - Use Python scripts with configuration files

### Must Remain Manual (Requires Domain Expertise) 
6. **Attack technique definitions** - Requires security expertise
7. **Assumption weight assignments** - Requires understanding of attack vectors
8. **Impact definitions** - Requires risk assessment knowledge

## Tools I've Created For You

### 📁 Strategy Document
- **scenario_generation_strategy.md**: Complete strategy guide with recommendations

### 📁 SPARQL Queries (in sparql_queries/)
1. **generate_scenario_template.sparql**: Generate AssumptionInScenario instances
2. **generate_scenario_definition.sparql**: Generate scenario definition
3. **generate_attack_actions.sparql**: Generate AttackAction instances
4. **list_assumptions_by_category.sparql**: List all assumptions
5. **analyze_technique_weights.sparql**: Analyze weights for techniques
6. **validate_scenario_completeness.sparql**: Check scenario completeness
7. **validate_attack_action_coverage.sparql**: Check attack action coverage

### 📁 Python Scripts
1. **generate_scenarios.py**: Automated scenario generation from config files
2. **generate_attack_actions.py**: Automated AttackAction instance generation

### 📁 Configuration
- **scenario_configs/example_scenarios.json**: 8 example scenario configurations

### 📁 Documentation
- **README_SCENARIO_GENERATION.md**: Complete usage guide

## Recommended Workflow

### Phase 1: Add More Attack Techniques (Manual Work Required)

For each new technique, you need to define:

```turtle
csro:NewAttackTechnique rdf:type owl:NamedIndividual ,
                                 csro:ContainerAttackTechnique ;
                        csro:hasBaseDifficulty csro:Medium ;
                        csro:referencesAttackTechnique d3f:TXXXX ;
                        csro:requiresTrait csro:some_trait ;
                        csro:description "..." .
```

Plus create:
- AssumptionWeight instances (which assumptions affect this technique and how much)
- ExploitabilityCalculationRule
- ExposureCalculationRule

**Estimated effort**: 30-60 minutes per technique depending on complexity

### Phase 2: Create Representative Scenarios (Automated + Manual Config)

#### Option A: Use Python Script (Recommended)

1. Edit `scenario_configs/example_scenarios.json`:
```json
{
  "scenarios": [
    {
      "name": "MyScenario",
      "description": "...",
      "rules": {
        "IMG": "Satisfied",
        "RTS": "Dissatisfied"
      },
      "default": "Unknown"
    }
  ]
}
```

2. Run generator:
```bash
python generate_scenarios.py --config scenario_configs/example_scenarios.json --output new_scenarios.ttl
```

3. Review and merge into csro.ttl

**Estimated effort**: 5-10 minutes per scenario (mostly configuration)

#### Option B: Use SPARQL Queries

1. Run `generate_scenario_template.sparql` to get AssumptionInScenario instances
2. Manually adjust satisfaction states in the output
3. Run `generate_scenario_definition.sparql` to get scenario definition
4. Copy both outputs into csro.ttl

**Estimated effort**: 15-20 minutes per scenario

### Phase 3: Generate AttackActions (Fully Automated)

#### Option A: Python Script
```bash
python generate_attack_actions.py --ontology csro.ttl --output attack_actions.ttl
```

#### Option B: SPARQL Query
Run `generate_attack_actions.sparql` and copy output

**Then manually add** for each AttackAction:
- `csro:affects` properties (which components affected)
- `csro:causesImpact` property (which impact)

**Estimated effort**: 2-5 minutes per attack action for manual properties

### Phase 4: Validate

Run validation queries:
- `validate_scenario_completeness.sparql` - Ensure all assumptions covered
- `validate_attack_action_coverage.sparql` - Ensure all combinations exist

## Recommended Scenario Strategy

Instead of generating all possible combinations, create **meaningful representative scenarios**:

### Suggested Scenarios (15 total)

**Risk-Based (3):**
1. HighRiskScenario - Most controls dissatisfied
2. MediumRiskScenario - Mixed controls
3. LowRiskScenario - Most controls satisfied

**Category-Based (8):**
4. ImageSecurityHardenedScenario - IMG-* satisfied
5. RuntimeSecurityHardenedScenario - RTS-* satisfied
6. NetworkSecurityHardenedScenario - NET-* satisfied
7. AuthenticationHardenedScenario - AUTH-* satisfied
8. SecretsManagementHardenedScenario - SCM-* satisfied
9. HostSecurityHardenedScenario - HIS-* satisfied
10. MonitoringEnabledScenario - MON-* satisfied
11. SupplyChainSecuredScenario - CIC-* satisfied

**Compliance-Based (3):**
12. CISCompliantScenario - CIS benchmark satisfied
13. NISTCompliantScenario - NIST 800-190 satisfied
14. OWASPCompliantScenario - OWASP recommendations satisfied

**Practical (4):**
15. ProductionScenario - Typical production config
16. DevelopmentScenario - Typical dev config
17. MinimalSecurityScenario - Only critical controls
18. FullyHardenedScenario - All controls satisfied

### With Your Current 3 Techniques
- 18 scenarios × 3 techniques = **54 AttackActions**
- Manageable and meaningful!

### When You Add More Techniques
- 18 scenarios × 10 techniques = **180 AttackActions**
- Still manageable with automation tools

## Effort Estimation

### Manual Work (Required)
- **10 new attack techniques**: ~5-10 hours (depending on complexity and weight definitions)
- **Per technique, define**: Technique properties + ~5-15 weights + 2 calculation rules

### Semi-Automated Work
- **18 scenarios**: ~3-4 hours total
  - Configure: ~5 min per scenario × 18 = ~90 minutes
  - Review: ~5 min per scenario × 18 = ~90 minutes

### Fully Automated Work
- **180 AttackActions** (for 10 techniques × 18 scenarios): ~1-2 hours
  - Generation: ~5 minutes (automated)
  - Manual properties (affects, causesImpact): ~0.5 min × 180 = ~90 minutes

### Total Estimated Time
**Approximately 10-15 hours** to:
- Add 10 attack techniques with weights
- Create 18 meaningful scenarios
- Generate 180 attack actions
- Validate and integrate everything

Compare to fully manual: **50+ hours** easily!

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install rdflib
   ```

2. **Start with scenarios**:
   ```bash
   python generate_scenarios.py --config scenario_configs/example_scenarios.json
   ```

3. **Review the generated output**:
   - Open generated_scenarios.ttl
   - Check satisfaction states make sense
   
4. **Add to your ontology**:
   - Copy content to csro.ttl or merge programmatically

5. **Generate attack actions**:
   ```bash
   python generate_attack_actions.py
   ```

6. **Validate**:
   - Run validation SPARQL queries
   - Check for completeness

## Questions Answered

✅ **Do I understand the ontology structure?** Yes! AttackAction combines technique + scenario, with assumptions affecting risk calculations.

✅ **Can we automate instantiations?** Yes! Scenarios and AttackActions can be largely automated.

✅ **Can we use SPARQL queries?** Yes! I've provided 7 SPARQL queries for generation and validation.

✅ **Should we model all combinations?** No! Focus on representative scenarios (15-20 scenarios is plenty).

✅ **What still requires manual work?** Attack technique definitions and assumption weights (domain expertise needed).

## Next Steps

1. Review the strategy document and tools I've created
2. Try generating a few example scenarios with the Python script
3. Add 1-2 new attack techniques manually to test the workflow
4. Generate AttackActions for the new techniques
5. Scale up once you're comfortable with the process

Let me know if you have any questions about the tools or strategy!
