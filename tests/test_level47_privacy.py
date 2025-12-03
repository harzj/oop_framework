"""Test Level 47: Spielobjekt privacy validation"""
import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(__file__))

# Test with CORRECT implementation (private attributes)
print("=== Test 1: Korrekte Implementierung (private Attribute) ===")
with open('klassen/spielobjekt.py', 'w', encoding='utf-8') as f:
    f.write('''# Korrekte Implementierung mit privaten Attributen
class Spielobjekt:
    def __init__(self, x, y):
        self.__typ = "Spielobjekt"
        self.__x = x
        self.__y = y

    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def ist_passierbar(self):
        return False
''')

# Load level
from framework.grundlage import level
level.lade(47, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld
print(f"Victory Status: {spielfeld.check_victory()}")
print(f"Victory sollte TRUE sein (private Attribute korrekt)")

# Test with WRONG implementation (public attributes)
print("\n=== Test 2: Falsche Implementierung (öffentliche Attribute) ===")
with open('klassen/spielobjekt.py', 'w', encoding='utf-8') as f:
    f.write('''# Falsche Implementierung mit öffentlichen Attributen
class Spielobjekt:
    def __init__(self, x, y):
        self.typ = "Spielobjekt"
        self.x = x
        self.y = y

    def get_typ(self):
        return self.typ
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def ist_passierbar(self):
        return False
''')

# Reload level
level.lade(47, weiblich=True)
from framework.grundlage import framework as fw2
spielfeld2 = fw2.spielfeld
print(f"Victory Status: {spielfeld2.check_victory()}")
print(f"Victory sollte FALSE sein (öffentliche Attribute falsch)")

# Restore correct version
with open('klassen/spielobjekt.py', 'w', encoding='utf-8') as f:
    f.write('''# Korrekte Implementierung mit privaten Attributen
class Spielobjekt:
    def __init__(self, x, y):
        self.__typ = "Spielobjekt"
        self.__x = x
        self.__y = y

    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def ist_passierbar(self):
        return False
''')

print("\n✓ Spielobjekt.py wiederhergestellt")
