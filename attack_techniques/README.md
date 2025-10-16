# Attack Techniques Workflow

This folder contains tools, data, and documentation for extending CSRO with new container attack techniques.

## 📁 Folder Structure

```
attack_techniques/
├── README.md                  # This file
├── weights/                   # Weight assessment data
│   ├── assumption_weights_matrix.csv
│   ├── assumption_weights_rationales.csv
│   └── assumption_weights.csv
├── scripts/                   # Automation scripts
│   ├── generate_ontology_instances.py
│   ├── merge_instances_to_ontology.py
│   ├── generate_attack_techniques.py
│   ├── merge_technique_labels.py
│   ├── review_weights.py
│   └── review_weights_by_category.py
└── docs/                      # Process documentation
    ├── WEIGHTS_EXPLANATION.md
    ├── scenario_generation_strategy.md
    └── README_SCENARIO_GENERATION.md
```

## 🔄 Workflow Overview

### 1. Add Technique Definitions
Add new `ContainerAttackTechnique` instances to `../../csro.ttl`:
```turtle
csro:NewTechnique rdf:type owl:NamedIndividual ,
                          csro:ContainerAttackTechnique ;
                 rdfs:label "Container New Technique" ;
                 csro:hasBaseDifficulty csro:Medium ;
                 csro:referencesAttackTechnique d3f:TXX ;
                 csro:requiresTrait csro:some_trait ;
                 csro:description "Description of the technique" .
```

**Alternative: Generate technique templates with labels**
```bash
cd scripts
python generate_ontology_instances.py --include-technique-templates
# or
python generate_attack_techniques.py --config techniques.json
```

### 2. Assess Assumption Weights
Use interactive review tools to assess how each security assumption affects the technique:

**Option A: Detailed Review (assumption-by-assumption)**
```bash
cd scripts
python review_weights.py
```

**Option B: Fast Review (category-based)**
```bash
cd scripts
python review_weights_by_category.py
```

Results are saved to:
- `weights/assumption_weights_matrix.csv` (visual matrix)
- `weights/assumption_weights_rationales.csv` (documented decisions)

### 3. Generate Ontology Instances
Convert assessed weights into OWL instances:
```bash
cd scripts
python generate_ontology_instances.py
```

This creates:
- 48 × 2 = 96 `AssumptionWeight` instances per technique
- 2 `CalculationRule` instances per technique (Exploitability + Exposure)

Output: `weights/generated_ontology_instances.ttl`

### 4. Merge into Ontology
Integrate generated instances into the main ontology:
```bash
cd scripts
python merge_instances_to_ontology.py
```

This updates `../../csro.ttl` with the new instances.

## 🏷️ Label Management

Add human-readable labels to existing ContainerAttackTechnique instances:
```bash
cd scripts
python merge_technique_labels.py --ontology ../../csro.ttl --backup
```

This automatically generates labels like:
- `ContainerCgroupDoS` → "Container Cgroup Do S"
- `ContainerKernelModuleLoading` → "Container Kernel Module Loading"
- `ContainerPtraceProcessDiscovery` → "Container Ptrace Process Discovery"

## 📊 Weight Scale

- **0 = No effect**: Assumption has no impact on the attack
- **1 = Low effect**: Minimal impact on attack difficulty/exposure
- **2 = Medium effect**: Moderate impact on attack difficulty/exposure
- **3 = High effect**: Significant impact on attack difficulty/exposure

## 📚 Documentation

- **[WEIGHTS_EXPLANATION.md](docs/WEIGHTS_EXPLANATION.md)**: Detailed explanation of the weight assessment approach
- **[scenario_generation_strategy.md](docs/scenario_generation_strategy.md)**: Strategy for generating attack scenarios
- **[README_SCENARIO_GENERATION.md](docs/README_SCENARIO_GENERATION.md)**: Guide for scenario generation

## 🛠️ Tools

### review_weights.py
Interactive tool for detailed assumption-by-assumption weight review.
- Shows technique description for context
- Reviews exploitability and exposure for each assumption
- Allows updating weights and rationales
- Skip/quit options for workflow control

### review_weights_by_category.py
Fast category-based weight review tool.
- Groups assumptions by category (IMG, RTS, NET, etc.)
- Set default weight/rationale for entire category
- Highlight specific assumptions for exceptions
- Much faster than assumption-by-assumption review

### generate_ontology_instances.py
Converts weight CSV data into OWL Turtle format.
- Reads `assumption_weights_rationales.csv`
- Generates `AssumptionWeight` individuals
- Generates `CalculationRule` individuals
- **New**: `--include-technique-templates` to generate technique templates with labels
- Output: `generated_ontology_instances.ttl`

### generate_attack_techniques.py
Standalone script for generating ContainerAttackTechnique instances.
- Supports JSON configuration files for technique definitions
- Automatically generates human-readable `rdfs:label` properties
- `--add-labels` option to add labels to existing techniques
- `--config` to generate from JSON configuration

### merge_technique_labels.py
Specialized script for adding `rdfs:label` properties to existing techniques.
- Automatically detects techniques that need labels
- Preserves existing ontology structure
- `--backup` creates timestamped backup
- `--dry-run` shows what would be changed

### merge_instances_to_ontology.py
Merges generated instances into the main ontology.
- Replaces old weight instances
- Maintains clean production-ready format
- Updates `csro.ttl` in place

## 📝 Example: Adding a New Technique

```bash
# 1. Add technique definition to csro.ttl manually
# OR generate from template:
cd attack_techniques/scripts
python generate_attack_techniques.py --config new_technique.json

# 2. Add labels to techniques (if needed)
python merge_technique_labels.py --ontology ../../csro.ttl --backup

# 3. Assess weights interactively
python review_weights_by_category.py

# 4. Generate ontology instances
python generate_ontology_instances.py

# 5. Merge into ontology
python merge_instances_to_ontology.py

# 6. Validate (use Protégé or GraphDB)
# 7. Commit changes
```

## 📝 Example: Adding Labels to Existing Techniques

```bash
cd attack_techniques/scripts
python merge_technique_labels.py --ontology ../../csro.ttl --backup --dry-run  # Preview changes
python merge_technique_labels.py --ontology ../../csro.ttl --backup            # Apply changes
```

## 🔍 Querying Weights

Example SPARQL query to get all weights for a technique:
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT ?assumption ?weightType ?value ?rationale
WHERE {
  ?weight csro:refersToAssumption ?assumption ;
          csro:weightValue ?value ;
          csro:effectDescription ?rationale .
  
  ?rule csro:appliesTo csro:YourTechnique ;
        csro:hasWeight ?weight .
  
  ?rule a ?ruleType .
  BIND(IF(?ruleType = csro:ExploitabilityCalculationRule, 
         "Exploitability", "Exposure") AS ?weightType)
}
ORDER BY ?assumption
```

## 🤝 Contributing

When adding new techniques:
1. Follow the existing naming conventions
2. Document rationales for all weight decisions
3. Test scripts after moving files
4. Validate ontology before committing
5. Update this README if workflow changes
