#!/usr/bin/env python3
"""Test Level 37 victory checking with klassen/held.py"""
import sys
import os
import pygame

pygame.init()
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

print("=" * 70)
print("Testing Level 37 Victory Conditions (load_from_klassen)")
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
print(f"✓ Victory conditions:")
vs = sp.victory_settings
print(f"  - move_to: x={vs.get('move_to', {}).get('x')}, y={vs.get('move_to', {}).get('y')}")
print(f"  - classes_present: {vs.get('classes_present')}")
req = sp.class_requirements.get('Held', {})
print(f"  - Required methods: {req.get('methods', [])}")
print(f"  - Required attributes: {req.get('attributes', [])}")
print(f"  - load_from_klassen: {req.get('load_from_klassen')}")

# Check class implementation
has_class = sp._student_has_class('Held')
print(f"\n✓ _student_has_class('Held'): {has_class}")

if not has_class:
    print("✗ Class check failed! Student class doesn't meet requirements.")
    sys.exit(1)

# Get the hero
held = sp.held
if held is None:
    print("✗ No hero spawned!")
    sys.exit(1)

print(f"\n✓ Hero starting position: x={held.x}, y={held.y}, richtung={held.richtung}")

# Check attributes
print(f"\n✓ Checking attributes:")
for attr in ['x', 'y', 'richtung', 'name', 'weiblich', 'typ']:
    # Access through held (MetaHeld wrapper) to properly trigger getter fallback
    try:
        val = getattr(held, attr)
        has_it = True
    except AttributeError:
        val = 'MISSING'
        has_it = False
    print(f"  - {attr}: {val} {'✓' if has_it else '✗'}")

# Move hero directly to target
target_x = vs['move_to']['x']
target_y = vs['move_to']['y']
held.x = target_x
held.y = target_y
print(f"\n✓ Moved hero to target: ({held.x}, {held.y})")

# Check victory
victory = sp.check_victory()
print(f"\n✓ Victory check result: {victory}")

if victory:
    print("\n" + "=" * 70)
    print("✓✓✓ LEVEL 37 VICTORY TEST PASSED ✓✓✓")
    print("=" * 70)
else:
    print("\n✗ Victory should have been triggered!")
    print(f"  Hero at: ({held.x}, {held.y})")
    print(f"  Target: ({target_x}, {target_y})")
    print(f"  Class requirements met: {has_class}")
    sys.exit(1)
