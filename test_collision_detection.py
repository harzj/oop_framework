"""Test Charakter geh() mit und ohne Kollisionserkennung"""
import os
import sys
import shutil

os.environ['OOP_TEST'] = '1'
os.environ['PYTHONPATH'] = '.'

print("=" * 70)
print("TEST 1: Level 51 - expects_set_level=false")
print("Sollte NUR Bewegung testen, NICHT Kollisionserkennung")
print("=" * 70)

# Copy files for test 1
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.spielfeld import Spielfeld
from framework.framework import Framework

f1 = Framework(51, auto_erzeuge_objekte=False)
import time
time.sleep(1.5)

print("\n" + "=" * 70)
print("TEST 2: Level 51_with_collision - expects_set_level=true")
print("Sollte Bewegung UND Kollisionserkennung testen")
print("=" * 70)

# Copy files for test 2
shutil.copy('klassen/charakter_with_collision.py', 'klassen/charakter.py')

# Need to reload modules
import importlib
import sys
if 'klassen.charakter' in sys.modules:
    del sys.modules['klassen.charakter']
if 'framework.spielfeld' in sys.modules:
    del sys.modules['framework.spielfeld']

from framework.spielfeld import Spielfeld as Spielfeld2

# Create spielfeld directly with custom level
s2 = Spielfeld2('level/level51_with_collision.json', f1)
time.sleep(1.5)

print("\n" + "=" * 70)
print("TESTS ABGESCHLOSSEN")
print("=" * 70)
print("\nErwartete Ergebnisse:")
print("Test 1: Charakter bewegt sich korrekt -> VICTORY")
print("Test 2: Charakter erkennt Hindernisse -> VICTORY")
print("        (testet set_level und Kollisionserkennung)")
