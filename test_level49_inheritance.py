#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Level 49 Zettel inheritance requirement"""

import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(__file__))

def test_zettel_version(zettel_file, expected_pass):
    """Test a specific Zettel implementation"""
    print(f"\n{'='*70}")
    print(f"Testing: {zettel_file}")
    print(f"Expected: {'PASS' if expected_pass else 'FAIL'}")
    print('='*70)
    
    # Backup current zettel.py
    zettel_path = 'klassen/zettel.py'
    backup_path = 'klassen/zettel_backup_test49.py'
    
    if os.path.exists(zettel_path):
        shutil.copy(zettel_path, backup_path)
    
    # Copy test version to zettel.py
    source = f'klassen/{zettel_file}'
    if os.path.exists(source):
        shutil.copy(source, zettel_path)
    else:
        print(f"ERROR: {source} not found!")
        return False
    
    try:
        # Clear modules
        for mod_name in list(sys.modules.keys()):
            if 'framework' in mod_name or 'klassen' in mod_name:
                del sys.modules[mod_name]
        
        import pygame
        pygame.init()
        
        from framework.grundlage import level
        level.lade(49)
        spielfeld = level.framework.spielfeld
        
        # Check if Zettel class is detected
        has_zettel = spielfeld._student_has_class('Zettel')
        has_spielobjekt = spielfeld._student_has_class('Spielobjekt')
        victory = spielfeld.check_victory()
        
        print(f"_student_has_class('Spielobjekt'): {has_spielobjekt}")
        print(f"_student_has_class('Zettel'): {has_zettel}")
        print(f"check_victory(): {victory}")
        
        # Check class requirements
        zettel_req = spielfeld.class_requirements.get('Zettel', {})
        required_inheritance = zettel_req.get('inherits', 'None')
        print(f"Required inheritance: {required_inheritance}")
        
        # Verify actual inheritance
        if has_zettel:
            from klassen.zettel import Zettel
            if hasattr(Zettel, '__bases__'):
                bases = [b.__name__ for b in Zettel.__bases__]
                print(f"Zettel bases: {bases}")
        
        pygame.quit()
        
        # Check result
        if expected_pass:
            if victory:
                print("✓ PASS: Correctly accepted")
                return True
            else:
                print("✗ FAIL: Should have passed but was rejected")
                return False
        else:
            if not victory:
                print("✓ PASS: Correctly rejected")
                return True
            else:
                print("✗ FAIL: Should have failed but was accepted")
                return False
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore backup
        if os.path.exists(backup_path):
            shutil.copy(backup_path, zettel_path)
            os.remove(backup_path)

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Level 49 - Zettel Inheritance Test")
    print("="*70)
    
    results = []
    
    # Test zettel_45.py (no inheritance - should FAIL)
    results.append(test_zettel_version('zettel_45.py', expected_pass=False))
    
    # Test zettel_49.py (with inheritance - should PASS)
    results.append(test_zettel_version('zettel_49.py', expected_pass=True))
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        sys.exit(1)
