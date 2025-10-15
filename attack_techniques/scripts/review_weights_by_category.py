#!/usr/bin/env python3
"""
Category-Based Interactive Weight Review Script for CSRO Assumption Weights

This script uses a category-based approach to speed up weight assignment:
1. Review each assumption category (IMG, RTS, NET, etc.)
2. Set a default weight and rationale for the entire category
3. Optionally highlight specific assumptions with different weights/rationales
4. Apply the category defaults to all non-highlighted assumptions

This approach is much faster while maintaining flexibility for special cases.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set


# Category definitions
CATEGORIES = {
    'IMG': {
        'name': 'Container Image Security',
        'assumptions': ['IMG-1', 'IMG-2', 'IMG-3', 'IMG-4', 'IMG-5', 'IMG-6'],
        'general_rationale': 'Container image security practices reduce the software footprint and likelihood of exploitable vulnerabilities'
    },
    'RTS': {
        'name': 'Runtime Security',
        'assumptions': ['RTS-1', 'RTS-2', 'RTS-3', 'RTS-4', 'RTS-5', 'RTS-6', 'RTS-7'],
        'general_rationale': 'Runtime security controls limit container privileges and restrict access to host resources'
    },
    'NET': {
        'name': 'Network Security',
        'assumptions': ['NET-1', 'NET-2', 'NET-3', 'NET-4'],
        'general_rationale': 'Network security controls limit network access and reduce attack surface'
    },
    'AUTH': {
        'name': 'Authentication & Access',
        'assumptions': ['AUTH-1', 'AUTH-2', 'AUTH-3'],
        'general_rationale': 'Authentication and access controls prevent unauthorized access to container infrastructure'
    },
    'SCM': {
        'name': 'Secrets & Config Management',
        'assumptions': ['SCM-1', 'SCM-2', 'SCM-3', 'SCM-4'],
        'general_rationale': 'Secrets management controls protect sensitive credentials from exposure'
    },
    'HIS': {
        'name': 'Host & Infrastructure Security',
        'assumptions': ['HIS-1', 'HIS-2', 'HIS-3'],
        'general_rationale': 'Host infrastructure security reduces vulnerabilities in the container runtime environment'
    },
    'MON': {
        'name': 'Monitoring, Detection & Response',
        'assumptions': ['MON-1', 'MON-2', 'MON-3', 'MON-4', 'MON-5', 'MON-6', 'MON-7', 'MON-8'],
        'general_rationale': 'Monitoring and detection controls enable early identification and response to attacks'
    },
    'CIC': {
        'name': 'CI/CD & Supply Chain',
        'assumptions': ['CIC-1', 'CIC-2', 'CIC-3', 'CIC-4', 'CIC-5', 'CIC-6'],
        'general_rationale': 'CI/CD and supply chain controls prevent introduction of vulnerabilities during development'
    },
    'CRM': {
        'name': 'Compliance & Risk Management',
        'assumptions': ['CRM-1', 'CRM-2', 'CRM-3', 'CRM-4'],
        'general_rationale': 'Compliance and risk management practices establish governance and oversight'
    }
}


class CategoryWeightReviewer:
    def __init__(self, matrix_path: str, rationales_path: str, ontology_path: str):
        self.matrix_path = Path(matrix_path)
        self.rationales_path = Path(rationales_path)
        self.ontology_path = Path(ontology_path)
        self.assumption_descriptions = {}  # assumption_id -> description
        self.techniques = []
        self.technique_descriptions = {}
        self.weights = {}  # (technique, assumption_id, weight_type) -> weight_value
        self.rationales = {}  # (technique, assumption_id, weight_type) -> rationale
        self.changes_made = False
        
    def load_files(self):
        """Load CSV files and ontology."""
        print("Loading assumption weights matrix...")
        self._load_matrix()
        print(f"Loaded {len(self.techniques)} techniques with {len(self.assumption_descriptions)} assumptions")
        
        print("Loading rationales...")
        self._load_rationales()
        print(f"Loaded {len(self.rationales)} existing rationales")
        
        print("Loading technique descriptions from ontology...")
        self._load_technique_descriptions()
        print(f"Loaded {len(self.technique_descriptions)} technique descriptions\n")
    
    def _load_matrix(self):
        """Load the assumption weights matrix."""
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # Parse assumption descriptions from header
            exploitability_start = 2
            exposure_start = None
            
            for i, col in enumerate(header[2:], start=2):
                if " Exposure" in col:
                    exposure_start = i
                    break
                else:
                    # Extract assumption ID and description
                    parts = col.split(':', 1)
                    if len(parts) == 2:
                        assumption_id = parts[0].strip()
                        description = parts[1].strip()
                        self.assumption_descriptions[assumption_id] = description
            
            num_assumptions = exposure_start - 2
            
            # Load technique weights
            for row in reader:
                technique = row[0]
                attack_id = row[1]
                self.techniques.append((technique, attack_id))
                
                # Load exploitability weights
                for i, assumption_id in enumerate(self.assumption_descriptions.keys()):
                    col_idx = 2 + i
                    weight = float(row[col_idx]) if row[col_idx] else 0.0
                    self.weights[(technique, assumption_id, 'Exploitability')] = weight
                
                # Load exposure weights
                for i, assumption_id in enumerate(self.assumption_descriptions.keys()):
                    col_idx = exposure_start + i
                    weight = float(row[col_idx]) if row[col_idx] else 0.0
                    self.weights[(technique, assumption_id, 'Exposure')] = weight
    
    def _load_rationales(self):
        """Load existing rationales."""
        if not self.rationales_path.exists():
            return
        
        with open(self.rationales_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['Technique'], row['Assumption ID'], row['Weight Type'])
                self.rationales[key] = row['Rationale']
    
    def _load_technique_descriptions(self):
        """Load technique descriptions from the ontology file."""
        if not self.ontology_path.exists():
            print(f"⚠️  Ontology file not found: {self.ontology_path}")
            return
        
        with open(self.ontology_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        # Match technique definitions - the description may be many lines after the type declaration
        # Pattern matches from technique name to the final period (end of declaration)
        pattern = r'csro:(\w+)\s+rdf:type\s+owl:NamedIndividual\s*,\s*csro:ContainerAttackTechnique\s*;(.*?)csro:description\s+"([^"]+)"\s*\.'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            technique_name = match.group(1)
            description = match.group(3)
            self.technique_descriptions[technique_name] = description
    
    def review_interactive(self):
        """Interactive category-based review."""
        print("=" * 80)
        print("CATEGORY-BASED WEIGHT REVIEW")
        print("=" * 80)
        print("\nThis tool reviews weights by assumption category (IMG, RTS, NET, etc.)")
        print("For each category, you can:")
        print("  1. Set a default weight and rationale for all assumptions in the category")
        print("  2. Highlight specific assumptions with different weights/rationales")
        print("\nWeight scale:")
        print("  0 = No effect")
        print("  1 = Low effect")
        print("  2 = Medium effect")
        print("  3 = High effect\n")
        
        for technique, attack_id in self.techniques:
            print("\n" + "=" * 80)
            print(f"TECHNIQUE: {technique} ({attack_id})")
            print("=" * 80)
            
            if technique in self.technique_descriptions:
                print(f"\n📋 {self.technique_descriptions[technique]}")
            
            if not self._review_technique_by_category(technique):
                break  # User quit
        
        if self.changes_made:
            self._save_files()
            print("\n✅ Changes saved successfully!")
        else:
            print("\n No changes were made.")
    
    def _review_technique_by_category(self, technique: str) -> bool:
        """Review all categories for a technique. Returns False if user wants to quit."""
        
        # Review each category (both exploitability and exposure) before moving to next
        for category_id, category_info in CATEGORIES.items():
            print("\n" + "#" * 80)
            print(f"📁 CATEGORY: {category_info['name']} ({category_id})")
            print("#" * 80)
            
            # Show technique description for context
            if technique in self.technique_descriptions:
                print(f"\n💡 Technique: {self.technique_descriptions[technique]}")
            
            # Show all assumptions in this category once
            print("\nAssumptions in this category:")
            for assumption_id in category_info['assumptions']:
                desc = self.assumption_descriptions.get(assumption_id, assumption_id)
                print(f"  {assumption_id}: {desc}")
            
            print(f"\n💡 General category rationale: {category_info['general_rationale']}")
            
            # Review exploitability and exposure for this category
            for weight_type in ['Exploitability', 'Exposure']:
                result = self._review_category(technique, weight_type, category_id, category_info)
                if result == 'quit':
                    return False  # User quit
                elif result == 'skip':
                    return True  # Skip to next technique
        
        return True  # Continue to next technique
    
    def _review_category(self, technique: str, weight_type: str, category_id: str, category_info: dict) -> str:
        """Review a single category for a technique and weight type.
        
        Returns:
            'continue' - Continue to next category/weight type
            'skip' - Skip to next technique
            'quit' - Quit the program
        """
        
        print("\n" + "-" * 80)
        print(f"⚖️  {weight_type.upper()}")
        print("-" * 80)
        
        if weight_type == 'Exploitability':
            print("❓ How effective are these assumptions in reducing exploitability through:")
            print("   - Increasing required attacker capabilities, efforts, and technical tools")
            print("   - Implementing security measures that counter the attack vector")
        else:
            print("❓ How effective are these assumptions in reducing exposure through:")
            print("   - Restrictive measures that reduce attacker access to the vulnerable state")
            print("   - Detection measures that increase the risk of getting caught")
        
        # Show current weights for this weight type
        print(f"\nCurrent {weight_type.lower()} weights:")
        for assumption_id in category_info['assumptions']:
            key = (technique, assumption_id, weight_type)
            current_weight = self.weights.get(key, 0)
            current_rationale = self.rationales.get(key, "")
            
            status = f"[{current_weight}]"
            if current_rationale:
                status += f" ✓"
            
            print(f"  {assumption_id}: {status}")
        
        # Get category-wide action
        print("\nOptions:")
        print("  [0-3] - Set default weight for entire category")
        print("  [h] - Highlight specific assumptions (set individual weights)")
        print("  [ENTER] - Keep current weights")
        print("  [s] - Skip to next technique")
        print("  [q] - Quit and save")
        
        while True:
            user_input = input("\nAction: ").strip().lower()
            
            if user_input == 'q':
                return 'quit'
            
            if user_input == 's':
                return 'skip'  # Skip to next technique
            
            if user_input == '':
                # Check if any assumptions in this category need rationales
                needs_rationales = []
                for assumption_id in category_info['assumptions']:
                    key = (technique, assumption_id, weight_type)
                    current_weight = self.weights.get(key, 0)
                    current_rationale = self.rationales.get(key, "")
                    
                    if not current_rationale:
                        needs_rationales.append((assumption_id, current_weight))
                
                if needs_rationales:
                    print(f"\n⚠️  {len(needs_rationales)} assumptions need rationales:")
                    for assumption_id, weight in needs_rationales:
                        desc = self.assumption_descriptions.get(assumption_id, assumption_id)
                        print(f"  {assumption_id}: [{weight}] {desc}")
                    
                    print("\nPlease provide a category-wide rationale or use [h] to set individual rationales:")
                    continue
                
                break  # Keep current
            
            if user_input == 'h':
                # Highlight mode
                result = self._highlight_assumptions(technique, weight_type, category_id, category_info)
                if result == 'quit':
                    return 'quit'
                elif result == 'skip':
                    return 'skip'
                break
            
            # Try to parse as category-wide weight
            try:
                category_weight = float(user_input)
                if 0 <= category_weight <= 3:
                    # Get rationale for category (required for all weights, including 0)
                    print(f"\nSetting weight {category_weight} for all {category_id} assumptions.")
                    if category_weight > 0:
                        print(f"Suggested rationale: {category_info['general_rationale']}")
                        rationale = input("Enter rationale (or ENTER to use suggested): ").strip()
                        if not rationale:
                            rationale = category_info['general_rationale']
                    else:
                        print("Please provide a rationale for why this category has no effect:")
                        rationale = input("Rationale: ").strip()
                        if not rationale:
                            print("⚠️  Rationale required even for zero weights in category-based assessment")
                            continue
                    
                    # Apply to all assumptions in category (with rationale for all weights)
                    for assumption_id in category_info['assumptions']:
                        key = (technique, assumption_id, weight_type)
                        old_weight = self.weights.get(key, 0)
                        
                        if category_weight != old_weight:
                            self.weights[key] = category_weight
                            self.changes_made = True
                        
                        if rationale:
                            self.rationales[key] = rationale
                            self.changes_made = True
                    
                    print(f"✓ Applied weight {category_weight} to all {category_id} assumptions")
                    break
                else:
                    print("❌ Weight must be between 0 and 3")
            except ValueError:
                print("❌ Invalid input")
        
        return 'continue'
    
    def _highlight_assumptions(self, technique: str, weight_type: str, category_id: str, category_info: dict) -> str:
        """Allow user to highlight specific assumptions with custom weights.
        
        Returns:
            'continue' - Continue to next category/weight type
            'skip' - Skip to next technique
            'quit' - Quit the program
        """
        
        print("\n" + "~" * 80)
        print(f"HIGHLIGHT MODE: {category_info['name']}")
        print("~" * 80)
        print("\nFirst, set the default weight for non-highlighted assumptions.")
        
        default_weight = None
        default_rationale = None
        
        while default_weight is None:
            user_input = input("Default weight [0-3]: ").strip()
            try:
                default_weight = float(user_input)
                if not (0 <= default_weight <= 3):
                    print("❌ Weight must be between 0 and 3")
                    default_weight = None
            except ValueError:
                print("❌ Invalid number")
        
        # Get rationale for all weights (including 0)
        if default_weight > 0:
            print(f"\nSuggested rationale: {category_info['general_rationale']}")
            default_rationale = input("Default rationale (or ENTER to use suggested): ").strip()
            if not default_rationale:
                default_rationale = category_info['general_rationale']
        else:
            print("\nPlease provide a rationale for why these assumptions have no effect:")
            default_rationale = input("Default rationale: ").strip()
            while not default_rationale:
                print("⚠️  Rationale required even for zero weights")
                default_rationale = input("Default rationale: ").strip()
        
        # Get highlighted assumptions
        print(f"\nEnter assumption IDs to highlight (comma-separated), or ENTER for none:")
        print(f"Available: {', '.join(category_info['assumptions'])}")
        
        highlighted_input = input("Highlight: ").strip()
        highlighted_ids = set()
        
        if highlighted_input:
            highlighted_ids = set(id.strip().upper() for id in highlighted_input.split(','))
            # Validate IDs
            invalid = highlighted_ids - set(category_info['assumptions'])
            if invalid:
                print(f"⚠️  Invalid IDs ignored: {', '.join(invalid)}")
                highlighted_ids -= invalid
        
        # Review highlighted assumptions
        for assumption_id in highlighted_ids:
            desc = self.assumption_descriptions.get(assumption_id, assumption_id)
            print(f"\n--- {assumption_id}: {desc}")
            
            key = (technique, assumption_id, weight_type)
            current_weight = self.weights.get(key, 0)
            current_rationale = self.rationales.get(key, "")
            
            print(f"Current: [{current_weight}] {current_rationale if current_rationale else '(no rationale)'}")
            
            while True:
                weight_input = input(f"Weight [0-3] or ENTER to keep [{current_weight}]: ").strip()
                
                if weight_input == '':
                    # Keep current
                    break
                
                try:
                    new_weight = float(weight_input)
                    if 0 <= new_weight <= 3:
                        # Require rationale for all weights (including 0)
                        if new_weight > 0:
                            rationale = input("Rationale: ").strip()
                        else:
                            rationale = input("Rationale (why no effect): ").strip()
                        
                        if rationale:
                            self.weights[key] = new_weight
                            self.rationales[key] = rationale
                            self.changes_made = True
                            print("✓ Highlighted assumption updated")
                        else:
                            print("⚠️  Rationale required for all weights")
                            continue
                        break
                    else:
                        print("❌ Weight must be between 0 and 3")
                except ValueError:
                    print("❌ Invalid number")
        
        # Apply defaults to non-highlighted assumptions (with rationale for all weights)
        for assumption_id in category_info['assumptions']:
            if assumption_id not in highlighted_ids:
                key = (technique, assumption_id, weight_type)
                old_weight = self.weights.get(key, 0)
                
                if default_weight != old_weight:
                    self.weights[key] = default_weight
                    self.changes_made = True
                
                if default_rationale:
                    self.rationales[key] = default_rationale
                    self.changes_made = True
        
        print(f"\n✓ Applied defaults to {len(category_info['assumptions']) - len(highlighted_ids)} assumptions")
        print(f"✓ Highlighted {len(highlighted_ids)} assumptions with custom weights")
        
        return 'continue'
    
    def _save_files(self):
        """Save updated weights and rationales back to CSV files."""
        print("\nSaving changes...")
        
        # Save matrix
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        
        # Update weights in rows
        assumption_ids = list(self.assumption_descriptions.keys())
        
        for i, (technique, attack_id) in enumerate(self.techniques):
            row = rows[i]
            
            # Update exploitability weights
            for j, assumption_id in enumerate(assumption_ids):
                key = (technique, assumption_id, 'Exploitability')
                weight = self.weights.get(key, 0)
                row[2 + j] = str(int(weight)) if weight == int(weight) else str(weight)
            
            # Update exposure weights
            exposure_start = 2 + len(assumption_ids)
            for j, assumption_id in enumerate(assumption_ids):
                key = (technique, assumption_id, 'Exposure')
                weight = self.weights.get(key, 0)
                row[exposure_start + j] = str(int(weight)) if weight == int(weight) else str(weight)
            
            rows[i] = row
        
        with open(self.matrix_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        
        print(f"✓ Matrix saved to {self.matrix_path}")
        
        # Save rationales (now includes zero weights with rationales)
        with open(self.rationales_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Technique', 'Assumption ID', 'Assumption Name', 'Weight Type', 'Value', 'Rationale'])
            
            # Sort by technique, then assumption ID
            sorted_rationales = sorted(self.rationales.items(), 
                                      key=lambda x: (x[0][0], x[0][1], x[0][2]))
            
            for (technique, assumption_id, weight_type), rationale in sorted_rationales:
                weight = self.weights.get((technique, assumption_id, weight_type), 0)
                # Save all weights that have rationales (including zero weights)
                assumption_name = self.assumption_descriptions.get(assumption_id, assumption_id)
                
                writer.writerow([
                    technique,
                    assumption_id,
                    assumption_name,
                    weight_type,
                    int(weight) if weight == int(weight) else weight,
                    rationale
                ])
        
        print(f"✓ Rationales saved to {self.rationales_path}")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    matrix_path = script_dir / "../weights/assumption_weights_matrix.csv"
    rationales_path = script_dir / "../weights/assumption_weights_rationales.csv"
    ontology_path = script_dir / "../../csro.ttl"
    
    if not matrix_path.exists():
        print(f"❌ Matrix file not found: {matrix_path}")
        sys.exit(1)
    
    reviewer = CategoryWeightReviewer(str(matrix_path), str(rationales_path), str(ontology_path))
    
    try:
        reviewer.load_files()
        reviewer.review_interactive()
    except KeyboardInterrupt:
        print("\n\n⚠️  Review interrupted. Changes not saved.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
