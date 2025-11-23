"""Test that student can control Held position independently from level definition"""
import sys
import os
import pygame
import shutil

# Initialize pygame before importing framework
pygame.init()

# Add project root to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Backup schueler.py
schueler_path = os.path.join(root_dir, 'schueler.py')
backup_path = os.path.join(root_dir, 'schueler_backup_test.py')
if os.path.exists(schueler_path):
    shutil.copy2(schueler_path, backup_path)

try:
    print("=" * 70)
    print("Test 1: Student sets position to (0,0) instead of level's (1,1)")
    print("=" * 70)

    # Create test schueler.py with wrong position
    test_schueler = """
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = 0  # Student chooses different position
        self.y = 0
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Test Held"
        self.typ = "Held"
        self.level = None
    
    def setze_level(self, level):
        self.level = level
"""

    with open(schueler_path, 'w', encoding='utf-8') as f:
        f.write(test_schueler)

    # Import after creating schueler.py
    from framework.spielfeld import Spielfeld

    class DummyFramework:
        def __init__(self):
            self.weiblich = False
            self._aktion_blockiert = False
            
        def taste_registrieren(self, key, callback):
            pass

    # Load level35
    fw = DummyFramework()
    level35_path = os.path.join(root_dir, 'level', 'level35.json')
    sp = Spielfeld(level35_path, fw, feldgroesse=32)

    if sp.held is None:
        print("✗ Held is None")
        sys.exit(1)

    # Check student instance position
    student = sp.held._student
    print(f"✓ Student set position to: ({student.x}, {student.y})")

    # Check MetaHeld uses student position
    print(f"✓ MetaHeld renders at: ({sp.held.x}, {sp.held.y})")

    # Check level expectation
    expected_x = getattr(sp.held, '_level_expected_x', None)
    expected_y = getattr(sp.held, '_level_expected_y', None)
    print(f"✓ Level expects position: ({expected_x}, {expected_y})")

    # Verify MetaHeld uses student's position, not level's
    if sp.held.x == 0 and sp.held.y == 0:
        print("✓ MetaHeld correctly uses student's position (0,0), not level's (1,1)")
    else:
        print(f"✗ MetaHeld at ({sp.held.x}, {sp.held.y}), expected student's (0,0)")
        sys.exit(1)

    # Check victory fails due to wrong position
    victory = sp.check_victory()
    if not victory:
        print("✓ Victory check fails (position doesn't match level expectation)")
    else:
        print("✗ Victory should fail when position is wrong")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("Test 2: Student uses level's position - victory should succeed")
    print("=" * 70)

    # Create schueler.py with correct position
    test_schueler_correct = """
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x  # Use level's position
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Test Held"
        self.typ = "Held"
        self.level = None
    
    def setze_level(self, level):
        self.level = level
"""

    with open(schueler_path, 'w', encoding='utf-8') as f:
        f.write(test_schueler_correct)

    # Reload modules
    import importlib
    if 'schueler' in sys.modules:
        del sys.modules['schueler']

    # Create new Spielfeld
    sp2 = Spielfeld(level35_path, fw, feldgroesse=32)
    student2 = sp2.held._student

    print(f"✓ Student set position to: ({student2.x}, {student2.y})")
    print(f"✓ MetaHeld renders at: ({sp2.held.x}, {sp2.held.y})")

    # Check victory succeeds
    victory2 = sp2.check_victory()
    if victory2:
        print("✓ Victory check succeeds (position matches level expectation)")
    else:
        print("✗ Victory should succeed when position is correct")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✓✓✓ ALL POSITION TESTS PASSED ✓✓✓")
    print("=" * 70)

finally:
    # Restore schueler.py
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, schueler_path)
        os.remove(backup_path)
