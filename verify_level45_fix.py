"""
Side-by-side comparison: Level 45 before and after fix
"""

import pygame
from framework.grundlage import level

pygame.init()

# Create side-by-side display
screen = pygame.display.set_mode((960, 320))  # 2x width for comparison
pygame.display.set_caption("Level 45 Fix - Trees should be hidden")

level.lade(45, weiblich=True)
sp = level.framework.spielfeld

print("="*70)
print("Level 45 Visual Verification")
print("="*70)
print(f"classes_present: {sp.victory_settings.get('classes_present', False)}")
print(f"Hindernis requirements: {bool(sp.class_requirements.get('Hindernis'))}")
print(f"Hindernis student mode: {sp._hindernis_student_mode_enabled}")
print(f"Hindernis class valid: {sp._hindernis_class_valid}")
print()
print("Expected result: NO tree tiles visible (only grass)")
print()

# Draw game view
sp.zeichne(screen)
pygame.display.flip()

# Save
pygame.image.save(screen, 'level45_fixed.png')
print("✓ Screenshot saved: level45_fixed.png")
print()
print("Visual check:")
print("  ✓ Should see: Green grass background")
print("  ✓ Should see: Hero sprite")  
print("  ✓ Should see: Zettel/Code sprite")
print("  ✗ Should NOT see: Tree/Berg/Busch sprites")
print()
print("Press any key...")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            running = False

pygame.quit()
print("Done")
