"""Test Level 55 mit charakter_55.py"""
import os
import sys
import shutil

os.environ['OOP_TEST'] = '1'
os.environ['PYTHONPATH'] = '.'

print("=" * 70)
print("TEST: Level 55 mit charakter_55.py (erwartet level.gib_objekt_bei)")
print("=" * 70)

# Copy charakter_55
shutil.copy('klassen/charakter_55.py', 'klassen/charakter.py')
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.spielfeld import Spielfeld
from framework.framework import Framework

# Test with level 55
f = Framework(55, auto_erzeuge_objekte=False)

import time
time.sleep(1.5)

print("\n" + "=" * 70)
print("TEST ABGESCHLOSSEN")
print("=" * 70)
print("\nErwartetes Ergebnis:")
print("KEIN Fehler mehr - geh() sollte mit self.spielfeld funktionieren")
