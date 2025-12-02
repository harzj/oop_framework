"""
Test dass bei classes_present: true keine Framework-Klassen gerendert werden,
wenn die entsprechenden Student-Klassen fehlen.
"""

import pygame
from framework.spielfeld import Spielfeld

pygame.init()

def test_level(level_num, expected_hindernis=None, expected_knappe=None, expected_zettel=None):
    """
    Test level rendering.
    expected_* can be:
        None - don't check
        True - should be present
        False - should NOT be present
    """
    print(f"\n{'='*70}")
    print(f"Testing Level {level_num}")
    print('='*70)
    
    sp = Spielfeld(f'level/level{level_num}.json', None, 80)
    
    # Count Hindernisse
    if expected_hindernis is not None:
        hindernisse = [o for o in sp.objekte if hasattr(o, 'typ') and o.typ in ['Baum', 'Berg', 'Busch']]
        has_hindernis = len(hindernisse) > 0
        
        if expected_hindernis:
            if has_hindernis:
                print(f"✓ Hindernis present: {len(hindernisse)} objects")
            else:
                print(f"✗ FAIL: Expected Hindernis but none found")
                return False
        else:
            if not has_hindernis:
                print(f"✓ No Hindernis (as expected)")
            else:
                print(f"✗ FAIL: Unexpected Hindernis: {len(hindernisse)} objects")
                return False
    
    # Check Knappe
    if expected_knappe is not None:
        has_knappe = sp.knappe is not None
        
        if expected_knappe:
            if has_knappe:
                print(f"✓ Knappe present: {sp.knappe}")
            else:
                print(f"✗ FAIL: Expected Knappe but none found")
                return False
        else:
            if not has_knappe:
                print(f"✓ No Knappe (as expected)")
            else:
                print(f"✗ FAIL: Unexpected Knappe: {sp.knappe}")
                return False
    
    # Check Zettel
    if expected_zettel is not None:
        zettel = [o for o in sp.objekte if hasattr(o, 'typ') and o.typ in ['Zettel', 'Code']]
        has_zettel = len(zettel) > 0
        
        if expected_zettel:
            if has_zettel:
                print(f"✓ Zettel/Code present: {len(zettel)} objects")
            else:
                print(f"✗ FAIL: Expected Zettel but none found")
                return False
        else:
            if not has_zettel:
                print(f"✓ No Zettel/Code (as expected)")
            else:
                print(f"✗ FAIL: Unexpected Zettel/Code: {len(zettel)} objects")
                return False
    
    print(f"✓ Level {level_num} PASSED")
    return True

# Run tests
tests = [
    # Level 45: classes_present=true, NO Hindernis requirements, NO Knappe requirements
    # → Should NOT render Hindernis or Knappe
    (45, False, False, True),  # Zettel expected (has requirements)
    
    # Level 46: classes_present=true, Knappe requirements exist
    # → Should render Knappe (knappe.py exists)
    (46, False, True, None),  # No Hindernis requirements
    
    # Level 48: classes_present=true, Hindernis requirements with inheritance
    # → Should render Hindernis (hindernis.py exists and inherits from Spielobjekt)
    (48, True, False, None),  # Knappe missing
    
    # Level 49: classes_present=true, Zettel requirements with inheritance
    # → Should render Zettel (zettel_49.py exists and inherits from Spielobjekt)
    (49, False, False, True),  # No Hindernis requirements
]

passed = 0
failed = 0

for level, exp_hind, exp_knappe, exp_zettel in tests:
    if test_level(level, exp_hind, exp_knappe, exp_zettel):
        passed += 1
    else:
        failed += 1

print(f"\n{'='*70}")
print(f"Summary")
print('='*70)
print(f"Tests passed: {passed}/{passed + failed}")

if failed == 0:
    print("\n✓ ALL TESTS PASSED")
else:
    print(f"\n✗ {failed} TESTS FAILED")

pygame.quit()
