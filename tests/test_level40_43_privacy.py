"""
Test privacy behavior for Levels 40-43.

Tests:
1. held.name returns student class name (from student implementation)
2. Private attributes raise AttributeError
3. Public attributes work correctly
4. Getter methods work as fallback
"""

import sys
import os

# Initialize pygame before importing framework
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()

from framework.grundlage import level
from framework.grundlage import *

def test_level40():
    """Level 40: x, y are private, name is public"""
    print("\n=== Testing Level 40 ===")
    
    level.lade(40, weiblich=False)
    held = framework.spielfeld.held
    
    print(f"Held type: {type(held).__name__}")
    print(f"Held has _student: {hasattr(held, '_student')}")
    
    # Test 1: name should return student's name, not "Namenloser Held"
    try:
        name = held.name
        print(f"✓ held.name = '{name}'")
        if name == "Namenloser Held":
            print(f"  ⚠️ WARNING: Expected student name, got framework default!")
        else:
            print(f"  ✓ Correct: Student name returned")
    except AttributeError as e:
        print(f"✗ held.name raised AttributeError: {e}")
    
    # Test 2: x should raise AttributeError (private)
    try:
        x = held.x
        print(f"✗ held.x = {x} (should raise AttributeError!)")
    except AttributeError as e:
        print(f"✓ held.x raised AttributeError: {e}")
    
    # Test 3: y should raise AttributeError (private)
    try:
        y = held.y
        print(f"✗ held.y = {y} (should raise AttributeError!)")
    except AttributeError as e:
        print(f"✓ held.y raised AttributeError: {e}")
    
    # Test 4: richtung should work (public)
    try:
        richtung = held.richtung
        print(f"✓ held.richtung = '{richtung}'")
    except AttributeError as e:
        print(f"✗ held.richtung raised AttributeError: {e}")
    
    pygame.quit()

def test_level41():
    """Level 41: x, y, name are private, getters added"""
    print("\n=== Testing Level 41 ===")
    
    level.lade(41, weiblich=False)
    held = framework.spielfeld.held
    
    # Test 1: name should raise AttributeError (private)
    try:
        name = held.name
        print(f"✗ held.name = '{name}' (should raise AttributeError!)")
    except AttributeError as e:
        print(f"✓ held.name raised AttributeError: {e}")
    
    # Test 2: get_name() should work
    try:
        name = held.get_name()
        print(f"✓ held.get_name() = '{name}'")
    except Exception as e:
        print(f"✗ held.get_name() failed: {e}")
    
    # Test 3: x should raise AttributeError (private)
    try:
        x = held.x
        print(f"✗ held.x = {x} (should raise AttributeError!)")
    except AttributeError as e:
        print(f"✓ held.x raised AttributeError: {e}")
    
    # Test 4: get_x() should work
    try:
        x = held.get_x()
        print(f"✓ held.get_x() = {x}")
    except Exception as e:
        print(f"✗ held.get_x() failed: {e}")
    
    pygame.quit()

def test_level42():
    """Level 42: More getters added"""
    print("\n=== Testing Level 42 ===")
    
    level.lade(42, weiblich=False)
    held = framework.spielfeld.held
    
    # Test 1: get_y() should work
    try:
        y = held.get_y()
        print(f"✓ held.get_y() = {y}")
    except Exception as e:
        print(f"✗ held.get_y() failed: {e}")
    
    # Test 2: get_richtung() should work
    try:
        richtung = held.get_richtung()
        print(f"✓ held.get_richtung() = '{richtung}'")
    except Exception as e:
        print(f"✗ held.get_richtung() failed: {e}")
    
    pygame.quit()

def test_level43():
    """Level 43: All getters present"""
    print("\n=== Testing Level 43 ===")
    
    level.lade(43, weiblich=False)
    held = framework.spielfeld.held
    
    # Test: All getters should work
    try:
        name = held.get_name()
        x = held.get_x()
        y = held.get_y()
        richtung = held.get_richtung()
        print(f"✓ All getters work:")
        print(f"  name='{name}', x={x}, y={y}, richtung='{richtung}'")
    except Exception as e:
        print(f"✗ Getter failed: {e}")
    
    pygame.quit()

if __name__ == '__main__':
    test_level40()
    test_level41()
    test_level42()
    test_level43()
    
    print("\n=== Summary ===")
    print("If all tests passed:")
    print("✓ Student class attributes override framework defaults")
    print("✓ Private attributes correctly blocked")
    print("✓ Getter methods work as fallback")
