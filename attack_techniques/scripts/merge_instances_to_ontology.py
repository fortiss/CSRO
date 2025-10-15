"""
Merge generated ontology instances into csro.ttl by replacing old instances
with comprehensive new ones.
"""

def merge_instances():
    # Read the original ontology
    with open('../../csro.ttl', 'r', encoding='utf-8') as f:
        csro_lines = f.readlines()
    
    # Read the generated instances (skip the header with prefixes)
    with open('../weights/generated_ontology_instances.ttl', 'r', encoding='utf-8') as f:
        generated_lines = f.readlines()
    
    # Find where to skip in generated file (after prefixes, before first ###)
    gen_start_idx = 0
    for i, line in enumerate(generated_lines):
        if line.strip().startswith('###'):
            gen_start_idx = i
            break
    
    # Find the section to replace in csro.ttl
    # Start: First old weight/rule instance (around line 1400)
    # End: Last old weight/rule instance (around line 1723)
    start_marker = None
    end_marker = None
    
    for i, line in enumerate(csro_lines):
        # Find start: First AssumptionWeight after ContainerDataFromLocalSystemAttack_MixedScenario
        if 'ContainerDataFromLocalSystemExp_NET_1_Weight' in line and '###' in line:
            start_marker = i
        # Find end: ContainerPtrace_RTS_3_Weight is the last old instance
        if 'ContainerPtrace_RTS_3_Weight' in line and 'csro:ContainerPtrace_RTS_3_Weight rdf:type' in line:
            # Find the end of this instance (next ### or blank line followed by ###)
            for j in range(i+1, len(csro_lines)):
                if csro_lines[j].strip().startswith('###'):
                    end_marker = j
                    break
    
    if start_marker is None or end_marker is None:
        print(f"ERROR: Could not find markers. Start: {start_marker}, End: {end_marker}")
        return
    
    print(f"Found old instances from line {start_marker+1} to {end_marker}")
    print(f"Replacing with {len(generated_lines) - gen_start_idx} lines of new content")
    
    # Create the new file
    new_content = []
    
    # Keep everything before the old instances
    new_content.extend(csro_lines[:start_marker])
    
    # Add the generated instances (skip header - already has clean section comments)
    new_content.extend(generated_lines[gen_start_idx:])
    
    # Keep everything after the old instances
    new_content.extend(csro_lines[end_marker:])
    
    # Write the new file
    with open('../../csro.ttl', 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    
    print(f"\n✅ Successfully merged instances into csro.ttl")
    print(f"   Removed {end_marker - start_marker} lines of old content")
    print(f"   Added {len(generated_lines) - gen_start_idx + 20} lines of new content (including markers)")
    print(f"   New file has {len(new_content)} total lines")

if __name__ == '__main__':
    merge_instances()
