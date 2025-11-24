"""Test Inspector UI Rendering for Level 37 with private attributes"""
import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.grundlage import level

# Load Level 38 with private attributes
level.lade(38, weiblich=False)

from framework.grundlage import *

print("=" * 70)
print("Inspector UI Test - Level 38 mit privaten Attributen")
print("=" * 70)
print()
print("Instructions:")
print("1. Das Spiel startet mit dem Objektinspektor auf der linken Seite")
print("2. Prüfe, ob folgende Attribute sichtbar sind:")
print("   - x: 1")
print("   - y: 1")
print("   - richtung: down")
print("3. Bewege den Held mit Pfeiltasten")
print("4. Prüfe, ob x, y, richtung sich aktualisieren")
print()
print("Drücke F1 um zu starten...")
print("=" * 70)

framework.starten()
