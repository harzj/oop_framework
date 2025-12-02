#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug script for Level 48 Hindernis loading"""

import sys
import os

# Add repo root to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import pygame
pygame.init()

from framework.spielfeld import Spielfeld
from framework.framework import Framework

print("Loading Level 48...")
fw = Framework()
s = Spielfeld('level/level48.json', fw)
# Enable debug output
s._debug_hindernis_spawn = True

print("\n=== Spielfeld State ===")
print(f"_hindernis_class_valid: {s._hindernis_class_valid}")
print(f"Number of objekte: {len(s.objekte)}")

# Filter for Hindernis objects
hindernisse = [obj for obj in s.objekte if 'Hindernis' in type(obj).__name__]
print(f"Number of Hindernis objects: {len(hindernisse)}")

if len(hindernisse) > 0:
    h = hindernisse[0]
    print(f"\n=== First Hindernis ===")
    print(f"Type: {type(h)}")
    print(f"Type name: {type(h).__name__}")
    print(f"Has _student: {hasattr(h, '_student')}")
    
    if hasattr(h, '_student'):
        print(f"_student type: {type(h._student)}")
        print(f"_student type name: {type(h._student).__name__}")
        print(f"_student has get_typ: {hasattr(h._student, 'get_typ')}")
        if hasattr(h._student, 'get_typ'):
            try:
                typ = h._student.get_typ()
                print(f"get_typ() returns: {typ}")
            except Exception as e:
                print(f"get_typ() error: {e}")
    else:
        print("WARNING: No _student attribute!")
        print(f"Hindernis attributes: {[a for a in dir(h) if not a.startswith('__')]}")
else:
    print("\nWARNING: No Hindernis objects found in objekte!")

print("\n=== Victory Check ===")
print(f"check_victory(): {s.check_victory()}")
