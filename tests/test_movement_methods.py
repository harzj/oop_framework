"""Test that movement only works when student implements the methods"""
import sys
import os
import shutil

# Backup schueler.py
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
schueler_path = os.path.join(root_dir, 'schueler.py')
backup_path = os.path.join(root_dir, 'schueler_backup_test.py')
if os.path.exists(schueler_path):
    shutil.copy2(schueler_path, backup_path)

try:
    # Test student class WITHOUT movement methods
    test_no_methods = """
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Held ohne Methoden"
        self.typ = "Held"
"""

    # Test student class WITH movement methods
    test_with_methods = """
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Held mit Methoden"
        self.typ = "Held"
    
    def geh(self):
        print("geh() aufgerufen")
        self.y -= 1
    
    def links(self):
        print("links() aufgerufen")
        self.x -= 1
    
    def rechts(self):
        print("rechts() aufgerufen")
        self.x += 1
    
    def zurueck(self):
        print("zurueck() aufgerufen")
        self.y += 1
"""

    print("=" * 70)
    print("Test 1: Student WITHOUT movement methods - keys should do nothing")
    print("=" * 70)

    with open(schueler_path, 'w', encoding='utf-8') as f:
        f.write(test_no_methods)

    import pygame
    pygame.init()

    sys.path.insert(0, root_dir)

    from framework.spielfeld import Spielfeld

    class DummyFramework:
        def __init__(self):
            self.weiblich = False
            self._aktion_blockiert = False
            self._key_handlers = {}
            
        def taste_registrieren(self, key, callback):
            self._key_handlers[key] = callback

    fw = DummyFramework()
    level35_path = os.path.join(root_dir, 'level', 'level35.json')
    sp = Spielfeld(level35_path, fw, feldgroesse=32)

    if sp.held:
        student = sp.held._student
        print(f"✓ Student: {student.name}")
        print(f"✓ Initial position: ({student.x}, {student.y})")
        
        # Check if methods exist
        has_geh = hasattr(student, 'geh')
        has_links = hasattr(student, 'links')
        print(f"✓ Has geh(): {has_geh}")
        print(f"✓ Has links(): {has_links}")
        
        # Simulate key press for UP (geh)
        if pygame.K_UP in fw._key_handlers:
            print("\nSimulating UP key press...")
            old_y = student.y
            fw._key_handlers[pygame.K_UP]()
            new_y = student.y
            if old_y == new_y:
                print(f"✓ Position unchanged ({old_y} -> {new_y}) - method not implemented")
            else:
                print(f"✗ Position changed ({old_y} -> {new_y}) - should not move!")
                sys.exit(1)
        
        # Simulate key press for LEFT (links)
        if pygame.K_LEFT in fw._key_handlers:
            print("\nSimulating LEFT key press...")
            old_x = student.x
            fw._key_handlers[pygame.K_LEFT]()
            new_x = student.x
            if old_x == new_x:
                print(f"✓ Position unchanged ({old_x} -> {new_x}) - method not implemented")
            else:
                print(f"✗ Position changed ({old_x} -> {new_x}) - should not move!")
                sys.exit(1)

    print("\n" + "=" * 70)
    print("Test 2: Student WITH movement methods - keys should work")
    print("=" * 70)

    with open(schueler_path, 'w', encoding='utf-8') as f:
        f.write(test_with_methods)

    # Reload modules
    if 'schueler' in sys.modules:
        del sys.modules['schueler']

    fw2 = DummyFramework()
    sp2 = Spielfeld(level35_path, fw2, feldgroesse=32)

    if sp2.held:
        student2 = sp2.held._student
        print(f"✓ Student: {student2.name}")
        print(f"✓ Initial position: ({student2.x}, {student2.y})")
        
        # Check if methods exist
        has_geh = hasattr(student2, 'geh')
        has_links = hasattr(student2, 'links')
        print(f"✓ Has geh(): {has_geh}")
        print(f"✓ Has links(): {has_links}")
        
        # Simulate key press for UP (geh)
        if pygame.K_UP in fw2._key_handlers:
            print("\nSimulating UP key press...")
            old_y = student2.y
            fw2._key_handlers[pygame.K_UP]()
            new_y = student2.y
            if old_y != new_y:
                print(f"✓ Position changed ({old_y} -> {new_y}) - method worked!")
            else:
                print(f"✗ Position unchanged ({old_y} -> {new_y}) - method should have moved!")
                sys.exit(1)
        
        # Simulate key press for LEFT (links)
        if pygame.K_LEFT in fw2._key_handlers:
            print("\nSimulating LEFT key press...")
            old_x = student2.x
            fw2._key_handlers[pygame.K_LEFT]()
            new_x = student2.x
            if old_x != new_x:
                print(f"✓ Position changed ({old_x} -> {new_x}) - method worked!")
            else:
                print(f"✗ Position unchanged ({old_x} -> {new_x}) - method should have moved!")
                sys.exit(1)

    print("\n" + "=" * 70)
    print("✓✓✓ ALL MOVEMENT METHOD TESTS PASSED ✓✓✓")
    print("=" * 70)

finally:
    # Restore schueler.py
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, schueler_path)
        os.remove(backup_path)
