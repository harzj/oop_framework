"""Debug victory check for level35"""
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
level35_path = os.path.join(root_dir, 'level', 'level35.json')
sp = Spielfeld(level35_path, fw, feldgroesse=32)

print("=" * 70)
print("Victory Check Debug")
print("=" * 70)

print(f"\nHeld: {sp.held}")
print(f"Held type: {type(sp.held).__name__}")

if sp.held:
    student = getattr(sp.held, '_student', None)
    print(f"Student instance: {student}")
    
    if student:
        print(f"\nStudent attributes:")
        for attr in ['x', 'y', 'richtung', 'name', 'weiblich', 'typ']:
            has_it = hasattr(student, attr)
            val = getattr(student, attr, '<missing>') if has_it else '<missing>'
            print(f"  {attr}: {val} (hasattr={has_it})")
    
    print(f"\nLevel expectations:")
    print(f"  _level_expected_x: {getattr(sp.held, '_level_expected_x', None)}")
    print(f"  _level_expected_y: {getattr(sp.held, '_level_expected_y', None)}")
    print(f"  _level_expected_richtung: {getattr(sp.held, '_level_expected_richtung', None)}")
    
    print(f"\nClass requirements:")
    req = sp.class_requirements.get("Held", {})
    print(f"  load_from_schueler: {req.get('load_from_schueler')}")
    print(f"  attributes: {req.get('attributes', [])}")

print(f"\nVictory settings:")
vic = sp.level.settings.get('victory', {})
print(f"  collect_hearts: {vic.get('collect_hearts')}")
print(f"  move_to: {vic.get('move_to')}")
print(f"  classes_present: {vic.get('classes_present')}")

print(f"\n_required_spawn_classes: {getattr(sp, '_required_spawn_classes', None)}")

print("\nCalling check_victory()...")
result = sp.check_victory()
print(f"Result: {result}")

if not result:
    print("\n[DEBUG] Checking why victory failed...")
    # Check _student_has_class
    has_class = sp._student_has_class('Held')
    print(f"  _student_has_class('Held'): {has_class}")
    
    # Check attributes
    if student:
        required_attrs = req.get('attributes', [])
        print(f"  Required attributes: {required_attrs}")
        for attr in required_attrs:
            has_it = hasattr(student, attr)
            print(f"    {attr}: {has_it}")
        
        # Check position match
        if hasattr(student, 'x') and hasattr(student, 'y'):
            expected_x = getattr(sp.held, '_level_expected_x', None)
            expected_y = getattr(sp.held, '_level_expected_y', None)
            print(f"  Position check:")
            print(f"    student.x={student.x} vs expected={expected_x}: {student.x == expected_x}")
            print(f"    student.y={student.y} vs expected={expected_y}: {student.y == expected_y}")
