"""
Comprehensive Tests for Levels 50-53 (Public Attributes & Inheritance)

This test suite validates:
- Level 50: Spielobjekt, Hindernis, Zettel with PUBLIC attributes
- Level 51: Charakter inherits from Spielobjekt (public attributes)
- Level 52: Held inherits from Charakter (public attributes)
- Level 53: Knappe inherits from Charakter (public attributes)
"""

import os
import sys
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
# LEVEL 50 TESTS: Spielobjekt + Hindernis + Zettel with PUBLIC attributes
# ==============================================================================

test_level50_correct = """
# Test Level 50: Correct implementation with public attributes
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(50, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 50 should pass with public attributes"
print("✓ PASS: Level 50 with public attributes")
"""

test_level50_private_attrs = """
# Test Level 50: With PRIVATE attributes (should FAIL - wrong for Level 50+)
import shutil
# Use Level 47 version (private) instead of Level 50 (public)
shutil.copy('klassen/spielobjekt_47.py', 'klassen/spielobjekt.py')

with open('klassen/hindernis.py', 'w', encoding='utf-8') as f:
    f.write('''
from spielobjekt import *

class Hindernis(Spielobjekt):
    def __init__(self, x, y, art):
        super().__init__(x, y)
        self._Spielobjekt__typ = art  # Name mangling (WRONG for Level 50!)
''')

with open('klassen/zettel.py', 'w', encoding='utf-8') as f:
    f.write('''
from spielobjekt import *

class Zettel(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)  
        self._Spielobjekt__typ = "Zettel"  # Name mangling (WRONG!)
        self.__spruch = "Sesam öffne dich"

    def get_spruch(self):
        return self.__spruch
    
    def set_spruch(self, spruch):
        self.__spruch = spruch
''')

from framework.grundlage import level
level.lade(50, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (private attributes not allowed in Level 50+)")
assert not victory, "Level 50 should fail with private attributes"
print("✓ PASS: Level 50 correctly rejects private attributes")
"""

# ==============================================================================
# LEVEL 51 TESTS: Charakter inherits from Spielobjekt
# ==============================================================================

test_level51_correct = """
# Test Level 51: Correct Charakter implementation
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(51, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 51 should pass with correct Charakter"
print("✓ PASS: Level 51 with correct Charakter inheritance")
"""

test_level51_missing_methods = """
# Test Level 51: Charakter missing methods (should FAIL)
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

with open('klassen/charakter.py', 'w', encoding='utf-8') as f:
    f.write('''
from spielobjekt import Spielobjekt

class Charakter(Spielobjekt):
    def __init__(self, x, y, richtung):
        super().__init__(x,y)
        self.richtung = richtung
        self.name = "Namenloser Charakter"
        self.typ = "Charakter"
    
    # Missing: geh(), links(), rechts(), set_richtung(), get_richtung()
''')

from framework.grundlage import level
level.lade(51, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (missing methods)")
assert not victory, "Level 51 should fail without required methods"
print("✓ PASS: Level 51 correctly rejects missing methods")
"""

# ==============================================================================
# LEVEL 52 TESTS: Held inherits from Charakter
# ==============================================================================

test_level52_correct = """
# Test Level 52: Correct Held implementation
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/held_52.py', 'klassen/held.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(52, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 52 should pass with correct Held"
print("✓ PASS: Level 52 with correct Held inheritance")
"""

test_level52_wrong_inheritance = """
# Test Level 52: Held NOT inheriting from Charakter (should FAIL)
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

with open('klassen/held.py', 'w', encoding='utf-8') as f:
    f.write('''
# Wrong: Held should inherit from Charakter, not Spielobjekt directly!
from spielobjekt import Spielobjekt

class Held(Spielobjekt):  # WRONG BASE CLASS!
    def __init__(self, x, y, richtung, weiblich):
        super().__init__(x, y)
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
    
    def get_weiblich(self):
        return self.weiblich
    
    # Missing all Charakter methods!
''')

from framework.grundlage import level
level.lade(52, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (wrong inheritance)")
assert not victory, "Level 52 should fail with wrong base class"
print("✓ PASS: Level 52 correctly rejects wrong inheritance")
"""

test_level52_private_weiblich = """
# Test Level 52: Held with PRIVATE weiblich (should FAIL)
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

with open('klassen/held.py', 'w', encoding='utf-8') as f:
    f.write('''
from charakter import Charakter

class Held(Charakter):
    def __init__(self, x, y, richtung, weiblich):
        super().__init__(x, y, richtung)
        self.__weiblich = weiblich  # PRIVATE (wrong for Level 50+)
        self.name = "Namenloser Held"
        self.typ = "Held"
        
    def get_weiblich(self):
        return self.__weiblich
''')

from framework.grundlage import level
level.lade(52, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (weiblich should be public)")
assert not victory, "Level 52 should fail with private weiblich"
print("✓ PASS: Level 52 correctly rejects private weiblich")
"""

# ==============================================================================
# LEVEL 53 TESTS: Knappe inherits from Charakter
# ==============================================================================

test_level53_correct = """
# Test Level 53: Correct Knappe implementation
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/held_52.py', 'klassen/held.py')
shutil.copy('klassen/knappe_53.py', 'klassen/knappe.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(53, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: True")
assert victory, "Level 53 should pass with correct Knappe"
print("✓ PASS: Level 53 with correct Knappe inheritance")
"""

test_level53_wrong_base = """
# Test Level 53: Knappe NOT inheriting from Charakter (should FAIL)
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/held_52.py', 'klassen/held.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

with open('klassen/knappe.py', 'w', encoding='utf-8') as f:
    f.write('''
# Wrong: Standalone class instead of inheriting from Charakter
class Knappe:
    def __init__(self, x, y, richtung):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.name = "Namenloser Knappe"
        self.typ = "Knappe"
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    # All other methods...
''')

from framework.grundlage import level
level.lade(53, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (must inherit from Charakter)")
assert not victory, "Level 53 should fail without Charakter inheritance"
print("✓ PASS: Level 53 correctly rejects standalone Knappe")
"""

# ==============================================================================
# BACKWARD COMPATIBILITY TESTS: Old implementations should NOT solve new levels
# ==============================================================================

test_level50_with_level47_classes = """
# Test Level 50: Using Level 47 classes (PRIVATE attrs) should FAIL
import shutil
shutil.copy('klassen/spielobjekt_47.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_47.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_47.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(50, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (Level 47 uses private attrs, Level 50+ needs public)")
assert not victory, "Level 50 should reject Level 47 implementations"
print("✓ PASS: Level 50 correctly rejects Level 47 private attributes")
"""

test_level51_without_charakter = """
# Test Level 51: Without Charakter class should FAIL
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')
# Don't copy charakter.py - simulate Level 50 state

with open('klassen/charakter.py', 'w', encoding='utf-8') as f:
    f.write('# Empty file - no Charakter class\\n')

from framework.grundlage import level
level.lade(51, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (Charakter class missing)")
assert not victory, "Level 51 should fail without Charakter class"
print("✓ PASS: Level 51 correctly rejects missing Charakter")
"""

test_level52_with_level43_held = """
# Test Level 52: Using Level 43 Held (PRIVATE attrs) should FAIL
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/held_43.py', 'klassen/held.py')  # Old Held with private attrs
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(52, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (Level 43 Held uses private attrs, Level 52 needs public)")
assert not victory, "Level 52 should reject Level 43 Held with private attributes"
print("✓ PASS: Level 52 correctly rejects Level 43 private Held")
"""

test_level53_with_level46_knappe = """
# Test Level 53: Using Level 46 Knappe (PRIVATE attrs) should FAIL
import shutil
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/held_52.py', 'klassen/held.py')
shutil.copy('klassen/knappe_46.py', 'klassen/knappe.py')  # Old Knappe with private attrs
shutil.copy('klassen/hindernis_50.py', 'klassen/hindernis.py')
shutil.copy('klassen/zettel_50.py', 'klassen/zettel.py')

from framework.grundlage import level
level.lade(53, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

victory = spielfeld.check_victory()
print(f"Victory Status: {victory}")
print(f"Expected: False (Level 46 Knappe uses private attrs, Level 53 needs public)")
assert not victory, "Level 53 should reject Level 46 Knappe with private attributes"
print("✓ PASS: Level 53 correctly rejects Level 46 private Knappe")
"""

# ==============================================================================
# RUN ALL TESTS
# ==============================================================================

if __name__ == "__main__":
    tests = [
        ("Level 50: Correct (public attrs)", test_level50_correct),
        ("Level 50: Private attrs (should fail)", test_level50_private_attrs),
        ("Level 50: Level 47 classes (should fail)", test_level50_with_level47_classes),
        ("Level 51: Correct Charakter", test_level51_correct),
        ("Level 51: Missing methods (should fail)", test_level51_missing_methods),
        ("Level 51: Without Charakter class (should fail)", test_level51_without_charakter),
        ("Level 52: Correct Held", test_level52_correct),
        ("Level 52: Wrong inheritance (should fail)", test_level52_wrong_inheritance),
        ("Level 52: Private weiblich (should fail)", test_level52_private_weiblich),
        ("Level 52: Level 43 Held (should fail)", test_level52_with_level43_held),
        ("Level 53: Correct Knappe", test_level53_correct),
        ("Level 53: Wrong base class (should fail)", test_level53_wrong_base),
        ("Level 53: Level 46 Knappe (should fail)", test_level53_with_level46_knappe),
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
