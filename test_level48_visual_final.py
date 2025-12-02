#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visual test Level 48 - Check if Hindernisse render correctly"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Level 48 Visual Test")

from framework.grundlage import level
level.lade(48)

spielfeld = level.framework.spielfeld
feldgroesse = 80

print(f"Loaded Level 48")
print(f"Hindernisse count: {len([o for o in spielfeld.objekte if 'Hindernis' in type(o).__name__])}")
print(f"_hindernis_class_valid: {spielfeld._hindernis_class_valid}")

# Draw
screen.fill((255, 255, 255))
spielfeld.zeichne(screen)
pygame.display.flip()

# Save screenshot
pygame.image.save(screen, "test_level48_visual.png")
print("Screenshot saved: test_level48_visual.png")

# Check Hindernis types
hindernisse = [o for o in spielfeld.objekte if 'Hindernis' in type(o).__name__]
if hindernisse:
    h = hindernisse[0]
    print(f"\nFirst Hindernis:")
    print(f"  typ attribute: {h.typ}")
    print(f"  has _student: {hasattr(h, '_student')}")
    if hasattr(h, '_student'):
        print(f"  _student.get_typ(): {h._student.get_typ()}")

# Wait for user to close
print("\nPress any key to exit...")
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            running = False

pygame.quit()
