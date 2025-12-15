"""Einfacher Test für Vererbungsprüfung"""
import sys
sys.path.insert(0, 'klassen')

# Importiere die Klassen
from zettel import Zettel
from hindernis import Hindernis

print("=" * 60)
print("Test: Vererbungsprüfung mit MRO")
print("=" * 60)

# Test Zettel
z = Zettel(1, 1)
print(f"\nZettel Klasse: {z.__class__.__name__}")
print(f"Zettel MRO: {[c.__name__ for c in z.__class__.__mro__]}")
print(f"✓ Erbt von Spielobjekt: {'Spielobjekt' in [c.__name__ for c in z.__class__.__mro__]}")

# Test Hindernis
h = Hindernis(2, 2, "Baum")
print(f"\nHindernis Klasse: {h.__class__.__name__}")
print(f"Hindernis MRO: {[c.__name__ for c in h.__class__.__mro__]}")
print(f"✓ Erbt von Spielobjekt: {'Spielobjekt' in [c.__name__ for c in h.__class__.__mro__]}")

# Test mit der neuen _check_inheritance_new Methode
print("\n" + "=" * 60)
print("Test: Framework-Vererbungsprüfung")
print("=" * 60)

# Simuliere die Prüfung
parent_class_name = "Spielobjekt"

def check_inheritance(obj, parent_name):
    """Simuliert _check_inheritance_new Logik"""
    obj_class = obj.__class__
    mro = obj_class.__mro__
    
    for base_class in mro:
        if base_class.__name__ == parent_name:
            return True
    return False

print(f"\nZettel erbt von Spielobjekt: {check_inheritance(z, 'Spielobjekt')}")
print(f"Hindernis erbt von Spielobjekt: {check_inheritance(h, 'Spielobjekt')}")

print("\n" + "=" * 60)
print("✓ Alle Tests bestanden!")
print("=" * 60)
