#!/usr/bin/env python3
"""Test private attributes with getters/setters"""
import sys
import os
import pygame

pygame.init()
root_dir = os.path.abspath('.')
sys.path.insert(0, root_dir)

# Mock schueler.py to prevent auto-loading
sys.modules['schueler'] = type(sys)('schueler')

print("=" * 70)
print("Testing Private Attributes with Getters")
print("=" * 70)

from framework.spielfeld import Spielfeld

class DummyFramework:
    def __init__(self):
        self.weiblich = False
        self._aktion_blockiert = False
        
    def taste_registrieren(self, key, callback):
        pass

fw = DummyFramework()
level37_path = os.path.join(root_dir, 'level', 'level37.json')
sp = Spielfeld(level37_path, fw, feldgroesse=32)

print(f"✓ Spielfeld loaded")

# Get the hero
held = sp.held
if held is None:
    print("✗ No hero spawned!")
    sys.exit(1)

print(f"\n✓ Hero spawned successfully")

# Test direct attribute access (should fail with private attributes)
print(f"\n=== Testing attribute access ===")
try:
    x_val = held.x
    print(f"✓ held.x = {x_val}")
except AttributeError as e:
    print(f"✗ held.x failed: {e}")

try:
    y_val = held.y
    print(f"✓ held.y = {y_val}")
except AttributeError as e:
    print(f"✗ held.y failed: {e}")

try:
    richt_val = held.richtung
    print(f"✓ held.richtung = {richt_val}")
except AttributeError as e:
    print(f"✗ held.richtung failed: {e}")

# Test attribute_als_text (inspector)
print(f"\n=== Testing Inspector (attribute_als_text) ===")
try:
    attrs = held.attribute_als_text()
    for key, val in attrs.items():
        print(f"  {key}: {val}")
except Exception as e:
    print(f"✗ attribute_als_text failed: {e}")

# Test setting attributes
print(f"\n=== Testing attribute setting ===")
try:
    held.x = 5
    print(f"✓ held.x = 5 successful")
    print(f"  New value: {held.x}")
except Exception as e:
    print(f"✗ Setting held.x failed: {e}")

print("\n" + "=" * 70)
print("Test completed")
print("=" * 70)
