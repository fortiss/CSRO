# Attack Action Generation Guide

This guide explains how to configure and generate AttackAction instances for CSRO.

## Overview

AttackAction instances represent the application of a ContainerAttackTechnique within a specific ContextScenario. The generation process creates all possible technique × scenario combinations automatically, but requires manual configuration of:

1. **Affected Components**: System components targeted by the attack
2. **Impacts**: Security consequences with severity ratings  
3. **Risks**: Associated risks indicated by impacts

## Configuration Process

### 1. Understanding the Technique

Before configuring, review the technique definition in `csro.ttl`:

```turtle
csro:ContainerDataFromLocalSystem rdf:type owl:NamedIndividual ,
                                           csro:ContainerAttackTechnique ;
                 csro:hasBaseDifficulty csro:Medium ;
                 csro:referencesAttackTechnique d3f:T1005 ;
                 csro:requiresTrait csro:some_trait ;
                 csro:description "Container accesses data from local host system..." .
```

Consider:
- What does this technique do?
- What is its goal or intended damage?
- What system parts does it target?
- What security properties does it violate?

### 2. Identifying Affected Components

Available `Component` individuals in CSRO:
- `Application` - The container application itself
- `Device` - The host device/system
- `DeviceOperatingSystem` - The host OS
- `DeviceContainerRuntime` - The container runtime (Docker, containerd, etc.)
- `OtherApplications` - Other containers or applications on the host

**Guidelines:**
- List components that are **directly** affected or compromised
- Include components that are **targets** of the attack
- Include components whose **security properties** are violated

**Examples:**
- Data exfiltration → affects `DeviceOperatingSystem`, `Application`
- Resource exhaustion → affects `Device`, `DeviceContainerRuntime`, `OtherApplications`
- Network interception → affects `OtherApplications`, `DeviceOperatingSystem`

### 3. Defining Impacts

Each impact represents a **security consequence** of the technique being successful.

**Impact Structure:**
```json
{
  "impact_id": "UniqueImpactName",
  "description": "Clear description of what happens",
  "impact_rating": "Critical",
  "risk_id": "AssociatedRiskName",
  "risk_description": "Description of the broader risk"
}
```

**Impact Rating Values:**
- `Negligible` - Minimal security impact, easily recoverable
- `Moderate` - Noticeable impact, requires attention
- `Critical` - Severe impact, immediate response needed
- `Disastrous` - Catastrophic impact, complete compromise

**Guidelines:**
- One technique can have **multiple impacts** (e.g., data theft + system compromise)
- Focus on **direct consequences** of the attack succeeding
- Be specific about **what is compromised**
- Ratings should reflect **worst-case realistic scenario**

**Impact Examples:**

| Technique Type | Impact Example | Rating |
|---|---|---|
| Data Exfiltration | "Sensitive host data accessed and stolen" | Critical |
| Resource DoS | "System resources exhausted, services unavailable" | Moderate |
| Privilege Escalation | "Container gains root access to host" | Disastrous |
| Network Attack | "Network traffic intercepted and modified" | Critical |
| Process Discovery | "Host process information leaked to attacker" | Moderate |

### 4. Associating Risks

Each Impact **indicates** a Risk. The Risk represents the **broader security threat**.

**Risk Guidelines:**
- Risks are **scenario-independent** (context will be added by SPARQL query)
- Focus on **what could happen** if the impact occurs
- Use format: "Risk of [bad thing happening]"

**Examples:**
- Impact: "Host data exfiltrated" → Risk: "Risk of sensitive data breach and compliance violations"
- Impact: "Resource exhaustion" → Risk: "Risk of service disruption and availability loss"
- Impact: "Container escape" → Risk: "Risk of full host compromise and lateral movement"

## Step-by-Step Configuration Example

Let's configure `ContainerKernelModuleLoading`:

### Step 1: Understand the Technique
"Container loads malicious kernel modules to gain host-level persistence and control"

### Step 2: Identify Components
- `DeviceOperatingSystem` - Kernel is part of host OS
- `Device` - Entire host is compromised
- `DeviceContainerRuntime` - Runtime's isolation is bypassed

### Step 3: Define Impacts

**Impact 1: Kernel Compromise**
```json
{
  "impact_id": "KernelModuleCompromise",
  "description": "Malicious kernel module loaded, providing host-level code execution and persistence",
  "impact_rating": "Disastrous",
  "risk_id": "HostKernelCompromiseRisk",
  "risk_description": "Risk of complete host compromise through kernel-level access with persistence"
}
```

**Impact 2: Container Isolation Bypass**
```json
{
  "impact_id": "ContainerIsolationBreak",
  "description": "Container security boundaries completely bypassed through kernel access",
  "impact_rating": "Disastrous",
  "risk_id": "IsolationBreachRisk",
  "risk_description": "Risk of container escape and access to all host resources and other containers"
}
```

### Step 4: Complete Configuration Entry

```json
{
  "technique_id": "ContainerKernelModuleLoading",
  "affected_components": [
    "DeviceOperatingSystem",
    "Device",
    "DeviceContainerRuntime"
  ],
  "impacts": [
    {
      "impact_id": "KernelModuleCompromise",
      "description": "Malicious kernel module loaded, providing host-level code execution and persistence",
      "impact_rating": "Disastrous",
      "risk_id": "HostKernelCompromiseRisk",
      "risk_description": "Risk of complete host compromise through kernel-level access with persistence"
    },
    {
      "impact_id": "ContainerIsolationBreak",
      "description": "Container security boundaries completely bypassed through kernel access",
      "impact_rating": "Disastrous",
      "risk_id": "IsolationBreachRisk",
      "risk_description": "Risk of container escape and access to all host resources and other containers"
    }
  ]
}
```

## Common Patterns

### Pattern 1: Data Theft Techniques
```json
{
  "technique_id": "...",
  "affected_components": ["DeviceOperatingSystem", "Application"],
  "impacts": [
    {
      "impact_id": "DataExfiltration",
      "description": "...",
      "impact_rating": "Critical",
      "risk_id": "DataBreachRisk",
      "risk_description": "..."
    }
  ]
}
```

### Pattern 2: Denial of Service Techniques
```json
{
  "technique_id": "...",
  "affected_components": ["Device", "DeviceContainerRuntime", "OtherApplications"],
  "impacts": [
    {
      "impact_id": "ResourceExhaustion",
      "description": "...",
      "impact_rating": "Moderate",
      "risk_id": "AvailabilityLossRisk",
      "risk_description": "..."
    }
  ]
}
```

### Pattern 3: Privilege Escalation Techniques
```json
{
  "technique_id": "...",
  "affected_components": ["DeviceOperatingSystem", "Device", "DeviceContainerRuntime"],
  "impacts": [
    {
      "impact_id": "PrivilegeEscalation",
      "description": "...",
      "impact_rating": "Disastrous",
      "risk_id": "HostCompromiseRisk",
      "risk_description": "..."
    }
  ]
}
```

### Pattern 4: Network Attack Techniques
```json
{
  "technique_id": "...",
  "affected_components": ["DeviceOperatingSystem", "OtherApplications"],
  "impacts": [
    {
      "impact_id": "NetworkInterception",
      "description": "...",
      "impact_rating": "Critical",
      "risk_id": "DataInterceptionRisk",
      "risk_description": "..."
    }
  ]
}
```

## Validation Checklist

Before running the generation script, verify:

- [ ] All 13 `technique_id` values match ontology instances exactly
- [ ] Each technique has at least one `affected_component`
- [ ] All component names exist in the ontology (`Application`, `Device`, etc.)
- [ ] Each technique has at least one `impact`
- [ ] All `impact_rating` values are: `Negligible`, `Moderate`, `Critical`, or `Disastrous`
- [ ] Each `impact_id` is unique across all techniques
- [ ] Each `risk_id` is unique across all techniques
- [ ] All descriptions are clear and specific
- [ ] JSON syntax is valid (use a JSON validator)

## Testing Your Configuration

1. **Validate JSON syntax:**
   ```bash
   python -m json.tool attack_action_metadata.json
   ```

2. **Run generation (dry-run first):**
   ```bash
   cd scripts
   python generate_attack_actions.py --validate-only
   ```

3. **Review generated output:**
   - Check `configs/generated_attack_actions.ttl`
   - Verify instance names and structure
   - Confirm all relationships are correct

4. **Merge to ontology:**
   ```bash
   python merge_attack_actions_to_ontology.py
   ```

## Tips for Success

1. **Start with one technique**: Configure and generate one technique first to understand the process
2. **Use the example**: Refer to `configs/example_attack_action.json` as a template
3. **Be consistent**: Use similar naming patterns for related impacts/risks
4. **Think scenario-independent**: Don't consider specific scenarios - the SPARQL query handles context
5. **Review existing instances**: Look at Impact/Risk instances already in the ontology for naming conventions
6. **Document your reasoning**: Keep notes on why you chose specific ratings and components

## Troubleshooting

**"Technique not found in ontology"**
- Check spelling of `technique_id`
- Verify technique exists in `csro.ttl`
- Ensure exact case match

**"Invalid component reference"**
- Must be one of: `Application`, `Device`, `DeviceOperatingSystem`, `DeviceContainerRuntime`, `OtherApplications`
- Check spelling and case

**"Invalid impact rating"**
- Must be exactly: `Negligible`, `Moderate`, `Critical`, or `Disastrous`
- Check case sensitivity

**"Duplicate impact/risk ID"**
- Each ID must be unique across all techniques
- Use technique-specific prefixes (e.g., `KernelModule_` prefix for kernel-related impacts)

## Next Steps

After configuration is complete:
1. Run generation script
2. Review generated TTL file
3. Merge into ontology
4. Test SPARQL risk calculation queries
5. Validate with ontology reasoner
