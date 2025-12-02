"""
Test flexible Held/Knappe constructor signatures
"""
import pygame
pygame.init()

print("="*70)
print("Testing Flexible Constructor Signatures")
print("="*70)

# Test 1: Student signature for Held
print("\n1. Student signature: Held(3, 4, 'down', False)")
from framework.held import Held
h1 = Held(3, 4, "down", False)
print(f"   Created: {h1}")
print(f"   Position: x={h1.x}, y={h1.y}")
print(f"   Richtung: {h1.richtung}")
print(f"   Weiblich: {h1.weiblich}")
print(f"   Framework: {h1.framework}")
print(f"   ✓ SUCCESS")

# Test 2: Student signature for Held (weiblich)
print("\n2. Student signature: Held(5, 6, 'up', True)")
h2 = Held(5, 6, "up", True)
print(f"   Created: {h2}")
print(f"   Position: x={h2.x}, y={h2.y}")
print(f"   Richtung: {h2.richtung}")
print(f"   Weiblich: {h2.weiblich}")
print(f"   Sprite: {h2.sprite_pfad}")
print(f"   ✓ SUCCESS")

# Test 3: Student signature for Knappe
print("\n3. Student signature: Knappe(2, 2, 'up')")
from framework.knappe import Knappe
k1 = Knappe(2, 2, "up")
print(f"   Created: {k1}")
print(f"   Position: x={k1.x}, y={k1.y}")
print(f"   Richtung: {k1.richtung}")
print(f"   Framework: {k1.framework}")
print(f"   Name: {k1.name}")
print(f"   ✓ SUCCESS")

# Test 4: Framework signature for Held (ensure backward compatibility)
print("\n4. Framework signature: Held(None, 7, 8, 'left', weiblich=False)")
h3 = Held(None, 7, 8, "left", False)
print(f"   Created: {h3}")
print(f"   Position: x={h3.x}, y={h3.y}")
print(f"   Richtung: {h3.richtung}")
print(f"   Weiblich: {h3.weiblich}")
print(f"   ✓ SUCCESS")

# Test 5: Framework signature for Knappe
print("\n5. Framework signature: Knappe(None, 9, 10, 'right')")
k2 = Knappe(None, 9, 10, "right")
print(f"   Created: {k2}")
print(f"   Position: x={k2.x}, y={k2.y}")
print(f"   Richtung: {k2.richtung}")
print(f"   ✓ SUCCESS")

print("\n" + "="*70)
print("✓ ALL TESTS PASSED")
print("="*70)

pygame.quit()
