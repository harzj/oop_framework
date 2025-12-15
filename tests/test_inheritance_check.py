"""Test für die verbesserte Vererbungsprüfung"""
import sys
import os

# Setup paths
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'klassen'))

# Import framework
from framework.spielfeld import Spielfeld

# Create a simple test level with Spielobjekt inheritance requirement
test_level = os.path.join(ROOT, 'level', 'level47.json')

print("Testing inheritance check with level47.json...")
print("=" * 60)

# Load level
try:
    from framework import framework
    f = framework.Framework(test_level)
    
    print("\nLoading level...")
    if hasattr(f, 'spielfeld'):
        spielfeld = f.spielfeld
        
        # Check if class validation passed
        if hasattr(spielfeld, '_class_validation_passed'):
            if spielfeld._class_validation_passed:
                print("✓ Class validation PASSED")
            else:
                print("✗ Class validation FAILED")
        else:
            print("? No class validation flag found")
    else:
        print("✗ No spielfeld found")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed")
