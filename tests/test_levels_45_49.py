"""
Comprehensive Tests for Levels 45-49 (Hindernis, Zettel, Knappe)

This test suite validates:
- Level 45: Zettel class (standalone, no inheritance)
- Level 46: Knappe class (standalone, private attributes)
- Level 47: Spielobjekt class (private attributes, no objects spawned)
- Level 48: Hindernis inherits from Spielobjekt (name mangling)
- Level 49: Multiple classes with inheritance (Spielobjekt, Hindernis, Zettel)
"""

import os
import sys
import shutil
import tempfile
import subprocess

def run_test_in_subprocess(test_name, code):
    """Run test in subprocess to ensure fresh imports"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, '-c', code],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(__file__)
    )
    
    print(result.stdout)
    if result.stderr and 'pygame' not in result.stderr.lower():
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

# ==============================================================================
# LEVEL 45 TESTS: Zettel (standalone, private attributes)
# ==============================================================================

test_level45_correct = """
# Test Level 45: Correct Zettel implementation
import shutil
shutil.copy('klassen/zettel_45.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(45, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 45 should pass with correct Zettel implementation"
print("✓ PASS: Level 45 with correct Zettel")
"""

test_level45_public_attrs = """
# Test Level 45: Zettel with PUBLIC attributes (should FAIL)
with open('klassen/zettel.py', 'w', encoding='utf-8') as f:
    f.write('''
class Zettel:
    def __init__(self, x, y):
        self.typ = "Zettel"  # PUBLIC (wrong!)
        self.x = x
        self.y = y
        self.spruch = "Sesam öffne dich"

    def ist_passierbar(self):
        return True
    
    def get_typ(self):
        return self.typ
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_spruch(self):
        return self.spruch
    
    def set_spruch(self, spruch):
        self.spruch = spruch
''')

from framework.grundlage import level
level.lade(45, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (public attributes)")
assert not victory, "Level 45 should fail with public attributes"
print("✓ PASS: Level 45 correctly rejects public attributes")
"""

test_level45_missing_methods = """
# Test Level 45: Zettel missing set_spruch (should FAIL)
with open('klassen/zettel.py', 'w', encoding='utf-8') as f:
    f.write('''
class Zettel:
    def __init__(self, x, y):
        self.__typ = "Zettel"
        self.__x = x
        self.__y = y
        self.__spruch = "Sesam öffne dich"

    def ist_passierbar(self):
        return True
    
    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def get_spruch(self):
        return self.__spruch
    
    # Missing set_spruch!
''')

from framework.grundlage import level
level.lade(45, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (missing set_spruch)")
assert not victory, "Level 45 should fail without set_spruch"
print("✓ PASS: Level 45 correctly rejects missing set_spruch")
"""

# ==============================================================================
# LEVEL 46 TESTS: Knappe (standalone, private attributes)
# ==============================================================================

test_level46_correct = """
# Test Level 46: Correct Knappe implementation
import shutil
shutil.copy('klassen/knappe_46.py', 'klassen/knappe.py')

from framework.grundlage import level
level.lade(46, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 46 should pass with correct Knappe implementation"
print("✓ PASS: Level 46 with correct Knappe")
"""

test_level46_public_attrs = """
# Test Level 46: Knappe with PUBLIC attributes (should FAIL)
with open('klassen/knappe.py', 'w', encoding='utf-8') as f:
    f.write('''
class Knappe:
    def __init__(self, x, y, richtung):
        self.x = x  # PUBLIC (wrong!)
        self.y = y
        self.richtung = richtung
        self.name = "Namenloser Knappe"
        self.typ = "Knappe"

    def set_richtung(self, neue_richtung):
        if neue_richtung in ["up", "down", "left", "right"]:
            self.richtung = neue_richtung

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_richtung(self):
        return self.richtung
    
    def get_typ(self):
        return self.typ
    
    def geh(self):
        if self.richtung == "up":
            self.y -= 1
        elif self.richtung == "down":
            self.y += 1
        elif self.richtung == "left":
            self.x -= 1
        elif self.richtung == "right":
            self.x += 1
    
    def links(self):
        if self.richtung == "up":
            self.richtung = "left"
        elif self.richtung == "down":
            self.richtung = "right"
        elif self.richtung == "left":
            self.richtung = "down"
        elif self.richtung == "right":
            self.richtung = "up"
    
    def rechts(self):
        if self.richtung == "up":
            self.richtung = "right"
        elif self.richtung == "down":
            self.richtung = "left"
        elif self.richtung == "left":
            self.richtung = "up"
        elif self.richtung == "right":
            self.richtung = "down"
''')

from framework.grundlage import level
level.lade(46, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (public attributes)")
assert not victory, "Level 46 should fail with public attributes"
print("✓ PASS: Level 46 correctly rejects public attributes")
"""

# ==============================================================================
# LEVEL 47 TESTS: Spielobjekt (abstract class, private attributes)
# ==============================================================================

test_level47_correct = """
# Test Level 47: Correct Spielobjekt with PRIVATE attributes
import shutil
shutil.copy('klassen/spielobjekt_47.py', 'klassen/spielobjekt.py')

from framework.grundlage import level
level.lade(47, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 47 should pass with private attributes"
print("✓ PASS: Level 47 with private attributes")
"""

test_level47_public_attrs = """
# Test Level 47: Spielobjekt with PUBLIC attributes (should FAIL)
with open('klassen/spielobjekt.py', 'w', encoding='utf-8') as f:
    f.write('''
class Spielobjekt:
    def __init__(self, x, y):
        self.typ = "Spielobjekt"  # PUBLIC (wrong!)
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

from framework.grundlage import level
level.lade(47, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (public attributes)")
assert not victory, "Level 47 should fail with public attributes"
print("✓ PASS: Level 47 correctly rejects public attributes")
"""

# ==============================================================================
# LEVEL 48 TESTS: Hindernis inherits from Spielobjekt (name mangling)
# ==============================================================================

test_level48_correct = """
# Test Level 48: Correct Hindernis with Spielobjekt inheritance
import shutil
shutil.copy('klassen/spielobjekt_47.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_48.py', 'klassen/hindernis.py')

from framework.grundlage import level
level.lade(48, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 48 should pass with correct inheritance"
print("✓ PASS: Level 48 with correct Hindernis inheritance")
"""

test_level48_wrong_name_mangling = """
# Test Level 48: Hindernis with WRONG name mangling (should FAIL)
import shutil
shutil.copy('klassen/spielobjekt_47.py', 'klassen/spielobjekt.py')

with open('klassen/hindernis.py', 'w', encoding='utf-8') as f:
    f.write('''
from spielobjekt import *

class Hindernis(Spielobjekt):
    def __init__(self, x, y, art):
        super().__init__(x, y)
        self.__typ = art  # WRONG! Should be self._Spielobjekt__typ
''')

from framework.grundlage import level
level.lade(48, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (wrong name mangling)")
assert not victory, "Level 48 should fail with wrong name mangling"
print("✓ PASS: Level 48 correctly rejects wrong name mangling")
"""

# ==============================================================================
# LEVEL 49 TESTS: Spielobjekt + Hindernis + Zettel inheritance
# ==============================================================================

test_level49_correct = """
# Test Level 49: Complete inheritance hierarchy
import shutil
shutil.copy('klassen/spielobjekt_47.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_48.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_49.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(49, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 49 should pass with correct implementation"
print("✓ PASS: Level 49 with complete inheritance")
"""

# ==============================================================================
# RUN ALL TESTS
# ==============================================================================

if __name__ == "__main__":
    tests = [
        ("Level 45: Correct Zettel", test_level45_correct),
        ("Level 45: Public Attrs (should fail)", test_level45_public_attrs),
        ("Level 45: Missing Methods (should fail)", test_level45_missing_methods),
        ("Level 46: Correct Knappe", test_level46_correct),
        ("Level 46: Public Attrs (should fail)", test_level46_public_attrs),
        ("Level 47: Correct Spielobjekt", test_level47_correct),
        ("Level 47: Public Attrs (should fail)", test_level47_public_attrs),
        ("Level 48: Correct Hindernis", test_level48_correct),
        ("Level 48: Wrong Name Mangling (should fail)", test_level48_wrong_name_mangling),
        ("Level 49: Complete Hierarchy", test_level49_correct),
    ]
    
    passed = 0
    failed = 0
    
    for name, code in tests:
        try:
            success = run_test_in_subprocess(name, code)
            if success:
                passed += 1
            else:
                failed += 1
                print(f"✗ FAILED: {name}")
        except Exception as e:
            failed += 1
            print(f"✗ EXCEPTION in {name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print('='*60)
    
    sys.exit(0 if failed == 0 else 1)
