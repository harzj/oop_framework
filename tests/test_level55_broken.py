"""Test Level 55 mit fehlerhafter Kollisionserkennung"""
import os
import sys
import shutil

os.environ['OOP_TEST'] = '1'
os.environ['PYTHONPATH'] = '.'

print("=" * 70)
print("TEST: Level 55 mit charakter_broken_collision.py")
print("Erwartung: FEHLER - geh() erkennt Hindernisse nicht")
print("=" * 70)

# Copy broken charakter
shutil.copy('klassen/charakter_broken_collision.py', 'klassen/charakter.py')
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.spielfeld import Spielfeld
from framework.framework import Framework

# Test with level 55
f = Framework(55, auto_erzeuge_objekte=False)

import time
time.sleep(2)

print("\n" + "=" * 70)
print("TEST ABGESCHLOSSEN")
print("=" * 70)
print("\nErwartetes Ergebnis:")
print("FEHLER: 'kann in nicht-passierbare Objekte laufen' sollte ausgegeben werden")
