#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug Level 49 needed classes"""

import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(__file__))

# Copy zettel_45 to zettel.py
shutil.copy('klassen/zettel_45.py', 'klassen/zettel.py')

# Clear modules
for mod_name in list(sys.modules.keys()):
    if 'framework' in mod_name or 'klassen' in mod_name:
        del sys.modules[mod_name]

import pygame
pygame.init()

from framework.grundlage import level
level.lade(49)
spielfeld = level.framework.spielfeld

print("=== Debug Info ===")
print(f"_zettel_student_mode_enabled: {getattr(spielfeld, '_zettel_student_mode_enabled', 'NOT SET')}")
print(f"_required_spawn_classes: {getattr(spielfeld, '_required_spawn_classes', 'NOT SET')}")

# Check mapping in check_victory
print("\n=== Checking victory logic ===")
zettel_req = spielfeld.class_requirements.get('Zettel', {})
print(f"Zettel requirements: {zettel_req}")

has_load_flags = bool(zettel_req.get('load_from_schueler') or zettel_req.get('load_from_klassen'))
has_inheritance = zettel_req.get('inherits') and zettel_req.get('inherits') != 'None'
has_methods = bool(zettel_req.get('methods') or zettel_req.get('methods_private'))
has_attributes = bool(zettel_req.get('attributes') or zettel_req.get('attributes_private'))

print(f"has_load_flags: {has_load_flags}")
print(f"has_inheritance: {has_inheritance}")
print(f"has_methods: {has_methods}")
print(f"has_attributes: {has_attributes}")

requires_student = has_load_flags or has_inheritance or has_methods or has_attributes
print(f"requires_student: {requires_student}")

print(f"\n_student_has_class('Zettel'): {spielfeld._student_has_class('Zettel')}")
print(f"check_victory(): {spielfeld.check_victory()}")

pygame.quit()
