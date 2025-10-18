# CSRO Automation Guide

This document describes the automation approach for generating and maintaining instances in the Container Security Risk Ontology (CSRO).

## Ontology Architecture

The CSRO models container security risks through a layered architecture:

```
ContainerSecurityAssumption (48 assumptions across 8 categories)
    ↓ (via AssumptionInScenario with satisfaction states)
ContextScenario (22 scenarios representing different security postures)
    ↓ (combined with)
ContainerAttackTechnique (15 techniques derived from MITRE ATT&CK)
    ↓ (creates)
AttackAction (330 instances: 15 techniques × 22 scenarios)
    ↓ (causes)
Impact & Risk
```

### Design Principle: Representative Scenarios

Rather than modeling all theoretically possible combinations of assumption satisfaction states (3^48 possibilities), the ontology uses **representative scenarios** that capture meaningful security postures:

- Risk-based scenarios (high, balanced, basic)
- Category-focused scenarios (image security, runtime security, etc.)
- Compliance-based scenarios (CIS, NIST, OWASP)
- Practical deployment scenarios (production, development, edge computing)

This approach balances expressiveness with maintainability.

## Automation Capabilities

### Fully Automated
1. **AssumptionInScenario generation** - Links all assumptions to scenarios with configured satisfaction states
2. **AttackAction generation** - Creates all technique × scenario combinations
3. **AttackAction properties** - Generates component relationships and impact links
4. **Validation** - Completeness and consistency checks

### Semi-Automated (Configuration + Generation)
5. **ContextScenario generation** - Python scripts generate scenarios from JSON configurations
6. **Risk calculation** - SPARQL CONSTRUCT queries generate dynamic risk assessments

### Manual (Domain Expertise Required)
7. **ContainerAttackTechnique definitions** - Requires security domain knowledge
8. **AssumptionWeight assignments** - Requires understanding of attack vectors
9. **Impact and Risk definitions** - Requires risk assessment expertise

## Available Tools and Resources

### Context Scenarios
- **Location**: `context_scenarios/`
- **Scripts**: 
  - `generate_scenarios.py` - Generate scenarios from JSON configuration
  - `merge_scenarios_to_ontology.py` - Merge generated scenarios into csro.ttl
- **Configuration**: `configs/representative_scenarios.json` - Defines 22 representative scenarios
- **Documentation**: `docs/scenario_generation_strategy.md` - Strategy and design rationale

### Attack Techniques
- **Location**: `attack_techniques/`
- **Scripts**:
  - `generate_attack_techniques.py` - Generate technique instances with weights
  - `generate_ontology_instances.py` - Generate technique calculation rules
  - `merge_instances_to_ontology.py` - Merge techniques into csro.ttl
- **Documentation**: `docs/WEIGHTS_EXPLANATION.md` - Weight assignment methodology

### Attack Actions
- **Location**: `attack_actions/`
- **Scripts**:
  - `generate_attack_actions.py` - Generate AttackAction instances
  - `merge_attack_actions_to_ontology.py` - Merge actions into csro.ttl
- **Configuration**: `configs/attack_action_metadata.json` - Define impacts and affected components
- **Documentation**: `docs/attack_action_generation_guide.md` - Detailed workflow guide

### Risk Calculations
- **Location**: `sparql_queries/`
- **Queries**:
  - `calculate_risk_ratings.sparql` - Comprehensive risk assessment CONSTRUCT query
  - `calculate_risk_ratings_optimized_with_feedback.sparql` - Performance-optimized version
- **Purpose**: Generate dynamic risk assessments based on scenario contexts

## Workflow for Extending the Ontology

### Phase 1: Define Attack Techniques

For each new container attack technique:

1. **Define the technique** in the ontology:
   ```turtle
   csro:NewAttackTechnique rdf:type owl:NamedIndividual ,
                                    csro:ContainerAttackTechnique ;
                           csro:hasBaseDifficulty csro:Medium ;
                           csro:referencesAttackTechnique d3f:TXXXX ;
                           csro:requiresTrait csro:some_trait ;
                           csro:description "..." .
   ```

2. **Create assumption weights** - Define how each security assumption affects the technique's exploitability and exposure

3. **Define calculation rules** - Create ExploitabilityCalculationRule and ExposureCalculationRule instances

**Tools**: Manual definition in `csro.ttl` or use `attack_techniques/scripts/` for batch generation

### Phase 2: Create Context Scenarios

#### Recommended Approach: Python Script

1. **Configure scenarios** in `context_scenarios/configs/representative_scenarios.json`:
   ```json
   {
     "scenarios": [
       {
         "name": "ProductionScenario",
         "description": "Typical production deployment with balanced security",
         "rules": {
           "IMG": "Satisfied",
           "RTS": "PartialSatisfied",
           "NET": "Satisfied"
         },
         "default": "Unknown"
       }
     ]
   }
   ```

2. **Generate scenarios**:
   ```bash
   cd context_scenarios/scripts
   python generate_scenarios.py
   ```

3. **Merge into ontology**:
   ```bash
   python merge_scenarios_to_ontology.py
   ```

**Output**: Complete ContextScenario definitions with all AssumptionInScenario links

### Phase 3: Generate Attack Actions

1. **Configure metadata** in `attack_actions/configs/attack_action_metadata.json`:
   ```json
   {
     "attack_techniques": [
       {
         "technique_id": "NewAttackTechnique",
         "affected_components": ["Application", "DeviceOperatingSystem"],
         "impacts": [
           {
             "impact_id": "SomeImpact",
             "description": "Impact description",
             "impact_rating": "Critical",
             "risk_id": "SomeRisk",
             "risk_description": "Risk description"
           }
         ]
       }
     ]
   }
   ```

2. **Generate AttackActions**:
   ```bash
   cd attack_actions/scripts
   python generate_attack_actions.py
   ```

3. **Merge into ontology**:
   ```bash
   python merge_attack_actions_to_ontology.py
   ```

**Output**: AttackAction instances for all technique × scenario combinations with complete property links

### Phase 4: Validate and Calculate Risks

1. **Run risk calculations**:
   ```bash
   # Load csro.ttl into your SPARQL endpoint
   # Execute calculate_risk_ratings.sparql
   ```

2. **Validate coverage**:
   - Check that all techniques have associated actions
   - Verify all scenarios have complete assumption coverage
   - Confirm calculation rules are properly defined

**Output**: Dynamic risk assessment data with exploitability, exposure, and likelihood ratings

## Scenario Strategy

The ontology includes 22 representative scenarios organized by purpose:

### Risk-Based Scenarios (3)
- **HighRiskScenario** - Minimal security controls
- **BalancedContainerSecurityScenario** - Moderate security posture  
- **BasicContainerSecurityScenario** - Basic security controls

### Category-Focused Scenarios (8)
- **ImageSecurityFocusedScenario** - Strong image security (IMG-* satisfied)
- **RuntimeHardenedScenario** - Strong runtime security (RTS-* satisfied)
- **NetworkHardenedScenario** - Strong network security (NET-* satisfied)
- **MonitoringScenario** - Comprehensive monitoring (MON-* satisfied)
- **SupplyChainSecuredScenario** - Secure CI/CD pipeline (CIC-* satisfied)
- **SecretsManagementScenario** - Secure secrets handling (SCM-* satisfied)
- **HostIsolationScenario** - Strong host isolation (HIS-* satisfied)
- **AuthenticationScenario** - Strong authentication (AUTH-* satisfied)

### Compliance-Based Scenarios (3)
- **CISCompliantScenario** - CIS Docker Benchmark compliance
- **NISTCompliantScenario** - NIST 800-190 compliance
- **OWASPTop10CompliantScenario** - OWASP recommendations

### Practical Deployment Scenarios (8)
- **ProductionScenario** - Typical production configuration
- **DevelopmentScenario** - Development environment
- **EdgeComputingScenario** - Resource-constrained edge deployment
- **MicroservicesScenario** - Microservices architecture
- **HybridCloudScenario** - Multi-cloud deployment
- **AirGappedScenario** - Isolated network environment
- **RapidPrototypeScenario** - Fast iteration, minimal security
- **OutdatedContainersScenario** - Legacy systems with outdated components

This approach provides **330 AttackAction instances** (15 techniques × 22 scenarios) with meaningful coverage across different deployment contexts.

## Getting Started

### Prerequisites
```bash
pip install rdflib
```

### Quick Start Example

1. **Generate a new scenario**:
   ```bash
   cd context_scenarios/scripts
   python generate_scenarios.py
   python merge_scenarios_to_ontology.py
   ```

2. **Generate attack actions for new techniques**:
   ```bash
   cd attack_actions/scripts
   python generate_attack_actions.py
   python merge_attack_actions_to_ontology.py
   ```

3. **Calculate risks**:
   Load `csro.ttl` into a SPARQL endpoint and execute `sparql_queries/calculate_risk_ratings.sparql`

## Additional Resources

- **Context Scenarios**: See `context_scenarios/README.md` for detailed scenario generation workflow
- **Attack Techniques**: See `attack_techniques/docs/WEIGHTS_EXPLANATION.md` for weight assignment methodology
- **Attack Actions**: See `attack_actions/docs/attack_action_generation_guide.md` for action generation details
- **Strategy Document**: See `context_scenarios/docs/scenario_generation_strategy.md` for design rationale
