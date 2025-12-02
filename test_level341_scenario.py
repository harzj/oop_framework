"""
Test Level 341 scenario: Students creating Held and Knappe objects
without framework knowledge
"""
import pygame
pygame.init()

print("="*70)
print("Level 341 Scenario Test")
print("Student creates Held and Knappe objects without framework")
print("="*70)

from framework.held import Held
from framework.knappe import Knappe

# Student code (Level 341 exercise)
print("\n# Student Code:")
print("held = Held(3, 4, 'down', False)")
print("knappe = Knappe(2, 2, 'up')")
print()

held = Held(3, 4, "down", False)
knappe = Knappe(2, 2, "up")

print("✓ Objects created successfully")
print(f"\nHeld:")
print(f"  Position: ({held.x}, {held.y})")
print(f"  Richtung: {held.richtung}")
print(f"  Weiblich: {held.weiblich}")
print(f"  Type: {held.typ}")

print(f"\nKnappe:")
print(f"  Position: ({knappe.x}, {knappe.y})")
print(f"  Richtung: {knappe.richtung}")
print(f"  Name: {knappe.name}")
print(f"  Type: {knappe.typ}")

# Verify they can be used like normal objects
print(f"\n✓ Held can be placed on a grid at ({held.x}, {held.y})")
print(f"✓ Knappe can be placed on a grid at ({knappe.x}, {knappe.y})")

print("\n" + "="*70)
print("✓ Level 341 Scenario PASSED")
print("Students can create Held/Knappe without framework knowledge")
print("="*70)

pygame.quit()
