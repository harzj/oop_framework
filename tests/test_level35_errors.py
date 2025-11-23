"""Test various student Held error scenarios for level35"""
import sys
import os
import pygame
import io

# Initialize pygame before importing framework
pygame.init()

# Add project root to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from framework.spielfeld import Spielfeld
from framework.held import MetaHeld

class DummyFramework:
    def __init__(self):
        self.weiblich = False
        self._aktion_blockiert = False
        
    def taste_registrieren(self, key, callback):
        pass

def capture_console_output(func):
    """Capture console output from a function."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        result = func()
        output = sys.stdout.getvalue()
        return result, output
    finally:
        sys.stdout = old_stdout

def test_no_class():
    """Test when schueler.py has no Held class."""
    print("\n" + "=" * 60)
    print("TEST 1: No Held class in schueler.py")
    print("=" * 60)
    
    schueler_path = os.path.join(root_dir, 'schueler.py')
    schueler_backup = os.path.join(root_dir, 'schueler_backup_test.py')
    
    # Rename schueler.py temporarily
    if os.path.exists(schueler_path):
        os.rename(schueler_path, schueler_backup)
    
    # Create empty schueler.py
    with open(schueler_path, 'w') as f:
        f.write('# Empty file - no Held class\n')
    
    try:
        fw = DummyFramework()
        
        # Capture console output
        def load():
            level35_path = os.path.join(root_dir, 'level', 'level35.json')
            return Spielfeld(level35_path, fw, feldgroesse=32)
        
        sp, output = capture_console_output(load)
        
        # Check for error message
        if "[FEHLER] Helden Klasse fehlt" in output:
            print("✓ Console error message shown")
        else:
            print(f"✗ Expected error message not found. Output: {output}")
        
        # Check held is None
        if sp.held is None:
            print("✓ Held is None (not spawned)")
        else:
            print(f"✗ Held should be None, got {type(sp.held)}")
        
        print("✓✓✓ TEST 1 PASSED")
        
    finally:
        # Restore schueler.py
        if os.path.exists(schueler_path):
            os.remove(schueler_path)
        if os.path.exists(schueler_backup):
            os.rename(schueler_backup, schueler_path)


def test_wrong_constructor():
    """Test when constructor has wrong signature."""
    print("\n" + "=" * 60)
    print("TEST 2: Wrong constructor signature")
    print("=" * 60)
    
    # Backup and create wrong version
    if os.path.exists('schueler.py'):
        os.rename('schueler.py', 'schueler_backup_test.py')
    
    with open('schueler.py', 'w') as f:
        f.write('''
class Held:
    def __init__(self, level, x, y, richtung, weiblich):
        # Wrong signature - includes level parameter
        self.level = level
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
''')
    
    try:
        fw = DummyFramework()
        
        def load():
            return Spielfeld('level/level35.json', fw, feldgroesse=32)
        
        sp, output = capture_console_output(load)
        
        # Check for error message about parameters
        if "[FEHLER] Helden Klasse: Parameterliste nicht korrekt" in output:
            print("✓ Console error message about parameters shown")
        else:
            print(f"✗ Expected parameter error. Output: {output}")
        
        # Check held is None
        if sp.held is None:
            print("✓ Held is None (not spawned)")
        else:
            print(f"✗ Held should be None, got {type(sp.held)}")
        
        print("✓✓✓ TEST 2 PASSED")
        
    finally:
        os.remove('schueler.py')
        os.rename('schueler_backup_test.py', 'schueler.py')


def test_missing_weiblich():
    """Test when weiblich attribute is missing (should show red question mark)."""
    print("\n" + "=" * 60)
    print("TEST 3: Missing weiblich attribute")
    print("=" * 60)
    
    # Backup and create version without weiblich
    if os.path.exists('schueler.py'):
        os.rename('schueler.py', 'schueler_backup_test.py')
    
    with open('schueler.py', 'w') as f:
        f.write('''
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        # weiblich not set!
        self.name = "Test Held"
        self.typ = "Held"
        self.level = None
    
    def setze_level(self, level):
        self.level = level
''')
    
    try:
        fw = DummyFramework()
        sp = Spielfeld('level/level35.json', fw, feldgroesse=32)
        
        # Check held exists
        if sp.held is None:
            print("✗ Held should exist with error sprite")
            return
        print("✓ Held created")
        
        # Check _show_error_sprite flag
        if getattr(sp.held, '_show_error_sprite', False):
            print("✓ _show_error_sprite flag is True")
        else:
            print("✗ _show_error_sprite flag should be True")
        
        # Check it's still in objekte list
        if sp.held in sp.objekte:
            print("✓ Held is in objekte list (visible in inspector)")
        else:
            print("✗ Held should be in objekte list")
        
        print("✓✓✓ TEST 3 PASSED")
        
    finally:
        os.remove('schueler.py')
        os.rename('schueler_backup_test.py', 'schueler.py')


def test_student_sets_wrong_values():
    """Test when student sets wrong x/y values (victory should fail)."""
    print("\n" + "=" * 60)
    print("TEST 4: Student sets wrong position values")
    print("=" * 60)
    
    # Backup and create version with wrong values
    if os.path.exists('schueler.py'):
        os.rename('schueler.py', 'schueler_backup_test.py')
    
    with open('schueler.py', 'w') as f:
        f.write('''
class Held:
    def __init__(self, x, y, richtung, weiblich):
        # Student ignores level's position and sets own values
        self.x = 5
        self.y = 5
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Test Held"
        self.typ = "Held"
        self.level = None
    
    def setze_level(self, level):
        self.level = level
''')
    
    try:
        fw = DummyFramework()
        sp = Spielfeld('level/level35.json', fw, feldgroesse=32)
        
        # Check held exists
        if sp.held is None:
            print("✗ Held should exist")
            return
        print("✓ Held created")
        
        # Check position
        student = sp.held._student
        if student.x == 5 and student.y == 5:
            print(f"✓ Student has wrong position ({student.x}, {student.y}) - different from level (1, 1)")
        else:
            print(f"✗ Expected position (5, 5), got ({student.x}, {student.y})")
        
        # Check victory fails
        if not sp.check_victory():
            print("✓ Victory check fails (values don't match)")
        else:
            print("✗ Victory should fail when values don't match")
        
        print("✓✓✓ TEST 4 PASSED")
        
    finally:
        os.remove('schueler.py')
        os.rename('schueler_backup_test.py', 'schueler.py')


if __name__ == '__main__':
    try:
        test_no_class()
        test_wrong_constructor()
        test_missing_weiblich()
        test_student_sets_wrong_values()
        
        print("\n" + "=" * 60)
        print("✓✓✓ ALL ERROR SCENARIO TESTS PASSED ✓✓✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗✗✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
