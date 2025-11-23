#!/usr/bin/env python3
"""Test Level 36 victory checking with move_to and method requirements"""
import sys
import os
import pygame

pygame.init()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Testing Level 36 Victory Conditions")
print("=" * 70)

# Create proper Level 36 solution
test_solution = """
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
    
    def geh(self):
        if self.richtung == "o":
            self.x += 1
        elif self.richtung == "w":
            self.x -= 1
        elif self.richtung == "n":
            self.y -= 1
        elif self.richtung == "s":
            self.y += 1
    
    def links(self):
        links_dict = {"o": "n", "n": "w", "w": "s", "s": "o"}
        self.richtung = links_dict[self.richtung]
    
    def rechts(self):
        rechts_dict = {"o": "s", "s": "w", "w": "n", "n": "o"}
        self.richtung = rechts_dict[self.richtung]
"""

schueler_path = os.path.join(root_dir, 'schueler.py')
with open(schueler_path, 'w', encoding='utf-8') as f:
    f.write(test_solution)

from framework.spielfeld import Spielfeld

class DummyFramework:
    def __init__(self):
        self.weiblich = False
        self._aktion_blockiert = False
        
    def taste_registrieren(self, key, callback):
        pass

fw = DummyFramework()
level36_path = os.path.join(root_dir, 'level', 'level36.json')
sp = Spielfeld(level36_path, fw, feldgroesse=32)

print(f"✓ Spielfeld loaded")
print(f"✓ Victory conditions:")
print(f"  - move_to: x={sp.victory_settings.get('move_to', {}).get('x')}, y={sp.victory_settings.get('move_to', {}).get('y')}")
print(f"  - classes_present: {sp.victory_settings.get('classes_present')}")
print(f"  - Required methods: {sp.class_requirements.get('Held', {}).get('methods', [])}")

# Check class implementation
has_class = sp._student_has_class('Held')
print(f"\n✓ _student_has_class('Held'): {has_class}")

if not has_class:
    print("✗ Class check failed! Student class doesn't meet requirements.")
    sys.exit(1)

# Get the hero
held = sp.held
print(f"\n✓ Hero starting position: x={held.x}, y={held.y}")

# Move hero to victory position (2, 3)
target_x = sp.victory_settings['move_to']['x']
target_y = sp.victory_settings['move_to']['y']

# Simulate movement to target
held.x = target_x
held.y = target_y
print(f"✓ Moved hero to: x={held.x}, y={held.y}")

# Check victory
victory = sp.check_victory()
print(f"\n✓ Victory check result: {victory}")

if victory:
    print("\n" + "=" * 70)
    print("✓✓✓ LEVEL 36 VICTORY TEST PASSED ✓✓✓")
    print("=" * 70)
else:
    print("\n✗ Victory should have been triggered!")
    print(f"  Hero at: ({held.x}, {held.y})")
    print(f"  Target: ({target_x}, {target_y})")
    print(f"  Class requirements met: {has_class}")
    sys.exit(1)
