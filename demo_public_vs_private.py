#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Vergleich: Public vs Private Attribute bei Vererbung"""

print("="*70)
print("PUBLIC Attribute (KEIN Name Mangling)")
print("="*70)

class A_Public:
    def __init__(self):
        self.x = 5  # PUBLIC: Nur EIN Unterstrich (oder keiner)
        
class B_Public(A_Public):
    def __init__(self):
        super().__init__()
        self.y = self.x  # ✓ Funktioniert direkt!
        
    def add(self):
        self.x = self.x + 1  # ✓ Funktioniert direkt!

b = B_Public()
b.add()
print(f"x = {b.x}")
print(f"y = {b.y}")
print("→ KEIN Name Mangling bei public (self.x)")

print("\n" + "="*70)
print("PRIVATE Attribute (MIT Name Mangling)")
print("="*70)

class A_Private:
    def __init__(self):
        self.__x = 5  # PRIVATE: ZWEI Unterstriche!
        
class B_Private_FALSCH(A_Private):
    def __init__(self):
        super().__init__()
        self.__y = self.__x  # ✗ AttributeError!

class B_Private_RICHTIG(A_Private):
    def __init__(self):
        super().__init__()
        self.__y = self._A_Private__x  # ✓ Muss Parent-Notation verwenden!
    
    def add(self):
        self._A_Private__x = self._A_Private__x + 1  # ✓ Parent-Notation

# Test FALSCHE Version
print("\n--- FALSCH: self.__x in Child ---")
try:
    b_falsch = B_Private_FALSCH()
    print("Sollte nicht hierher kommen!")
except AttributeError as e:
    print(f"✗ AttributeError: {e}")
    print("  → self.__x in B_Private wird zu _B_Private__x")
    print("  → Aber das existiert nicht! Parent hat _A_Private__x")

# Test RICHTIGE Version
print("\n--- RICHTIG: self._A_Private__x ---")
b_richtig = B_Private_RICHTIG()
b_richtig.add()
print(f"x = {b_richtig._A_Private__x}")
print(f"y = {b_richtig._B_Private_RICHTIG__y}")
print("→ Funktioniert mit expliziter Parent-Notation")

print("\n" + "="*70)
print("FAZIT")
print("="*70)
print("self.x       → PUBLIC  → Kein Name Mangling → Einfach vererbbar")
print("self.__x     → PRIVATE → Name Mangling zu _Klasse__x")
print()
print("Bei Vererbung mit PRIVATE Attributen:")
print("  Child muss self._ParentKlasse__attribut verwenden")
print()
print("Daher: In Spielobjekt/Hindernis/Zettel:")
print("  Parent: self.__typ → _Spielobjekt__typ")
print("  Child:  Muss self._Spielobjekt__typ verwenden!")
print("="*70)
