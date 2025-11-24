#!/usr/bin/env python3
"""Debug Inspector für Level 37"""
import sys
import os
import pygame

pygame.init()
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from framework.spielfeld import Spielfeld

class DummyFramework:
    def __init__(self):
        self.weiblich = False
        self._aktion_blockiert = False
        
    def taste_registrieren(self, key, callback):
        pass

fw = DummyFramework()
sp = Spielfeld('level/level38.json', fw, feldgroesse=32)

held = sp.held
if held is None:
    print("✗ Kein Held gespawnt!")
    sys.exit(1)

print("=" * 70)
print("Inspector Debug für Level 37 mit privaten Attributen")
print("=" * 70)

# Student object
student = object.__getattribute__(held, '_student')
print("\nStudent object type:", type(student).__name__)
print("\nStudent attributes (dir):")
attrs = [a for a in dir(student) if not a.startswith('_') or a.startswith('_Held__')]
for attr in sorted(attrs):
    print(f"  - {attr}")

# Test getter calls directly
print("\n" + "=" * 70)
print("Direct getter calls:")
print("=" * 70)
for getter in ['get_x', 'get_y', 'get_richtung', 'get_weiblich', 'get_typ']:
    if hasattr(student, getter):
        try:
            method = getattr(student, getter)
            value = method()
            print(f"✓ {getter}() = {value}")
        except Exception as e:
            print(f"✗ {getter}() raised: {e}")
    else:
        print(f"✗ {getter} not found")

# Test attribute_als_text
print("\n" + "=" * 70)
print("MetaHeld.attribute_als_text():")
print("=" * 70)
inspector_result = held.attribute_als_text()
for key, value in inspector_result.items():
    status = "✓" if "privat" not in str(value) and "error" not in str(value) else "✗"
    print(f"{status} {key}: {value}")

# Check if critical attributes are missing
print("\n" + "=" * 70)
print("Analysis:")
print("=" * 70)
required = ['x', 'y', 'richtung', 'weiblich', 'typ']
missing = []
for attr in required:
    val = inspector_result.get(attr, 'FEHLT')
    if 'privat' in str(val) or 'error' in str(val) or val == 'FEHLT':
        missing.append(attr)

if missing:
    print(f"✗ Fehlende Attribute: {missing}")
    
    # Debug: Try getattr on student directly
    print("\nDebug: Direct getattr tests:")
    for attr in missing:
        print(f"\n  Testing '{attr}':")
        try:
            val = getattr(student, attr)
            print(f"    ✓ Direct getattr(student, '{attr}') = {val}")
        except AttributeError as e:
            print(f"    ✗ Direct getattr failed: {e}")
            
            getter = f'get_{attr}'
            if hasattr(student, getter):
                try:
                    method = getattr(student, getter)
                    val = method()
                    print(f"    ✓ Via getter: {getter}() = {val}")
                except Exception as e2:
                    print(f"    ✗ Getter failed: {e2}")
            else:
                print(f"    ✗ No getter {getter} found")
else:
    print("✓ Alle Attribute vorhanden")
