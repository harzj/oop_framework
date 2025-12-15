import os
os.environ["OOP_TEST"] = "1"

import sys
sys.path.insert(0, os.path.dirname(__file__))

# Import schueler.py to run the level
import schueler

# Load level 50
level = Level('level/level50.json')

# Create Spielfeld
spielfeld = Spielfeld(level, None)

# Check _get_needed_classes
print("=== Checking _get_needed_classes() ===")
needed = spielfeld._get_needed_classes()
print(f"Needed classes: {needed}")

# Check class_requirements for Hindernis
print("\n=== Checking class_requirements for Hindernis ===")
req = spielfeld.class_requirements.get('Hindernis', {})
print(f"Hindernis requirements: {req}")

# Check _requires_student_implementation
print("\n=== Checking _requires_student_implementation('Hindernis') ===")
requires = spielfeld._requires_student_implementation('Hindernis', req)
print(f"Requires student implementation: {requires}")

# Check if Hindernis class exists
print("\n=== Checking if student has Hindernis class ===")
has_class = spielfeld._student_has_class('Hindernis')
print(f"Student has Hindernis class: {has_class}")
