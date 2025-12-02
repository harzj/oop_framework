#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Zeige Name Mangling in allen Methoden"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'klassen'))

from spielobjekt import Spielobjekt

# Beispiel: Zettel mit zusätzlichen Methoden
class ZettelFalsch(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.__typ = "Zettel"  # _ZettelFalsch__typ
        self.__spruch = "Hallo"  # _ZettelFalsch__spruch
    
    def aendere_typ(self, neuer_typ):
        # FALSCH: Erstellt _ZettelFalsch__typ
        self.__typ = neuer_typ
    
    def zeige_info(self):
        # FALSCH: Liest _ZettelFalsch__typ (nicht was get_typ() zurückgibt!)
        print(f"Interner typ: {self.__typ}")
        print(f"get_typ() gibt: {self.get_typ()}")

class ZettelRichtig(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._Spielobjekt__typ = "Zettel"  # Überschreibt Parent
        self.__spruch = "Hallo"  # Eigenes neues Attribut (OK!)
    
    def aendere_typ(self, neuer_typ):
        # RICHTIG: Ändert das Parent-Attribut
        self._Spielobjekt__typ = neuer_typ
    
    def zeige_info(self):
        # RICHTIG: Konsistent mit get_typ()
        print(f"Interner typ: {self._Spielobjekt__typ}")
        print(f"get_typ() gibt: {self.get_typ()}")
    
    def get_spruch(self):
        # HIER ist self.__spruch OK, weil es ein EIGENES Attribut ist!
        return self.__spruch

print("="*70)
print("Name Mangling in ALLEN Methoden")
print("="*70)

print("\n=== FALSCHE Version ===")
z1 = ZettelFalsch(5, 10)
print(f"Nach __init__: get_typ() = {z1.get_typ()}")
z1.zeige_info()

print("\nÄndere Typ...")
z1.aendere_typ("Dokument")
z1.zeige_info()
print(f"Aber get_typ() gibt: {z1.get_typ()}")
print("  → get_typ() hat sich NICHT geändert!")

print("\n" + "="*70)
print("=== RICHTIGE Version ===")
z2 = ZettelRichtig(5, 10)
print(f"Nach __init__: get_typ() = {z2.get_typ()}")
z2.zeige_info()

print("\nÄndere Typ...")
z2.aendere_typ("Dokument")
z2.zeige_info()
print(f"Und get_typ() gibt: {z2.get_typ()}")
print("  → Alles konsistent!")

print("\n" + "="*70)
print("REGEL:")
print("="*70)
print("Für GEERBTE private Attribute (__x, __y, __typ):")
print("  → Immer self._Spielobjekt__attribut verwenden")
print("  → In __init__, in Settern, in allen Methoden!")
print()
print("Für EIGENE neue private Attribute (__spruch):")
print("  → Normal self.__spruch verwenden")
print("  → Wird zu _KlassenName__spruch (eigenes Attribut)")
print("="*70)
