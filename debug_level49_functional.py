"""Debug functional test for Level 49"""
import pygame
pygame.init()

from framework.spielfeld import Spielfeld

sp = Spielfeld('level/level49.json', None, 80)

print("="*70)
print("Level 49 Functional Test Debug")
print("="*70)

# Check requirements
req = sp.class_requirements.get('Zettel', {})
print(f"Zettel requirements methods: {req.get('methods', [])}")
print(f"'get_spruch' in methods: {'get_spruch' in req.get('methods', [])}")
print(f"'set_spruch' in methods: {'set_spruch' in req.get('methods', [])}")

zettel = [o for o in sp.objekte if hasattr(o, 'get_spruch')]
print(f"\nZettel objects: {len(zettel)}")

if zettel:
    z = zettel[0]
    print(f"Has get_spruch: {hasattr(z, 'get_spruch')}")
    print(f"Has set_spruch: {hasattr(z, 'set_spruch')}")
    if hasattr(z, 'set_spruch') and hasattr(z, 'get_spruch'):
        try:
            original = z.get_spruch()
            print(f"Original spruch: {original}")
            z.set_spruch("TEST")
            retrieved = z.get_spruch()
            print(f"After set_spruch('TEST'): {retrieved}")
            print(f"Test passed: {retrieved == 'TEST'}")
        except Exception as e:
            print(f"Exception: {e}")

print(f"\nCheck victory: {sp.check_victory()}")

pygame.quit()
