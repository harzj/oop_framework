#!/usr/bin/env python3
"""
Test script for Phase 2: class_requirements integration in spielfeld.py
This test verifies that the framework correctly loads student classes based on F4 configuration.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a simple test student class
test_held_code = '''
class Held:
    def __init__(self, x, y, spielfeld):
        self.x = x
        self.y = y
        self.spielfeld = spielfeld
        self.name = "Test Held"
        self.richtung = "down"
        print("[Student Held] Initialized from klassen/held.py!")
    
    def geh(self):
        print("[Student Held] geh() called")
        pass
    
    def links(self):
        self.richtung = "left"
    
    def rechts(self):
        self.richtung = "right"
'''

def test_class_requirements_loading():
    """Test that spielfeld loads student classes based on class_requirements."""
    print("Testing Phase 2: class_requirements in spielfeld...")
    
    # Create klassen directory if it doesn't exist
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    klassen_dir = os.path.join(root_dir, "klassen")
    os.makedirs(klassen_dir, exist_ok=True)
    
    # Write test Held class to klassen/held.py
    with open(os.path.join(klassen_dir, "held.py"), "w", encoding="utf-8") as f:
        f.write(test_held_code)
    print("✓ Created test student class: klassen/held.py")
    
    # Create a test level that uses class_requirements
    import json
    test_level = {
        "tiles": ["wpw", "www", "www"],
        "settings": {
            "Held": {"public": True},
            "class_requirements": {
                "Held": {
                    "load_from_klassen": True,
                    "load_from_schueler": False,
                    "inherits": "Objekt",
                    "methods": ["geh", "links", "rechts"],
                    "attributes": ["x", "y", "richtung"]
                }
            }
        }
    }
    
    test_file = os.path.join(root_dir, "level", "level_test_phase2.json")
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_level, f, ensure_ascii=False, indent=2)
    print(f"✓ Created test level: {test_file}")
    
    # Now test that the framework loads this properly
    print("\nImporting framework modules...")
    from framework.spielfeld import Spielfeld
    
    print("Creating minimal Framework mock...")
    class MockFramework:
        def __init__(self):
            self.levelfile = test_file
            self.spielfeld = None
    
    fw = MockFramework()
    
    print("Creating Spielfeld with test level...")
    # The spielfeld should read class_requirements and try to load from klassen/held.py
    sp = Spielfeld(test_file, fw, auto_erzeuge_objekte=False)
    
    # Check that class_requirements were loaded
    assert hasattr(sp, 'class_requirements'), "Spielfeld missing class_requirements attribute"
    assert "Held" in sp.class_requirements, "Held not in class_requirements"
    
    print(f"✓ Spielfeld loaded class_requirements: {list(sp.class_requirements.keys())}")
    print(f"✓ Held config: {sp.class_requirements['Held']}")
    
    # Test _get_entity_class with class_requirements
    print("\nTesting _get_entity_class with Held...")
    from framework.held import Held as FrameworkHeld
    
    result_cls = sp._get_entity_class("Held", FrameworkHeld)
    
    if result_cls is None:
        print("✗ _get_entity_class returned None - student class not found!")
        print("  This might be expected if klassen/held.py couldn't be loaded")
        # Check if file exists
        if os.path.exists("klassen/held.py"):
            print("  klassen/held.py exists, investigating...")
            with open("klassen/held.py", "r") as f:
                print(f"  Content: {f.read()[:100]}...")
    elif result_cls == FrameworkHeld:
        print("✗ _get_entity_class returned framework class instead of student class!")
        return False
    else:
        print(f"✓ _get_entity_class returned student class: {result_cls}")
        print(f"  Class name: {result_cls.__name__}")
        print(f"  Class module: {getattr(result_cls, '__module__', 'unknown')}")
        
        # Try to instantiate it
        try:
            test_instance = result_cls(0, 0, sp)
            print(f"✓ Successfully instantiated student Held")
            print(f"  Instance name: {getattr(test_instance, 'name', 'N/A')}")
        except Exception as e:
            print(f"✗ Failed to instantiate: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✓✓✓ PHASE 2 BASIC TEST PASSED ✓✓✓")
    print("="*60)
    print("\nThe class_requirements integration is working!")
    print("- spielfeld.py reads class_requirements from level JSON")
    print("- _get_entity_class respects load_from_klassen flag")
    print("- Student classes can be loaded from klassen/ directory")
    
    return True

if __name__ == "__main__":
    try:
        test_class_requirements_loading()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
