#!/usr/bin/env python3
"""
Test script for F4 class requirements feature in leveleditor.py
This script tests that class_requirements are properly saved and loaded.
"""
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_class_requirements_persistence():
    """Test that class requirements can be saved and loaded from JSON."""
    print("Testing class_requirements persistence...")
    
    # Create a test level with class requirements (updated structure)
    test_level = {
        "tiles": ["wpw", "www", "www"],
        "settings": {
            "Held": {"public": True},
            "class_requirements": {
                "Held": {
                    "load_from_schueler": True,
                    "load_from_klassen": False,
                    "inherits": "Charakter",
                    "methods": ["geh", "links", "rechts", "custom_method"],
                    "attributes": ["x", "y", "gold", "knappe"]
                },
                "Monster": {
                    "inherits": "Objekt",
                    "methods": ["geh", "angriff"],
                    "attributes": ["x", "y"]
                },
                "Zettel": {
                    "inherits": "Gegenstand",
                    "methods": ["set_position", "get_x"],
                    "attributes": ["x", "y", "text"]
                }
            }
        }
    }
    
    # Write test level
    test_file = os.path.join(root_dir, "level", "level_test_f4_requirements.json")
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_level, f, ensure_ascii=False, indent=2)
    print(f"✓ Created test level: {test_file}")
    
    # Read it back
    with open(test_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    
    # Verify class_requirements were preserved
    assert "class_requirements" in loaded["settings"], "class_requirements not in settings"
    reqs = loaded["settings"]["class_requirements"]
    
    assert "Held" in reqs, "Held not in class_requirements"
    assert reqs["Held"]["load_from_schueler"] == True, "Held load_from_schueler not True"
    assert reqs["Held"]["load_from_klassen"] == False, "Held load_from_klassen not False"
    assert reqs["Held"]["inherits"] == "Charakter", "Held inherits not Charakter"
    assert "geh" in reqs["Held"]["methods"], "geh not in Held methods"
    assert "custom_method" in reqs["Held"]["methods"], "custom_method not in Held methods"
    assert "x" in reqs["Held"]["attributes"], "x not in Held attributes"
    assert "gold" in reqs["Held"]["attributes"], "gold not in Held attributes (extra attribute)"
    assert "knappe" in reqs["Held"]["attributes"], "knappe not in Held attributes (extra attribute)"
    
    assert "Monster" in reqs, "Monster not in class_requirements"
    assert reqs["Monster"]["inherits"] == "Objekt", "Monster inherits not Objekt"
    
    assert "Zettel" in reqs, "Zettel not in class_requirements (Code renamed)"
    assert reqs["Zettel"]["inherits"] == "Gegenstand", "Zettel inherits not Gegenstand"
    
    print("✓ class_requirements correctly persisted in JSON")
    print(f"✓ Held requirements: {reqs['Held']}")
    print(f"✓ Monster requirements: {reqs['Monster']}")
    print(f"✓ Zettel requirements: {reqs['Zettel']}")
    
    # Now test that leveleditor can load this
    print("\nImporting leveleditor module...")
    import leveleditor
    
    # Create an editor instance and load the test level
    print("Creating LevelEditor instance...")
    # We can't actually run the GUI, but we can test the from_json method
    editor = leveleditor.LevelEditor()
    
    print("Loading test level via from_json...")
    editor.from_json(test_level)
    
    # Verify editor loaded the class_requirements
    assert hasattr(editor, 'class_requirements'), "Editor missing class_requirements attribute"
    assert "Held" in editor.class_requirements, "Held not in editor.class_requirements"
    assert editor.class_requirements["Held"]["load_from_schueler"] == True, "Editor: Held load_from_schueler not True"
    assert "gold" in editor.class_requirements["Held"]["attributes"], "Editor: gold not in Held attributes"
    
    print("✓ LevelEditor.from_json() correctly loaded class_requirements")
    print(f"✓ Editor has {len(editor.class_requirements)} configured classes")
    
    # Test to_json export
    print("\nTesting to_json export...")
    exported = editor.to_json()
    
    assert "settings" in exported, "No settings in exported JSON"
    assert "class_requirements" in exported["settings"], "No class_requirements in exported settings"
    exported_reqs = exported["settings"]["class_requirements"]
    
    assert "Held" in exported_reqs, "Held not in exported class_requirements"
    assert exported_reqs["Held"]["load_from_schueler"] == True, "Exported Held load_from_schueler not True"
    assert "gold" in exported_reqs["Held"]["attributes"], "Exported Held missing gold attribute"
    
    print("✓ LevelEditor.to_json() correctly exported class_requirements")
    print(f"✓ Exported requirements: {list(exported_reqs.keys())}")
    
    print("\n" + "="*60)
    print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("="*60)
    print("\nThe F4 class requirements feature is working correctly!")
    print("- Data structure is correct")
    print("- JSON persistence works")
    print("- LevelEditor can load and save class_requirements")
    
    return True

if __name__ == "__main__":
    try:
        test_class_requirements_persistence()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
