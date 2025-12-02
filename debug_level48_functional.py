"""Debug functional test for Level 48"""
import pygame
pygame.init()

from framework.spielfeld import Spielfeld

sp = Spielfeld('level/level48.json', None, 80)

print("="*70)
print("Level 48 Functional Test Debug")
print("="*70)

# Check requirements
req = sp.class_requirements.get('Hindernis', {})
print(f"Hindernis requirements methods: {req.get('methods', [])}")
print(f"'get_typ' in methods: {'get_typ' in req.get('methods', [])}")

hindernisse = [o for o in sp.objekte if hasattr(o, '_student')]
print(f"\nHindernisse with _student: {len(hindernisse)}")

if hindernisse:
    h = hindernisse[0]
    print(f"Has _student: {hasattr(h, '_student')}")
    print(f"_student has get_typ: {hasattr(h._student, 'get_typ')}")
    if hasattr(h._student, 'get_typ'):
        typ_val = h._student.get_typ()
        print(f"get_typ() returns: {typ_val}")
        print(f"Is valid? {typ_val in ['Baum', 'Berg', 'Busch']}")

# Check required spawn classes
needed = getattr(sp, '_required_spawn_classes', set())
print(f"\nRequired spawn classes: {needed}")
print(f"'Hindernis' in needed: {'Hindernis' in needed}")

print(f"\nCheck victory: {sp.check_victory()}")

pygame.quit()
