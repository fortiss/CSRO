# Container Attack Technique Assumption Weights - Explanation

This document explains the proposed weight values in `assumption_weights.csv` for each attack technique and security assumption combination.

## Weight Scale

- **0 = No effect**: The assumption has no impact on this technique
- **1 = Low effect**: Minor impact on attack success
- **2 = Medium effect**: Moderate impact on attack success  
- **3 = High effect**: Significant impact on attack success

## Column Format

Each assumption has **two columns**:
- **(Exploit)**: Impact on **exploitability** - how difficult it is to execute the attack
- **(Expose)**: Impact on **exposure** - how likely the attack is to reach the target

## Existing Techniques (Already Defined)

### 1. ContainerExploitPublicFacingApp (T1190)
**Existing weights from ontology:**
- IMG-1 (Exploit): 2 - Vulnerability scanning reduces exploitable vulnerabilities
- NET-2 (Expose): 3 - Firewall rules critical for restricting external access
- NET-1 (Expose): 0 - External network required for attack, so segmentation doesn't help

### 2. ContainerDataFromLocalSystem (T1005)
**Existing weights from ontology:**
- IMG-1 (Exploit): 2 - Scanning helps identify vulnerable images
- RTS-1 (Exploit): 3 - Non-root user significantly limits file access
- RTS-2 (Exploit): 0 - Read-only filesystem doesn't prevent reading
- RTS-3 (Exploit): 3 - Dropped capabilities prevent file operations
- NET-1 (Expose): 2 - Segmentation restricts access to privileged container
- NET-2 (Expose): 2 - Firewall rules also restrict access

### 3. ContainerPtraceInjection (T1055.008)
**Existing weights from ontology:**
- IMG-1 (Exploit): 1 - Basic vulnerability scanning helps
- RTS-1 (Exploit): 3 - Non-root significantly reduces process privilege
- RTS-2 (Exploit): 2 - Read-only prevents shellcode injection modifications
- RTS-3 (Exploit): 3 - Without CAP_SYS_PTRACE, attack fails
- NET-1 (Expose): 2 - Segmentation limits lateral movement
- NET-2 (Expose): 2 - Firewall blocks unauthorized connections

## New Techniques - Proposed Weights

### 4. ContainerPtraceProcessDiscovery (T1057)
**Rationale:** Process discovery via ptrace for reconnaissance

**Exploitability:**
- IMG-1: 1 (Low) - Scanning provides basic protection
- RTS-1: 2 (Medium) - Non-root limits process visibility
- RTS-3: 3 (High) - Without CAP_SYS_PTRACE, cannot discover processes
- RTS-4: 2 (Medium) - Seccomp can block ptrace syscalls
- RTS-5: 2 (Medium) - AppArmor profiles can restrict ptrace
- RTS-6: 2 (Medium) - SELinux policies can block ptrace operations

**Exposure:**
- NET-1: 2 (Medium) - Segmentation limits discovery scope
- NET-2: 2 (Medium) - Firewall reduces attacker reach
- MON-1 to MON-8: 1 (Low) - Monitoring can detect suspicious ptrace usage

### 5. ContainerKernelModuleLoading (T1547.006)
**Rationale:** Loading malicious kernel modules for persistence

**Exploitability:**
- IMG-1: 1 (Low) - Image scanning may detect module files
- RTS-1: 3 (High) - Root required for module loading
- RTS-4/5/6: 3 (High) - Seccomp/AppArmor/SELinux can block init_module syscalls
- HIS-1/2/3: 3 (High) - Host hardening critical for module loading protection

**Exposure:**
- NET-1/2: 2 (Medium) - Reduces initial access vectors
- MON-1 to MON-8: 2 (Medium) - Monitoring can detect module loading events
- CIC-1/2/3: 1 (Low) - Secure supply chain reduces malicious module risk

### 6. ContainerNetworkBridgeEvasion (T1599.001)
**Rationale:** Manipulating bridges/routing to bypass segmentation

**Exploitability:**
- RTS-1: 1 (Low) - Non-root provides minimal protection
- RTS-4/5/6: 1 (Low) - Seccomp/AppArmor/SELinux can restrict network operations

**Exposure:**
- NET-1: 3 (High) - Network segmentation is the primary target
- NET-2: 3 (High) - Firewall rules are being bypassed
- NET-3/4: 2 (Medium) - Network policies/isolation help
- MON-1 to MON-8: 1 (Low) - Monitoring can detect bridge manipulation

### 7. ContainerFirewallDisable (T1562.004)
**Rationale:** Disabling host firewall rules

**Exploitability:**
- RTS-1: 1 (Low) - Non-root provides minimal protection

**Exposure:**
- NET-1: 3 (High) - Segmentation is primary defense being removed
- NET-2: 3 (High) - Direct firewall manipulation
- NET-3: 1 (Low) - Network policies provide redundant controls
- MON-1 to MON-8: 2 (Medium) - Monitoring critical for detecting firewall changes

### 8. ContainerCgroupResourceHijacking (T1496)
**Rationale:** Cryptomining via cgroup manipulation

**Exploitability:**
- RTS-1: 2 (Medium) - Non-root limits but doesn't prevent cgroup access
- RTS-4/5/6: 2 (Medium) - LSMs can restrict cgroup operations
- RTS-7: 3 (High) - Host resource limits critical

**Exposure:**
- NET-1/2: 2 (Medium) - Reduces command & control access
- HIS-1/2/3: 2 (Medium) - Host hardening limits cgroup manipulation
- MON-1 to MON-8: 2 (Medium) - Resource monitoring detects cryptomining

### 9. ContainerCgroupDoS (T1499)
**Rationale:** DoS via cgroup resource exhaustion

**Exploitability:**
- RTS-1: 1 (Low) - Non-root provides minimal protection
- RTS-4/5/6: 1 (Low) - LSMs provide some protection
- RTS-7: 3 (High) - Resource limits prevent DoS

**Exposure:**
- NET-1/2: 2 (Medium) - Limits attack reach
- HIS-1/2/3: 1 (Low) - Host hardening helps
- MON-1 to MON-8: 3 (High) - Monitoring critical for detecting resource spikes

### 10. ContainerPrivilegedPortTrafficCapture (T1040)
**Rationale:** Sniffing traffic on privileged ports

**Exploitability:**
- IMG-1: 1 (Low) - Image scanning helps
- RTS-1: 2 (Medium) - Non-root limits port binding
- RTS-4/5/6: 1 (Low) - LSMs provide some protection

**Exposure:**
- NET-1: 2 (Medium) - Segmentation limits traffic exposure
- NET-2: 3 (High) - Firewall critical for port access control
- NET-3/4: 1 (Low) - Network policies help
- AUTH-1/2: 2 (Medium) - Authentication reduces credential theft impact
- AUTH-1/2 (Expose): 1 (Low) - Reduces exposure to auth traffic
- SCM-1/2/3: 2 (Medium) - Secrets management limits credential exposure
- SCM-1/2/3 (Expose): 1 (Low) - Reduces secret exposure
- MON-1 to MON-8: 2 (Medium) - Monitoring detects unusual port activity

### 11. ContainerPrivilegedPortServiceImpersonation (T1556)
**Rationale:** Impersonating services to capture credentials

**Exploitability:**
- IMG-1: 1 (Low) - Image scanning helps
- RTS-1: 2 (Medium) - Non-root limits port binding
- RTS-4/5/6: 1 (Low) - LSMs provide some protection

**Exposure:**
- NET-1: 2 (Medium) - Segmentation limits service exposure
- NET-2: 3 (High) - Firewall critical for preventing fake services
- NET-3/4: 1 (Low) - Network policies help
- AUTH-1: 3 (High) - Strong authentication prevents impersonation success
- AUTH-2: 3 (High) - MFA critical defense against credential capture
- AUTH-1/2 (Expose): 2 (Medium) - Reduces authentication exposure
- SCM-1/2/3: 2 (Medium) - Secrets management limits credential theft
- SCM-1/2/3 (Expose): 1 (Low) - Reduces exposure to secrets
- MON-1 to MON-8: 2 (Medium) - Monitoring detects impersonation attempts

### 12. ContainerPrivilegedPortNetworkDoS (T1498)
**Rationale:** DoS via port hijacking

**Exploitability:**
- RTS-1: 1 (Low) - Non-root provides minimal protection

**Exposure:**
- NET-1: 2 (Medium) - Segmentation limits DoS impact
- NET-2: 3 (High) - Firewall prevents port hijacking
- MON-1 to MON-8: 3 (High) - Monitoring critical for detecting DoS

### 13. ContainerLayer2MitM (T1557)
**Rationale:** ARP spoofing and Layer 2 MitM attacks

**Exploitability:**
- RTS-1: 1 (Low) - Non-root provides minimal protection
- RTS-4/5/6: 1 (Low) - LSMs provide some protection

**Exposure:**
- NET-1: 3 (High) - Network segmentation primary defense
- NET-2: 3 (High) - Firewall helps prevent MitM positioning
- NET-3/4: 2 (Medium) - Network policies and isolation critical
- NET-3/4 (Expose): 2 (Medium) - Isolation reduces MitM exposure
- AUTH-1/2: 2 (Medium) - Authentication protects against credential theft
- AUTH-1/2 (Expose): 1 (Low) - Reduces exposure to auth traffic
- SCM-1/2/3: 1 (Low) - Secrets management provides some protection
- MON-1 to MON-8: 2 (Medium) - Monitoring can detect ARP anomalies

### 14. ContainerOTNetworkAttack (T1200)
**Rationale:** Attacking OT/ICS systems via Layer 2 access

**Exploitability:**
- RTS-1: 1 (Low) - Non-root provides minimal protection
- RTS-4/5/6: 2 (Medium) - LSMs can restrict specialized operations

**Exposure:**
- NET-1: 3 (High) - Critical for OT network isolation
- NET-2: 3 (High) - Firewall essential for OT protection
- NET-3/4: 3 (High) - Network policies critical for OT segmentation
- NET-3/4 (Expose): 3 (High) - Isolation essential for OT networks
- AUTH-1/2: 0 - Not typically applicable to OT protocol manipulation
- MON-1 to MON-8: 3 (High) - Monitoring critical for OT anomaly detection

### 15. ContainerSystemAdminEscape (T1611)
**Rationale:** Container escape via CAP_SYS_ADMIN

**Exploitability:**
- IMG-1: 1 (Low) - Image scanning helps
- RTS-1: 3 (High) - Non-root significantly reduces escape vectors
- RTS-2: 2 (Medium) - Read-only filesystem limits persistence
- RTS-4/5/6: 3 (High) - LSMs critical for preventing escape
- HIS-1/2/3: 3 (High) - Host hardening essential defense

**Exposure:**
- NET-1/2: 2 (Medium) - Limits initial access vectors
- MON-1 to MON-8: 2 (Medium) - Monitoring can detect escape attempts
- CIC-1/2/3: 1 (Low) - Supply chain security reduces malicious containers

## Assumptions Not Affecting Most Techniques

Several assumption categories have **0 weights** for most techniques:
- **IMG-2 to IMG-6**: Image-specific controls (registries, signatures, etc.) - don't directly prevent technique execution
- **AUTH-3**: Password policies - not relevant for most container attacks
- **CIC-4 to CIC-6**: Build process controls - don't prevent runtime attacks
- **CRM-1 to CRM-4**: Compliance/risk management - administrative controls

## How to Use This File

1. **Open in Excel**: The CSV file is designed for easy Excel editing
2. **Review Proposed Values**: Check each technique's weights against your environment
3. **Adjust as Needed**: Modify values based on your specific security context
4. **Document Changes**: Add notes about any changes you make
5. **Import to Ontology**: Use the values to create AssumptionWeight instances in the ontology

## Next Steps

After confirming/adjusting weights in Excel:
1. Create AssumptionWeight instances for each non-zero cell
2. Create ExploitabilityCalculationRule for each technique (referencing Exploit weights)
3. Create ExposureCalculationRule for each technique (referencing Expose weights)
4. Validate the rules using SPARQL queries

## Notes

- **Monitoring (MON) weights**: Generally provide detection rather than prevention, so often lower exploitability impact but higher exposure detection
- **Network (NET) weights**: Critical for exposure, especially for network-based attacks
- **Runtime Security (RTS) weights**: Most critical for exploitability, especially capability-based attacks
- **Host Infrastructure (HIS) weights**: Essential for host-level attacks like kernel modules and escapes
