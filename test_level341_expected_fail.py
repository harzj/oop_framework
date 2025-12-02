"""
Test Level 341 with missing object (should fail).
Tests that rebuild mode correctly detects when a required object is missing.
"""
import sys
import os

# Ensure the framework can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_level341_expected_fail():
    """Test Level 341 with missing object - should NOT achieve victory"""
    print("Testing Level 341 with missing object (expected to fail)...")
    
    # Import framework
    from framework.grundlage import Framework
    
    # Create framework instance and load Level 341 with weiblich=True
    framework = Framework(levelnummer=341, auto_erzeuge_objekte=False, w=True)
    
    # Get spielfeld
    spielfeld = framework.spielfeld
    
    # Check that level loaded successfully
    assert spielfeld is not None, "Spielfeld should exist"
    assert spielfeld.rebuild_mode is True, "Level 341 should be in rebuild mode"
    
    # Import classes after level is loaded
    from framework.hindernis import Hindernis
    from framework.monster import Monster
    from framework.herz import Herz
    from framework.schluessel import Schluessel
    from framework.tuer import Tuer
    from framework.held import Held
    from framework.knappe import Knappe
    
    # Add objects BUT SKIP ONE REQUIRED OBJECT (e.g., skip the Monster at 2,1)
    print("Adding objects but skipping Monster at (2,1)...")
    
    spielfeld.objekt_hinzufuegen(Hindernis("Busch", 2, 0))
    spielfeld.objekt_hinzufuegen(Hindernis("Berg", 0, 1))
    spielfeld.objekt_hinzufuegen(Hindernis("Baum", 0, 2))
    spielfeld.objekt_hinzufuegen(Hindernis("Baum", 4, 3))
    # SKIP: spielfeld.objekt_hinzufuegen(Monster(2, 1, "down"))  # <-- Missing!
    spielfeld.objekt_hinzufuegen(Herz(2, 2))
    spielfeld.objekt_hinzufuegen(Herz(3, 3))
    spielfeld.objekt_hinzufuegen(Herz(4, 4))
    s = Schluessel(0, 4)
    spielfeld.objekt_hinzufuegen(s)
    s.set_farbe("blue")
    spielfeld.objekt_hinzufuegen(Tuer(3, 4, "blue"))
    spielfeld.objekt_hinzufuegen(Held(1, 2, "down", False))
    spielfeld.objekt_hinzufuegen(Knappe(3, 2, "down"))
    
    # Check victory condition
    victory = spielfeld.check_victory()
    
    print(f"Victory check result: {victory}")
    
    # Verify that objects were added (but one is missing)
    objects_count = len(spielfeld._objekte)
    print(f"Total objects added: {objects_count}")
    
    # Expected: 11 objects (one Monster missing)
    assert objects_count == 11, f"Expected 11 objects (one missing), got {objects_count}"
    
    # Check that victory is NOT achieved (missing object)
    assert victory is False, "Level 341 should NOT be completed with missing Monster"
    
    print("✓ Level 341 expected fail test passed!")
    print("✓ Rebuild mode correctly detects missing object!")
    return True

if __name__ == "__main__":
    try:
        test_level341_expected_fail()
        print("\n=== TEST SUCCESS (Expected Fail Scenario) ===")
    except AssertionError as e:
        print(f"\n=== TEST FAILED ===")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n=== TEST ERROR ===")
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
