#!/usr/bin/env python3
"""
Interactive Weight Review Script for CSRO Assumption Weights

This script guides you through reviewing and updating assumption weights for
container attack techniques. For each technique-assumption pair, you can:
- See the current weight and rationale
- Accept the current weight
- Update the weight and provide a new rationale
- Skip zero-weight assumptions (they don't need rationales)

The script updates both the matrix and rationales files automatically.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class WeightReviewer:
    def __init__(self, matrix_path: str, rationales_path: str, ontology_path: str):
        self.matrix_path = Path(matrix_path)
        self.rationales_path = Path(rationales_path)
        self.ontology_path = Path(ontology_path)
        self.assumptions = []
        self.techniques = []
        self.technique_descriptions = {}  # technique_name -> description
        self.weights = {}  # (technique, assumption_id, weight_type) -> weight_value
        self.rationales = {}  # (technique, assumption_id, weight_type) -> rationale
        self.changes_made = False
        
    def load_files(self):
        """Load both CSV files into memory."""
        print("Loading assumption weights matrix...")
        self._load_matrix()
        print(f"Loaded {len(self.techniques)} techniques with {len(self.assumptions)} assumptions")
        
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
            
            # Parse header: Technique, ATT&CK ID, then assumptions
            # Assumptions appear twice: exploitability columns, then exposure columns
            technique_col = 0
            attack_col = 1
            
            # Find the split point between exploitability and exposure
            exploitability_assumptions = []
            exposure_assumptions = []
            
            for i, col in enumerate(header[2:], start=2):
                if " Exposure" in col:
                    # This is the start of exposure columns
                    exposure_start = i
                    break
                else:
                    # Extract assumption ID from "ID: Description" format
                    assumption_id = col.split(':')[0].strip()
                    exploitability_assumptions.append((assumption_id, col, i))
            
            # Now get exposure assumptions
            for i, col in enumerate(header[exposure_start:], start=exposure_start):
                assumption_id = col.split(':')[0].strip().replace(' Exposure', '')
                exposure_assumptions.append((assumption_id, col, i))
            
            self.assumptions = exploitability_assumptions
            
            # Load technique weights
            for row in reader:
                technique = row[technique_col]
                attack_id = row[attack_col]
                self.techniques.append((technique, attack_id))
                
                # Load exploitability weights
                for assumption_id, _, col_idx in exploitability_assumptions:
                    weight = float(row[col_idx]) if row[col_idx] else 0.0
                    self.weights[(technique, assumption_id, 'Exploitability')] = weight
                
                # Load exposure weights
                for assumption_id, _, col_idx in exposure_assumptions:
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
        
        # Parse Turtle format to extract technique descriptions
        # Looking for patterns like:
        # csro:ContainerTechniqueName rdf:type owl:NamedIndividual ,
        #                                     csro:ContainerAttackTechnique ;
        #                            csro:description "..." .
        
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
        """Interactive review of all weights."""
        print("=" * 80)
        print("INTERACTIVE WEIGHT REVIEW")
        print("=" * 80)
        print("\nFor each technique-assumption combination, you can:")
        print("  [ENTER] - Accept current weight and rationale")
        print("  [number] - Set new weight (0-3)")
        print("  [r] - Update rationale (keep current weight)")
        print("  [s] - Skip remaining assumptions for this technique")
        print("  [q] - Quit and save changes")
        print("\nNote: Zero weights don't require rationales.\n")
        
        for technique, attack_id in self.techniques:
            print("\n" + "=" * 80)
            print(f"TECHNIQUE: {technique} ({attack_id})")
            print("=" * 80)
            
            if not self._review_technique(technique):
                break  # User quit
        
        if self.changes_made:
            self._save_files()
            print("\n✅ Changes saved successfully!")
        else:
            print("\n No changes were made.")
    
    def _review_technique(self, technique: str) -> bool:
        """Review all assumptions for a technique. Returns False if user wants to quit."""
        
        # Show technique description once at the start
        if technique in self.technique_descriptions:
            print(f"\n📋 TECHNIQUE DESCRIPTION:")
            print(f"   {self.technique_descriptions[technique]}")
        
        print("\nWeight scale:")
        print("  0 = No effect - assumption doesn't impact this attack aspect")
        print("  1 = Low effect - minimal impact on attack difficulty/likelihood")
        print("  2 = Medium effect - moderate impact on attack difficulty/likelihood")
        print("  3 = High effect - significant impact on attack difficulty/likelihood")
        
        # Review each assumption (both exploitability and exposure)
        for assumption_id, assumption_desc, _ in self.assumptions:
            print("\n" + "=" * 80)
            assumption_text = assumption_desc.split(':', 1)[1].strip() if ':' in assumption_desc else assumption_desc
            print(f"📌 ASSUMPTION {assumption_id}: {assumption_text}")
            
            # Show full technique description for context
            if technique in self.technique_descriptions:
                print(f"\n💡 Technique: {self.technique_descriptions[technique]}")
            
            # Review exploitability and exposure for this assumption
            for weight_type in ['Exploitability', 'Exposure']:
                key = (technique, assumption_id, weight_type)
                current_weight = self.weights[key]
                current_rationale = self.rationales.get(key, "")
                
                # Display weight type section
                print("\n" + "-" * 80)
                print(f"⚖️  {weight_type.upper()}")
                
                if weight_type == 'Exploitability':
                    print("❓ How effective is this assumption in reducing exploitability through:")
                    print("   - Increasing required attacker capabilities, efforts, and technical tools")
                    print("   - Implementing security measures that counter the attack vector")
                else:
                    print("❓ How effective is this assumption in reducing exposure through:")
                    print("   - Restrictive measures that reduce attacker access to the vulnerable state")
                    print("   - Detection measures that increase the risk of getting caught")
                
                print(f"\n📊 Current weight: {current_weight}")
                if current_rationale:
                    print(f"📝 Rationale: {current_rationale}")
                elif current_weight > 0:
                    print("⚠️  No rationale defined (required for non-zero weights)")
                
                # Get user input
                while True:
                    user_input = input(f"\nAction [0-3/r/ENTER/s/q]: ").strip().lower()
                    
                    if user_input == 'q':
                        return False  # Quit
                    
                    if user_input == 's':
                        return True  # Skip to next technique
                    
                    if user_input == 'r':
                        # Update rationale only
                        if current_weight == 0:
                            print("⚠️  Zero weights don't need rationales")
                            continue
                        print(f"\nCurrent rationale: {current_rationale if current_rationale else '(none)'}")
                        new_rationale = input("Enter new rationale: ").strip()
                        if new_rationale:
                            self.rationales[key] = new_rationale
                            self.changes_made = True
                            print("✓ Rationale updated")
                        break
                    
                    if user_input == '':
                        # Accept current weight
                        if current_weight > 0 and not current_rationale:
                            print("⚠️  Non-zero weight requires a rationale!")
                            rationale = input("Enter rationale: ").strip()
                            if rationale:
                                self.rationales[key] = rationale
                                self.changes_made = True
                                print("✓ Rationale added")
                        break
                    
                    # Try to parse as weight
                    try:
                        new_weight = float(user_input)
                        if 0 <= new_weight <= 3:
                            if new_weight != current_weight:
                                self.weights[key] = new_weight
                                self.changes_made = True
                                
                                if new_weight > 0:
                                    # Need rationale for non-zero weight
                                    print(f"\nWeight changed to {new_weight}. Please provide a rationale:")
                                    rationale = input("Rationale: ").strip()
                                    if rationale:
                                        self.rationales[key] = rationale
                                        print("✓ Weight and rationale updated")
                                    else:
                                        print("⚠️  Rationale required for non-zero weights!")
                                        continue
                                else:
                                    # Zero weight - remove rationale if it exists
                                    if key in self.rationales:
                                        del self.rationales[key]
                                    print("✓ Weight set to 0 (no rationale needed)")
                            break
                        else:
                            print("❌ Weight must be between 0 and 3")
                    except ValueError:
                        print("❌ Invalid input. Enter a number 0-3, ENTER, 's', or 'q'")
        
        return True  # Continue to next technique
    
    def _save_files(self):
        """Save updated weights and rationales back to CSV files."""
        print("\nSaving changes...")
        
        # Save matrix
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        
        # Update weights in rows
        for i, (technique, attack_id) in enumerate(self.techniques):
            row = rows[i]
            col_idx = 2
            
            # Update exploitability weights
            for assumption_id, _, _ in self.assumptions:
                key = (technique, assumption_id, 'Exploitability')
                row[col_idx] = str(int(self.weights[key])) if self.weights[key] == int(self.weights[key]) else str(self.weights[key])
                col_idx += 1
            
            # Update exposure weights
            for assumption_id, _, _ in self.assumptions:
                key = (technique, assumption_id, 'Exposure')
                row[col_idx] = str(int(self.weights[key])) if self.weights[key] == int(self.weights[key]) else str(self.weights[key])
                col_idx += 1
            
            rows[i] = row
        
        with open(self.matrix_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        
        print(f"✓ Matrix saved to {self.matrix_path}")
        
        # Save rationales (only non-zero weights)
        with open(self.rationales_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Technique', 'Assumption ID', 'Assumption Name', 'Weight Type', 'Value', 'Rationale'])
            
            # Sort by technique, then assumption ID
            sorted_rationales = sorted(self.rationales.items(), 
                                      key=lambda x: (x[0][0], x[0][1], x[0][2]))
            
            for (technique, assumption_id, weight_type), rationale in sorted_rationales:
                weight = self.weights[(technique, assumption_id, weight_type)]
                if weight > 0:  # Only save non-zero weights
                    # Get assumption name from original header
                    assumption_name = next((desc.split(':', 1)[1].strip() 
                                          for aid, desc, _ in self.assumptions 
                                          if aid == assumption_id), assumption_id)
                    
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
    
    reviewer = WeightReviewer(str(matrix_path), str(rationales_path), str(ontology_path))
    
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
