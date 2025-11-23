"""Test level35.json with student Held class validation"""
import sys
import os
import pygame

# Initialize pygame before importing framework
pygame.init()

# Add project root to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from framework.spielfeld import Spielfeld

class DummyFramework:
    def __init__(self):
        self.weiblich = False
        self._aktion_blockiert = False
        
    def taste_registrieren(self, key, callback):
        pass

def test_level35_with_student_held():
    """Test that level35 loads student Held and validates attributes."""
    print("=" * 60)
    print("Testing level35.json with student Held validation")
    print("=" * 60)
    
    # Create framework mock
    fw = DummyFramework()
    
    # Load level35 which requires student Held from schueler.py
    try:
        level35_path = os.path.join(root_dir, 'level', 'level35.json')
        sp = Spielfeld(level35_path, fw, feldgroesse=32)
        print("✓ Spielfeld loaded")
    except Exception as e:
        print(f"✗ Failed to load Spielfeld: {e}")
        return False
    
    # Check that Held was created
    if sp.held is None:
        print("✗ Held is None (should have been created from schueler.py)")
        return False
    print(f"✓ Held created: {type(sp.held).__name__}")
    
    # Check if it's a MetaHeld wrapping student instance
    from framework.held import MetaHeld
    if not isinstance(sp.held, MetaHeld):
        print(f"✗ Expected MetaHeld, got {type(sp.held)}")
        return False
    print("✓ Held is MetaHeld wrapper")
    
    # Get student instance
    try:
        student = sp.held._student
        print(f"✓ Student instance accessible: {type(student)}")
    except Exception as e:
        print(f"✗ Cannot access _student: {e}")
        return False
    
    # Check required attributes
    required = ['x', 'y', 'richtung', 'weiblich', 'name', 'level', 'typ']
    print("\nChecking required attributes:")
    for attr in required:
        if hasattr(student, attr):
            val = getattr(student, attr)
            # Don't print full Level object
            if attr == 'level' and val is not None:
                print(f"  ✓ {attr}: <Level>")
            else:
                print(f"  ✓ {attr}: {val}")
        else:
            print(f"  ✗ {attr}: MISSING")
            return False
    
    # Check values match level expectations
    print("\nChecking values match level JSON:")
    expected_x = getattr(sp.held, '_level_expected_x', None)
    expected_y = getattr(sp.held, '_level_expected_y', None)
    expected_richtung = getattr(sp.held, '_level_expected_richtung', None)
    
    print(f"  Expected position: ({expected_x}, {expected_y}), direction: {expected_richtung}")
    print(f"  Actual position: ({student.x}, {student.y}), direction: {student.richtung}")
    
    if student.x == expected_x and student.y == expected_y and student.richtung == expected_richtung:
        print("  ✓ Values match!")
    else:
        print("  ✗ Values don't match (victory will fail)")
    
    # Check victory condition
    print("\nChecking victory condition:")
    victory_result = sp.check_victory()
    if victory_result:
        print("  ✓ Victory condition satisfied!")
    else:
        print("  ✗ Victory condition NOT satisfied")
        return False
    
    # Check attribute display
    print("\nChecking attribute display in inspector:")
    attrs = sp.held.attribute_als_text()
    for key, val in attrs.items():
        print(f"  {key}: {val}")
    
    print("\n" + "=" * 60)
    print("✓✓✓ LEVEL35 TEST PASSED ✓✓✓")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_level35_with_student_held()
    if not success:
        sys.exit(1)
