"""
Visual test for Level 45 tile rendering.
Verifies that obstacle tiles (trees) are NOT rendered when:
- classes_present: true
- No Hindernis requirements
- No Hindernis class present
"""

import pygame
from framework.grundlage import level

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Level 45 - No Trees Test")

print("="*70)
print("Level 45 Visual Tile Test")
print("="*70)
print("Expected: NO trees visible (only grass + Held + Zettel)")
print()

level.lade(45, weiblich=True)
sp = level.framework.spielfeld

print(f"Spielfeld objekte: {len(sp.objekte)}")
print(f"Hindernis valid: {getattr(sp, '_hindernis_class_valid', 'NOT_SET')}")
print(f"Hindernis student mode: {getattr(sp, '_hindernis_student_mode_enabled', False)}")

# Count Hindernisse
hindernisse = [o for o in sp.objekte if hasattr(o, 'typ') and o.typ in ['Baum', 'Berg', 'Busch']]
print(f"Hindernis objects: {len(hindernisse)}")

# Draw
sp.zeichne(screen)
pygame.display.flip()

# Save screenshot
pygame.image.save(screen, 'test_level45_no_obstacles.png')
print()
print("✓ Screenshot saved: test_level45_no_obstacles.png")
print()
print("Verify manually:")
print("  - Should see: Green grass, Hero, Zettel")
print("  - Should NOT see: Trees (obstacle tiles)")
print()
print("Press any key to exit...")

# Wait for key
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            running = False

pygame.quit()
print("✓ Test complete")
