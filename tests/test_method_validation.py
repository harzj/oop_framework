#!/usr/bin/env python3
"""Test that _student_has_class checks both attributes and methods"""
import sys
import os
import pygame

pygame.init()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Test 1: Student class WITHOUT required methods")
print("=" * 70)

# Create schueler.py without methods
test_no_methods = """
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
"""

schueler_path = os.path.join(root_dir, 'schueler.py')
with open(schueler_path, 'w', encoding='utf-8') as f:
    f.write(test_no_methods)

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
print(f"✓ Class requirements methods: {sp.class_requirements.get('Held', {}).get('methods', [])}")

has_class = sp._student_has_class('Held')
print(f"✓ _student_has_class('Held'): {has_class}")

if has_class:
    print("✗ Should return False because methods are missing!")
    sys.exit(1)
else:
    print("✓ Correctly returns False (methods missing)")

print("\n" + "=" * 70)
print("Test 2: Student class WITH required methods")
print("=" * 70)

# Create schueler.py with methods
test_with_methods = """
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
    
    def geh(self):
        pass
    
    def links(self):
        pass
    
    def rechts(self):
        pass
"""

with open(schueler_path, 'w', encoding='utf-8') as f:
    f.write(test_with_methods)

# Reload
if 'schueler' in sys.modules:
    del sys.modules['schueler']

sp2 = Spielfeld(level36_path, fw, feldgroesse=32)

has_class2 = sp2._student_has_class('Held')
print(f"✓ _student_has_class('Held'): {has_class2}")

if not has_class2:
    print("✗ Should return True because all methods are present!")
    sys.exit(1)
else:
    print("✓ Correctly returns True (all methods present)")

print("\n" + "=" * 70)
print("✓✓✓ ALL METHOD CHECK TESTS PASSED ✓✓✓")
print("=" * 70)
