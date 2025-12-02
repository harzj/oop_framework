#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Demonstriere Name Mangling Problem"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'klassen'))

from spielobjekt import Spielobjekt

# FALSCH: Verwendet self.__typ in Child-Klasse
class ZettelWrong(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.__typ = "Zettel"  # Wird zu _ZettelWrong__typ

# RICHTIG: Verwendet self._Spielobjekt__typ
class ZettelRight(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._Spielobjekt__typ = "Zettel"  # Überschreibt Parent-Attribut

print("="*70)
print("Python Name Mangling bei Vererbung")
print("="*70)

# Test FALSCHE Version
z1 = ZettelWrong(5, 10)
print("\n=== FALSCH: self.__typ in Child-Klasse ===")
print(f"get_typ() gibt zurück: {z1.get_typ()}")
print(f"  → get_typ() liest _Spielobjekt__typ")
print(f"  → Das ist immer noch None (vom Parent __init__)")
print(f"\nAttribut-Liste:")
print(f"  Hat _ZettelWrong__typ: {hasattr(z1, '_ZettelWrong__typ')}")
print(f"  Wert: {getattr(z1, '_ZettelWrong__typ', 'N/A')}")
print(f"  Hat _Spielobjekt__typ: {hasattr(z1, '_Spielobjekt__typ')}")
print(f"  Wert: {getattr(z1, '_Spielobjekt__typ', 'N/A')}")

# Test RICHTIGE Version
z2 = ZettelRight(5, 10)
print("\n=== RICHTIG: self._Spielobjekt__typ ===")
print(f"get_typ() gibt zurück: {z2.get_typ()}")
print(f"  → get_typ() liest _Spielobjekt__typ")
print(f"  → Das wurde korrekt auf 'Zettel' gesetzt")
print(f"\nAttribut-Liste:")
print(f"  Hat _ZettelRight__typ: {hasattr(z2, '_ZettelRight__typ')}")
print(f"  Hat _Spielobjekt__typ: {hasattr(z2, '_Spielobjekt__typ')}")
print(f"  Wert: {getattr(z2, '_Spielobjekt__typ', 'N/A')}")

print("\n" + "="*70)
print("FAZIT:")
print("="*70)
print("Private Attribute (__name) werden klassenspezifisch umbenannt:")
print("  - In Spielobjekt: __typ → _Spielobjekt__typ")
print("  - In Zettel:      __typ → _Zettel__typ")
print()
print("Um das Parent-Attribut zu überschreiben, MUSS man schreiben:")
print("  self._Spielobjekt__typ = ...")
print()
print("Sonst erstellt man ein NEUES Attribut, das get_typ() nicht findet!")
print("="*70)
