"""
Test Level 341 with correct solution (rebuild mode).
Tests that students can create all required objects using the new constructor signatures.
"""
import sys
import os

# Ensure the framework can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_level341_success():
    """Test Level 341 with the correct solution from schueler.py"""
    print("Testing Level 341 with correct solution...")
    
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
    
    # Add objects as students would (using new constructor signatures)
    spielfeld.objekt_hinzufuegen(Hindernis("Busch", 2, 0))
    spielfeld.objekt_hinzufuegen(Hindernis("Berg", 0, 1))
    spielfeld.objekt_hinzufuegen(Hindernis("Baum", 0, 2))
    spielfeld.objekt_hinzufuegen(Hindernis("Baum", 4, 3))
    spielfeld.objekt_hinzufuegen(Monster(2, 1, "down"))
    spielfeld.objekt_hinzufuegen(Herz(2, 2))
    spielfeld.objekt_hinzufuegen(Herz(3, 3))
    spielfeld.objekt_hinzufuegen(Herz(4, 4))
    s = Schluessel(0, 4)
    spielfeld.objekt_hinzufuegen(s)
    s.set_farbe("blue")
    spielfeld.objekt_hinzufuegen(Tuer(3, 4, "blue"))
    
    # Add Held and Knappe using new student-friendly signatures
    spielfeld.objekt_hinzufuegen(Held(1, 2, "down", False))
    spielfeld.objekt_hinzufuegen(Knappe(3, 2, "down"))
    
    # Check victory condition (rebuild mode checks if all template objects are present)
    victory = spielfeld.check_victory()
    
    print(f"Victory check result: {victory}")
    
    # Verify that all objects were added correctly
    objects_count = len(spielfeld._objekte)
    print(f"Total objects added: {objects_count}")
    
    # Expected: 3 Hindernis + 1 Monster + 3 Herz + 1 Schluessel + 1 Tuer + 1 Held + 1 Knappe + 1 Hindernis = 12
    assert objects_count == 12, f"Expected 12 objects, got {objects_count}"
    
    # Check that victory is achieved
    assert victory is True, "Level 341 should be completed with all objects present"
    
    print("✓ Level 341 test passed - all objects created successfully!")
    print("✓ Student-friendly constructor signatures work correctly!")
    return True

if __name__ == "__main__":
    try:
        test_level341_success()
        print("\n=== TEST SUCCESS ===")
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
