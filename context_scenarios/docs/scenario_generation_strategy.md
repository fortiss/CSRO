# CSRO Ontology: Scenario Generation Strategy

## Current Structure Understanding

### Key Classes
1. **ContainerSecurityAssumption**: Security assumptions (e.g., IMG-1, RTS-1, NET-1)
2. **ContextScenario**: Deployment scenarios (Basic, Hardened, Mixed)
3. **AssumptionInScenario**: Links assumptions to scenarios with satisfaction states (Satisfied, Dissatisfied, Unknown)
4. **ContainerAttackTechnique**: Attack techniques (3 currently)
5. **AttackAction**: Combination of technique + scenario (9 currently: 3×3)
6. **AssumptionWeight**: Weight for each assumption per attack technique
7. **ExploitabilityCalculationRule** & **ExposureCalculationRule**: Rules with weights for risk calculation

### Current State
- **3 Attack Techniques**: ContainerExploitPublicFacingApp, ContainerDataFromLocalSystem, ContainerPtraceInjection
- **3 Scenarios**: BasicScenario, HardenedScenario, MixedScenario
- **9 Attack Actions**: Each technique applied to each scenario
- **~48 Security Assumptions** across 8 categories (from CSV)
- **Currently used in scenarios**: Only 6 assumptions (IMG_1, NET_1, NET_2, RTS_1, RTS_2, RTS_3)

## Challenges & Combinatorial Explosion

### Problem
- With 48 assumptions and 3 satisfaction states (Satisfied, Dissatisfied, Unknown)
- Theoretical combinations: 3^48 ≈ 7.9 × 10^22 scenarios
- Even with 10 assumptions: 3^10 = 59,049 scenarios
- Manual modeling is not feasible

### What Requires Manual Effort
1. **Attack Techniques**: Domain expertise needed for:
   - Identifying relevant MITRE ATT&CK techniques
   - Determining base difficulty
   - Identifying required deployment traits
   - Defining impacts and affected components

2. **Assumption Weights**: For each attack technique, need to define:
   - Which assumptions affect exploitability (and their weights)
   - Which assumptions affect exposure (and their weights)
   - Effect descriptions for each weight

## Recommended Strategy

### Phase 1: Add More Attack Techniques (Manual)
**Continue manual modeling for attack techniques** - this requires domain expertise and cannot be effectively automated.

For each new technique, you need to define:
- Base properties (difficulty, required traits, MITRE reference)
- Exploitability weights (which assumptions matter and how much)
- Exposure weights (which assumptions matter and how much)

### Phase 2: Generate Representative Scenarios (Semi-Automated)

Instead of all combinations, create **meaningful representative scenarios**:

#### Approach A: Category-Based Scenarios
Create scenarios based on assumption categories:
- **ImageSecurityHardened**: All IMG-* assumptions satisfied
- **RuntimeSecurityHardened**: All RTS-* assumptions satisfied
- **NetworkSecurityHardened**: All NET-* assumptions satisfied
- **FullyHardened**: All assumptions satisfied
- **FullyUnsecured**: All assumptions dissatisfied
- **Production**: Typical production configuration
- **Development**: Typical development configuration

#### Approach B: Risk-Level Based Scenarios
Create scenarios representing different risk postures:
- **HighRisk**: Critical assumptions dissatisfied
- **MediumRisk**: Mix of satisfied/dissatisfied
- **LowRisk**: Most critical assumptions satisfied
- **Minimal**: Only bare minimum satisfied

#### Approach C: Compliance-Based Scenarios
Create scenarios based on compliance standards:
- **CISCompliant**: All CIS Docker Benchmark related assumptions satisfied
- **NISTCompliant**: All NIST SP 800-190 assumptions satisfied
- **OWASPCompliant**: All OWASP recommendations satisfied

### Phase 3: Auto-Generate Attack Actions (Fully Automated)

Once you have N attack techniques and M scenarios, automatically generate N×M attack actions.

## Implementation with SPARQL

### Query 1: Count All Security Assumptions
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT (COUNT(?assumption) as ?count)
WHERE {
  ?assumption a csro:ContainerSecurityAssumption .
}
```

### Query 2: List Assumptions by Category
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT ?category ?assumptionId ?description
WHERE {
  ?assumption a csro:ContainerSecurityAssumption ;
              csro:belongsToCategory ?category ;
              csro:assumptionId ?assumptionId ;
              csro:description ?description .
}
ORDER BY ?category ?assumptionId
```

### Query 3: Generate AssumptionInScenario Instances (Template)
This generates the Turtle syntax for creating AssumptionInScenario instances for a new scenario:

```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT 
  (CONCAT("csro:", ?scenarioName, "_", ?assumptionId) AS ?instanceName)
  (CONCAT("###  https://w3id.org/csro/ontology#", ?scenarioName, "_", ?assumptionId, "\n",
          "csro:", ?scenarioName, "_", ?assumptionId, " rdf:type owl:NamedIndividual ,\n",
          "                                  csro:AssumptionInScenario ;\n",
          "                         csro:forAssumption csro:", ?assumptionId, " ;\n",
          "                         csro:hasSatisfactionState csro:", ?satisfactionState, " .\n\n") AS ?turtle)
WHERE {
  ?assumption a csro:ContainerSecurityAssumption ;
              csro:assumptionId ?assumptionId .
  
  # Replace these values for your scenario
  BIND("NewScenario" AS ?scenarioName)
  BIND("Unknown" AS ?satisfactionState)  # or Satisfied, Dissatisfied
}
ORDER BY ?assumptionId
```

### Query 4: Generate Complete Scenario (Template)
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT 
  (CONCAT(
    "###  https://w3id.org/csro/ontology#", ?scenarioName, "\n",
    "csro:", ?scenarioName, " rdf:type owl:NamedIndividual ,\n",
    "                            csro:ContextScenario ;\n",
    "                   csro:includes csro:Application ,\n",
    "                                 csro:Device ,\n",
    "                                 csro:DeviceContainerRuntime ,\n",
    "                                 csro:DeviceOperatingSystem ,\n",
    "                                 csro:OtherApplications ;\n",
    "                   csro:includesAssumption ",
    GROUP_CONCAT(CONCAT("csro:", ?scenarioName, "_", ?assumptionId); separator=" ,\n                                           "),
    " ;\n",
    "                   csro:description \"", ?description, "\" .\n\n"
  ) AS ?scenarioTurtle)
WHERE {
  ?assumption a csro:ContainerSecurityAssumption ;
              csro:assumptionId ?assumptionId .
  
  # Configure your scenario
  BIND("CategoryBasedScenario" AS ?scenarioName)
  BIND("Scenario description here" AS ?description)
}
GROUP BY ?scenarioName ?description
```

### Query 5: Generate Attack Actions for All Technique-Scenario Combinations
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?techniqueName ?scenarioName
  (CONCAT(?techniqueName, "Attack_", ?scenarioName) AS ?attackActionName)
  (CONCAT(
    "###  https://w3id.org/csro/ontology#", ?techniqueName, "Attack_", ?scenarioName, "\n",
    "csro:", ?techniqueName, "Attack_", ?scenarioName, " rdf:type owl:NamedIndividual ,\n",
    "                                                                  csro:AttackAction ;\n",
    "                                                         csro:appliesTechnique csro:", ?techniqueName, " ;\n",
    "                                                         csro:inContext csro:", ?scenarioName, " ;\n",
    "                                                         # TODO: Add csro:affects and csro:causesImpact properties\n",
    "                                                         csro:description \"", ?techniqueName, " attack applied in ", ?scenarioName, "\" .\n\n"
  ) AS ?turtle)
WHERE {
  ?technique a csro:ContainerAttackTechnique .
  ?scenario a csro:ContextScenario .
  
  # Extract local names
  BIND(REPLACE(STR(?technique), ".*#", "") AS ?techniqueName)
  BIND(REPLACE(STR(?scenario), ".*#", "") AS ?scenarioName)
}
ORDER BY ?techniqueName ?scenarioName
```

### Query 6: Find Assumptions Relevant to a Specific Attack Technique
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT DISTINCT ?assumptionId ?weightValue ?effectDescription
WHERE {
  {
    # From exploitability rules
    ?rule a csro:ExploitabilityCalculationRule ;
          csro:appliesTo csro:ContainerExploitPublicFacingApp ;
          csro:hasWeight ?weight .
  } UNION {
    # From exposure rules
    ?rule a csro:ExposureCalculationRule ;
          csro:appliesTo csro:ContainerExploitPublicFacingApp ;
          csro:hasWeight ?weight .
  }
  
  ?weight csro:refersToAssumption ?assumption ;
          csro:weightValue ?weightValue ;
          csro:effectDescription ?effectDescription .
  
  ?assumption csro:assumptionId ?assumptionId .
}
ORDER BY DESC(?weightValue) ?assumptionId
```

## Practical Workflow

### Step 1: Define New Attack Technique (Manual)
```turtle
csro:NewAttackTechnique rdf:type owl:NamedIndividual ,
                                 csro:ContainerAttackTechnique ;
                        csro:hasBaseDifficulty csro:Medium ;
                        csro:referencesAttackTechnique d3f:TXXXX ;
                        csro:requiresTrait csro:some_trait ;
                        csro:description "Description..." .
```

### Step 2: Define Weights for New Technique (Manual)
Define AssumptionWeight instances and calculation rules (exploitability and exposure).

### Step 3: Create New Scenario (Semi-Automated)
1. Use Query 3 to generate all AssumptionInScenario instances
2. Manually adjust satisfaction states based on scenario concept
3. Use Query 4 to generate scenario definition

### Step 4: Generate Attack Actions (Automated)
Use Query 5 to generate all AttackAction instances for technique-scenario combinations.

### Step 5: Use Python Script for Bulk Generation
Create a Python script using RDFLib to:
1. Load current ontology
2. Generate new scenarios programmatically
3. Generate attack actions
4. Export as new Turtle file or append to existing

## Python Script Template

```python
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from itertools import product

# Load ontology
g = Graph()
g.parse("csro.ttl", format="turtle")

CSRO = Namespace("https://w3id.org/csro/ontology#")

# Get all assumptions
assumptions = list(g.subjects(RDF.type, CSRO.ContainerSecurityAssumption))

# Define new scenario
scenario_name = "NetworkHardenedScenario"
scenario_uri = CSRO[scenario_name]

# Add scenario
g.add((scenario_uri, RDF.type, CSRO.ContextScenario))
g.add((scenario_uri, CSRO.description, Literal("Scenario with network security hardened")))

# Define satisfaction states by category
satisfaction_rules = {
    "NET": CSRO.Satisfied,
    "IMG": CSRO.Dissatisfied,
    "RTS": CSRO.Unknown,
    # ... etc
}

# Add AssumptionInScenario instances
for assumption in assumptions:
    assumption_id = str(g.value(assumption, CSRO.assumptionId))
    category_prefix = assumption_id.split("-")[0]
    
    ais_name = f"{scenario_name}_{assumption_id.replace('-', '_')}"
    ais_uri = CSRO[ais_name]
    
    satisfaction = satisfaction_rules.get(category_prefix, CSRO.Unknown)
    
    g.add((ais_uri, RDF.type, CSRO.AssumptionInScenario))
    g.add((ais_uri, CSRO.forAssumption, assumption))
    g.add((ais_uri, CSRO.hasSatisfactionState, satisfaction))
    g.add((scenario_uri, CSRO.includesAssumption, ais_uri))

# Save
g.serialize("csro_extended.ttl", format="turtle")
```

## Recommended Next Steps

1. **Short term**: 
   - Add 5-10 more attack techniques manually
   - For each, define weights based on domain expertise
   
2. **Medium term**: 
   - Create 10-15 meaningful scenarios (category-based, risk-based, compliance-based)
   - Use SPARQL queries to generate AssumptionInScenario instances
   - Manually adjust satisfaction states
   
3. **Long term**: 
   - Develop Python/RDFLib scripts for automated scenario generation
   - Create scenario templates library
   - Implement validation queries to check consistency

## Validation Queries

### Check Scenarios Have All Assumptions
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT ?scenario (COUNT(DISTINCT ?ais) as ?assumptionCount)
WHERE {
  ?scenario a csro:ContextScenario ;
            csro:includesAssumption ?ais .
}
GROUP BY ?scenario
```

### Check Attack Actions Cover All Combinations
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT ?technique ?scenario
  (EXISTS {
    ?action a csro:AttackAction ;
            csro:appliesTechnique ?technique ;
            csro:inContext ?scenario .
  } AS ?hasAction)
WHERE {
  ?technique a csro:ContainerAttackTechnique .
  ?scenario a csro:ContextScenario .
}
ORDER BY ?technique ?scenario
```

## Summary

**Yes, you can automate scenario generation!** But be strategic:

1. ✅ **Automate**: AssumptionInScenario instance creation, AttackAction generation
2. 🔧 **Semi-automate**: Scenario definitions (template + manual satisfaction state configuration)
3. ❌ **Keep manual**: Attack technique definitions, assumption weight assignments

Focus on creating **meaningful, representative scenarios** rather than exhaustive combinations. Use SPARQL queries and Python scripts to reduce repetitive work while maintaining domain expertise where it matters.
