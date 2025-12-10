"""Test Charakter mit fehlerhafter Kollisionserkennung"""
import os
import sys
import shutil

os.environ['OOP_TEST'] = '1'
os.environ['PYTHONPATH'] = '.'

print("=" * 70)
print("TEST: Charakter MIT set_level OHNE Kollisionserkennung")
print("Erwartung: FEHLER - geh() erkennt Hindernisse nicht")
print("=" * 70)

# Copy broken charakter
shutil.copy('klassen/charakter_broken_collision.py', 'klassen/charakter.py')
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.spielfeld import Spielfeld
from framework.framework import Framework

# Use custom level with expects_set_level=true
f = Framework(51, auto_erzeuge_objekte=False)
s = Spielfeld('level/level51_with_collision.json', f)

import time
time.sleep(1.5)

print("\n" + "=" * 70)
print("TEST ABGESCHLOSSEN")
print("=" * 70)
print("\nErwartetes Ergebnis:")
print("FEHLER: 'geh() erkennt Hindernis nicht' sollte ausgegeben werden")
