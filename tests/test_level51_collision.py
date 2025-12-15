"""Test Level 51 - Charakter ohne Kollisionserkennung"""
import os
import sys

# Set test mode
os.environ['OOP_TEST'] = '1'
os.environ['PYTHONPATH'] = '.'

# Copy required class files
import shutil
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

print("Testing Level 51 (expects_set_level=false)...")
print("Should only test movement, NOT collision detection\n")

from framework.spielfeld import Spielfeld
from framework.framework import Framework

# Create Framework with level 51
f = Framework(51, auto_erzeuge_objekte=False)

import time
time.sleep(1)

print("\n=== Level 51 Test abgeschlossen ===")
print("Expected: VICTORY message if movement works")
print("Should NOT test collision detection")
