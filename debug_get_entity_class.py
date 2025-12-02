#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug _get_entity_class for Hindernis"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pygame
pygame.init()

from framework.spielfeld import Spielfeld
from framework.framework import Framework

print("Creating Framework and Spielfeld...")
fw = Framework()
s = Spielfeld('level/level48.json', fw)

print(f"\nclass_requirements: {s.class_requirements}")
print(f"Hindernis requirements: {s.class_requirements.get('Hindernis', {})}")

print("\nCalling _get_entity_class('Hindernis', None)...")
HindernisClass = s._get_entity_class('Hindernis', None)

print(f"Result: {HindernisClass}")
if HindernisClass:
    print(f"Type: {type(HindernisClass)}")
    print(f"Name: {HindernisClass.__name__}")
    print(f"Module: {HindernisClass.__module__}")
