# Container Security Assumptions

This folder contains the comprehensive list of container security assumptions for the CSRO ontology, along with their corresponding risk treatments and automation scripts for generating RiskTreatment instances.

## 📁 Folder Structure

```
container_security_assumptions/
├── README.md                          # This file
├── container_security_assumptions.csv # Master list of assumptions and treatments
├── configs/                           # Generated configurations
│   └── generated_risk_treatments.ttl  # Generated RiskTreatment instances
└── scripts/                           # Generation scripts
    ├── generate_risk_treatments.py    # Generate RiskTreatment instances
    └── merge_risk_treatments_to_ontology.py # Merge treatments into csro.ttl
```

## 🎯 Overview

Container security assumptions represent fundamental security controls and practices that can be implemented in containerized environments. Each assumption has:

- **Unique ID**: Identifier following category-number pattern (e.g., IMG-1, RTS-3)
- **Category**: Security domain classification
- **Description**: What the assumption represents
- **Risk Treatment**: Corresponding mitigation strategy with implementation guidance
- **Standards Mapping**: References to NIST SP 800-190, CIS Docker Benchmark, OWASP guidelines

## 📋 Security Assumption Categories

The framework includes **48 security assumptions** across **9 categories**:

### **🖼️ Container Image Security (IMG)** - 6 assumptions
- **IMG-1**: App images are scanned for vulnerabilities
- **IMG-2**: App uses minimal base images
- **IMG-3**: App images are signed and verified
- **IMG-4**: Dockerfiles pin base image versions
- **IMG-5**: App images are rebuilt and updated regularly
- **IMG-6**: Device orchestration only uses trusted image registries

### **⚡ Runtime Security (RTS)** - 7 assumptions
- **RTS-1**: App containers run as non-root user
- **RTS-2**: App containers use read-only file systems
- **RTS-3**: App containers deployed with minimal Linux capabilities
- **RTS-4**: Seccomp is implemented on the device
- **RTS-5**: AppArmor is implemented on the device
- **RTS-6**: SELinux is implemented on the device
- **RTS-7**: App containers have minimal access to host resources

### **🔐 Authentication & Access (AUTH)** - 3 assumptions
- **AUTH-1**: Authentication for exposed container APIs is enforced
- **AUTH-2**: Role-based access control is used for orchestration and container management
- **AUTH-3**: Access to container management interfaces is restricted

### **🌐 Network Security (NET)** - 4 assumptions
- **NET-1**: App container networks are segmented
- **NET-2**: Host-level firewall rules and network policies are applied
- **NET-3**: Inter-container communication is encrypted
- **NET-4**: Ingress/egress controls for containers are implemented

### **🔑 Secrets & Configuration Management (SCM)** - 4 assumptions
- **SCM-1**: Secrets are managed using dedicated secret management tools
- **SCM-2**: Environment variables containing secrets are avoided
- **SCM-3**: Configuration files are secured and access-controlled
- **SCM-4**: Container configuration is validated against security baselines

### **🏛️ Host Infrastructure Security (HIS)** - 3 assumptions
- **HIS-1**: Host operating system is hardened according to security benchmarks
- **HIS-2**: Host system updates and patches are applied regularly
- **HIS-3**: Host access is restricted and monitored

### **👁️ Monitoring, Detection & Response (MON)** - 8 assumptions
- **MON-1**: Container runtime activities are monitored and logged
- **MON-2**: Processes on the host device are monitored for anomalous behavior
- **MON-3**: Runtime security tools (e.g. Falco, Trivy) are used
- **MON-4**: Incident response procedures are implemented
- **MON-5**: Logs are centralized and protected
- **MON-6**: Decoy containers (honeypots) are deployed to detect malicious activity
- **MON-7**: Container API calls and orchestration events are monitored for anomalies
- **MON-8**: Alerts are triggered for unauthorized access attempts

### **🔄 CI/CD & Supply Chain (CIC)** - 6 assumptions
- **CIC-1**: The CI/CD pipeline for the app is secured
- **CIC-2**: SBOMs are used for the app to track code dependencies
- **CIC-3**: Code reviews and automated testing of the app are enforced
- **CIC-4**: Third-party components used by the app are validated
- **CIC-5**: The CI/CD pipeline enables reproducible builds
- **CIC-6**: Apps for development and production are not deployed in the same environment

### **📊 Compliance & Risk Management (CRM)** - 7 assumptions
- **CRM-1**: Regular risk assessments of apps and host devices are performed
- **CRM-2**: The operation's asset inventory is maintained
- **CRM-3**: Container security policies along the app lifecycle are documented and enforced
- **CRM-4**: Periodic audits and reviews of apps and host devices are conducted
- **CRM-5**: Compliance with relevant standards and regulations is maintained
- **CRM-6**: Security metrics and KPIs are tracked and reported
- **CRM-7**: Business continuity and disaster recovery plans include container infrastructure

## 🔄 Workflow

### 1. Review and Update Assumptions

Edit the `container_security_assumptions.csv` file to:
- Add new security assumptions
- Update treatment descriptions
- Map to additional security standards
- Modify assumption categorization

**CSV Structure:**
```csv
Assumption ID;Security Assumption Category;Security Assumption;Treatment ID;Treatment Description;NIST SP 800-190;CIS Docker Benchmark;OWASP Docker Top 10;OWASP Docker Security Cheat Sheet
IMG-1;Container Image Security;App images are scanned for vulnerabilities;ScanContainerImages;Perform vulnerability scanning...;§4.1.1;4.4;;#9, #13
```

### 2. Generate RiskTreatment Instances

Convert the CSV data into OWL Turtle format:

```bash
cd scripts
python generate_risk_treatments.py
```

**Options:**
```bash
# Generate with custom output path
python generate_risk_treatments.py --output ../configs/custom_treatments.ttl

# Generate from custom CSV
python generate_risk_treatments.py --csv ../custom_assumptions.csv
```

This creates RiskTreatment instances with:
- Human-readable `rdfs:label` properties
- `csro:addresses` relationships to ContainerSecurityAssumption instances
- `csro:description` with implementation guidance

### 3. Merge into Ontology

Integrate generated treatments into the main ontology:

```bash
cd scripts
python merge_risk_treatments_to_ontology.py
```

**Features:**
- **Preserves existing treatments** with their guidelines and implementation relationships
- **Only adds new treatments** that don't already exist
- **Updates missing properties** (description, addresses) for existing treatments
- **Creates automatic backup** with timestamp
- **Safe and idempotent operation**

## 🏷️ Risk Treatment Labels

The script automatically generates human-readable labels from treatment IDs:

**Examples:**
- `ScanContainerImages` → "Scan Container Images"
- `UseMinimalBaseImages` → "Use Minimal Base Images"
- `ImplementRBAC` → "Implement R B A C"
- `EnforceAPIAuthentication` → "Enforce A P I Authentication"

## 📊 Standards Mapping

Each assumption includes references to major container security frameworks:

### **NIST SP 800-190** - Application Container Security Guide
- Comprehensive security guidance for container technologies
- Section references (e.g., §4.1.1, §4.3.2)

### **CIS Docker Benchmark**
- Industry-standard security configuration baselines
- Control references (e.g., 2.5, 4.3, 5.24)

### **OWASP Docker Top 10**
- Common security risks in Docker deployments
- Risk identifiers (e.g., D01, D04, D08)

### **OWASP Docker Security Cheat Sheet**
- Practical security implementation guidelines
- Recommendation numbers (e.g., #2, #9, #13)

## 🛠️ Scripts

### **generate_risk_treatments.py**

Converts the CSV data into OWL Turtle format RiskTreatment instances.

**Features:**
- Automatic label generation from treatment IDs
- Proper relationships to ContainerSecurityAssumption instances
- Clean OWL Turtle output with full prefixes
- Category-based statistics and reporting

**Dependencies:**
- Python 3.8 or higher
- Standard library only (csv, argparse, pathlib)

### **merge_risk_treatments_to_ontology.py**

Safely merges generated treatments into the main CSRO ontology.

**Features:**
- **Smart merging**: Preserves existing treatments and their relationships
- **Relationship preservation**: Maintains `hasGuideline` and `isImplementedBy` properties
- **Selective updates**: Only adds missing `description` and `addresses` properties
- **Backup creation**: Automatic timestamped backups
- **Detailed reporting**: Shows what was preserved, added, or updated

**Merge Logic:**
- If treatment exists and has all properties → **Skip** (preserve as-is)
- If treatment exists but missing properties → **Update** (add missing properties only)
- If treatment doesn't exist → **Add** (create complete new instance)

## 📝 Example: Adding a New Assumption

1. **Add to CSV:**
```csv
RTS-8;Runtime Security;App containers use resource limits;ConfigureResourceLimits;Configure CPU and memory limits for containers to prevent resource exhaustion;§4.4.3;5.26;;#7
```

2. **Generate treatments:**
```bash
cd scripts
python generate_risk_treatments.py
```

3. **Merge into ontology:**
```bash
python merge_risk_treatments_to_ontology.py
```

4. **Result in ontology:**
```turtle
csro:ConfigureResourceLimits rdf:type owl:NamedIndividual ,
                                      csro:RiskTreatment ;
                             csro:addresses csro:RTS_8 ;
                             csro:description "Configure CPU and memory limits for containers to prevent resource exhaustion" ;
                             rdfs:label "Configure Resource Limits" .
```

## 🔍 Querying Assumptions and Treatments

### Get all assumptions by category:
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT ?assumption ?assumptionId ?description
WHERE {
  ?assumption a csro:ContainerSecurityAssumption ;
              csro:assumptionId ?assumptionId ;
              csro:description ?description .
  FILTER(STRSTARTS(?assumptionId, "IMG"))
}
ORDER BY ?assumptionId
```

### Get treatments with their assumptions:
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?treatment ?treatmentLabel ?assumption ?assumptionId
WHERE {
  ?treatment a csro:RiskTreatment ;
             rdfs:label ?treatmentLabel ;
             csro:addresses ?assumption .
  ?assumption csro:assumptionId ?assumptionId .
}
ORDER BY ?assumptionId
```

### Get implementation status:
```sparql
PREFIX csro: <https://w3id.org/csro/ontology#>

SELECT ?treatment ?guideline ?implementation
WHERE {
  ?treatment a csro:RiskTreatment .
  OPTIONAL { ?treatment csro:hasGuideline ?guideline }
  OPTIONAL { ?treatment csro:isImplementedBy ?implementation }
}
```

## 📚 Security Framework Integration

The assumptions directly support:

### **Risk Assessment**
- Each assumption affects attack technique exploitability and exposure
- Satisfaction states (Satisfied/Dissatisfied/Unknown) impact risk calculations
- Used in context scenarios to model different security postures

### **Compliance Mapping**
- Traceable to major security frameworks and standards
- Support for regulatory compliance requirements
- Gap analysis capabilities through assumption satisfaction tracking

### **Treatment Planning**
- Each assumption has corresponding implementation guidance
- Treatments can be linked to specific guidelines and tools
- Implementation tracking through `isImplementedBy` relationships

## 🤝 Contributing

When adding new assumptions:

1. **Follow naming conventions**: `CATEGORY-NUMBER` format for assumption IDs
2. **Use clear descriptions**: Focus on what can be verified/measured
3. **Provide actionable treatments**: Include specific implementation guidance
4. **Map to standards**: Reference relevant security frameworks
5. **Test generation**: Validate CSV format and generation scripts
6. **Update documentation**: Keep this README current with changes

## 💡 Best Practices

- **Assumption Clarity**: Write assumptions as verifiable statements
- **Treatment Specificity**: Provide concrete implementation steps
- **Standards Alignment**: Maintain consistency with referenced frameworks
- **Category Balance**: Distribute assumptions evenly across security domains
- **Version Control**: Track changes to assumptions and their rationales
- **Validation**: Test CSV parsing and generation after modifications

## 🔗 Related

- **Context Scenarios**: `../context_scenarios/` - Scenario-based assumption satisfaction
- **Attack Techniques**: `../attack_techniques/` - Weights and impacts based on assumptions
- **SPARQL Queries**: `../sparql_queries/` - Risk calculation and analysis queries
- **Main Ontology**: `../csro.ttl` - CSRO ontology with integrated assumptions and treatments
