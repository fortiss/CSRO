# Context Scenarios

This folder contains tools, configurations, and documentation for generating CSRO context scenarios that represent different deployment environments and security postures.

## 📁 Folder Structure

```
context_scenarios/
├── README.md                          # This file
├── configs/                           # Scenario configurations
│   ├── representative_scenarios.json  # 20 representative scenarios
│   └── example_scenarios.json         # Basic examples
├── scripts/                           # Generation scripts
│   └── generate_scenarios.py          # Scenario generator tool
└── docs/                              # Process documentation
    ├── README_SCENARIO_GENERATION.md
    └── scenario_generation_strategy.md
```

## 🎯 Overview

Context scenarios represent different deployment environments with varying security control implementations. Each scenario defines the satisfaction state of all 48 security assumptions, which directly affects the calculated risk ratings for attack techniques.

## 📋 Representative Scenarios

The `representative_scenarios.json` configuration includes 20 diverse scenarios covering:

### **Production & Compliance**
- **ProductionScenario**: Comprehensive security controls per best practices
- **CISCompliantScenario**: Full CIS Benchmark compliance
- **ComplianceFocusedScenario**: Regulatory compliance (HIPAA, PCI-DSS)
- **ZeroTrustScenario**: Zero trust architecture implementation

### **Development & Testing**
- **DevelopmentScenario**: Minimal security for ease of development
- **RapidPrototypeScenario**: Speed prioritized over security
- **MinimalSecurityScenario**: Only critical controls implemented

### **Architecture Patterns**
- **CloudNativeScenario**: Modern cloud-native with service mesh
- **MicroservicesScenario**: Service-to-service authentication focus
- **EdgeComputingScenario**: Edge deployment constraints
- **MultiTenantScenario**: Strict isolation for multi-tenancy
- **HybridCloudScenario**: Mixed on-premises and cloud controls

### **Specialized Deployments**
- **NetworkHardenedScenario**: Strong network security focus
- **RuntimeHardenedScenario**: Strong runtime protection focus
- **ImageSecurityFocusedScenario**: Container image security focus
- **CICDIntegratedScenario**: Security throughout CI/CD pipeline
- **AirGappedScenario**: No external connectivity

### **Risk Scenarios**
- **HighRiskScenario**: Worst-case with minimal controls
- **LegacySystemScenario**: Outdated security practices
- **BalancedSecurityScenario**: Moderate controls across categories

## 🔄 Workflow

### 0. Setup Python Environment (First Time Only)

Create and activate a virtual environment with required dependencies:

**Windows (PowerShell)**:
```powershell
# Navigate to context_scenarios folder
cd context_scenarios

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Linux/MacOS (Bash)**:
```bash
# Navigate to context_scenarios folder
cd context_scenarios

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note**: After initial setup, you only need to activate the virtual environment before running scripts:
- Windows: `.\venv\Scripts\Activate.ps1`
- Linux/MacOS: `source venv/bin/activate`

### 1. Configure Scenarios

Edit or create JSON configuration files in `configs/`:

```json
{
  "scenarios": [
    {
      "name": "YourScenario",
      "description": "Description of the scenario",
      "rules": {
        "IMG": "Satisfied",
        "RTS": "Dissatisfied",
        "NET": "Unknown"
      },
      "default": "Unknown"
    }
  ]
}
```

**Configuration Options:**

- **Category rules**: Set satisfaction state for entire assumption categories (IMG, RTS, NET, AUTH, SCM, HIS, MON, CIC, CRM)
- **Explicit mapping**: Set individual assumption satisfaction states using `satisfaction_map`
- **Default state**: Fallback for assumptions not covered by rules or explicit mapping

### 2. Generate Scenario Instances

**Important**: Make sure the virtual environment is activated first (see step 0).

Run the generator script to create OWL Turtle format instances:

**Windows (PowerShell)**:
```powershell
cd scripts

# Generate from representative scenarios
python generate_scenarios.py --config ..\configs\representative_scenarios.json --output ..\configs\generated_scenarios.ttl

# Generate from example scenarios
python generate_scenarios.py --config ..\configs\example_scenarios.json --output ..\configs\example_generated.ttl

# Generate single example scenario (no config)
python generate_scenarios.py
```

**Linux/MacOS (Bash)**:
```bash
cd scripts

# Generate from representative scenarios
python generate_scenarios.py --config ../configs/representative_scenarios.json --output ../configs/generated_scenarios.ttl

# Generate from example scenarios
python generate_scenarios.py --config ../configs/example_scenarios.json --output ../configs/example_generated.ttl

# Generate single example scenario (no config)
python generate_scenarios.py
```

### 3. Merge into Ontology

After reviewing the generated scenarios, merge them into the main ontology:

**Windows (PowerShell)**:
```powershell
# Review the generated file first
code ..\configs\generated_scenarios.ttl

# Merge into ontology (creates automatic backup)
python merge_scenarios_to_ontology.py

# If you want to skip backup creation
python merge_scenarios_to_ontology.py --no-backup
```

**Linux/MacOS (Bash)**:
```bash
# Review the generated file first
cat ../configs/generated_scenarios.ttl

# Merge into ontology (creates automatic backup)
python merge_scenarios_to_ontology.py

# If you want to skip backup creation
python merge_scenarios_to_ontology.py --no-backup
```

**Note**: The merge script automatically:
- Creates a backup of `csro.ttl` (as `csro.ttl.backup`) unless `--no-backup` is used
- **Preserves all existing scenarios** (e.g., BasicScenario, MixedScenario, HardenedScenario)
- **Only adds new scenarios** that don't already exist in the ontology
- Skips scenarios with duplicate names to avoid conflicts
- Preserves all other ontology content

### 4. Validate and Test

- Load `csro.ttl` in Protégé or GraphDB
- Run reasoner to validate consistency
- Test SPARQL queries (see `../../sparql_queries/`)

## 📊 Satisfaction States

Each security assumption in a scenario can have one of three states:

- **Satisfied**: Security control is properly implemented
- **Dissatisfied**: Security control is not implemented or ineffective
- **Unknown**: Implementation state is unclear or mixed

These states directly affect risk calculations:
- Satisfied = 1.0 (full security score contribution)
- Unknown = 0.5 (partial security score contribution)
- Dissatisfied = 0.0 (no security score contribution)

## 🛠️ Scripts

### **generate_scenarios.py**

Creates complete scenario instances including:

- `ContextScenario` individual with description
- Component inclusions (Application, Device, Runtime, OS, etc.)
- 48 `AssumptionInScenario` instances (one per security assumption)
- Satisfaction state assignments based on configuration

**Dependencies:**
- Python 3.8 or higher
- rdflib >= 7.0.0 (specified in `requirements.txt`)

**Key Features:**
- Category-based rules (set entire categories at once)
- Explicit assumption mapping (override individual assumptions)
- Default state for unconfigured assumptions
- Automatic assumption discovery from ontology
- Clean OWL Turtle output format

### **merge_scenarios_to_ontology.py**

Merges generated scenario instances into the main CSRO ontology file.

**Features:**
- Automatic backup creation (optional)
- **Preserves existing scenarios** - does not overwrite
- **Only adds new scenarios** - skips duplicates
- Intelligent scenario detection and extraction
- Safe and idempotent operation
- Detailed merge summary with preserved/added counts

**Usage:**
```bash
cd scripts
python merge_scenarios_to_ontology.py                    # Merge with backup
python merge_scenarios_to_ontology.py --no-backup        # Merge without backup
```

## 📝 Example: Creating a Custom Scenario

```json
{
  "scenarios": [
    {
      "name": "CustomTestScenario",
      "description": "My custom test scenario",
      "rules": {
        "IMG": "Satisfied",
        "RTS": "Satisfied",
        "NET": "Dissatisfied"
      },
      "satisfaction_map": {
        "NET-1": "Satisfied",
        "NET-2": "Satisfied"
      },
      "default": "Unknown"
    }
  ]
}
```

This creates a scenario where:
- All IMG assumptions are Satisfied
- All RTS assumptions are Satisfied
- NET-1 and NET-2 are Satisfied (explicit overrides)
- Other NET assumptions are Dissatisfied (category rule)
- All other assumptions are Unknown (default)

## 🔍 Using Scenarios for Risk Assessment

Once scenarios are in the ontology, use SPARQL queries to calculate risks:

```bash
# Calculate complete risk assessments
cd ../../sparql_queries
# Run calculate_risk_ratings.sparql in your SPARQL endpoint

# View calculation examples
# Run calculation_example.sparql

# Export calculation rules
# Run calculation_rules_export.sparql
```

See `../../sparql_queries/` for comprehensive risk calculation queries.

## 📚 Documentation

- **[README_SCENARIO_GENERATION.md](docs/README_SCENARIO_GENERATION.md)**: Detailed scenario generation guide
- **[scenario_generation_strategy.md](docs/scenario_generation_strategy.md)**: Strategy and methodology

## 🤝 Contributing

When adding new scenarios:
1. Consider representativeness of real-world deployments
2. Provide clear descriptions explaining the security posture
3. Document assumptions about the environment
4. Test scenarios with risk calculation queries
5. Validate generated instances with reasoner

## 💡 Best Practices

- **Virtual Environment**: Always use the virtual environment to avoid dependency conflicts
- **Diverse Scenarios**: Cover wide range of security postures
- **Realistic Configurations**: Base on actual deployment patterns
- **Clear Naming**: Use descriptive scenario names
- **Document Rationale**: Explain why certain assumptions are satisfied/dissatisfied
- **Test Thoroughly**: Validate with SPARQL queries before committing
- **Version Control**: Track configuration changes in Git (but exclude `venv/` folder)

## 🔗 Related

- **Attack Techniques**: `../attack_techniques/` - Attack technique definitions and weights
- **SPARQL Queries**: `../sparql_queries/` - Risk calculation queries
- **Main Ontology**: `../csro.ttl` - CSRO ontology file
