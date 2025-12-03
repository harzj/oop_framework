"""Direkter Test der _check_privacy_requirements Funktion"""
import sys
sys.path.insert(0, 'klassen')

# Test 1: Korrekte Implementierung (private Attribute)
print("=== Test 1: Private Attribute ===")
code_private = '''
class Spielobjekt:
    def __init__(self, x, y):
        self.__typ = "Spielobjekt"
        self.__x = x
        self.__y = y

    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def ist_passierbar(self):
        return False
'''

exec(code_private)
obj1 = Spielobjekt(5, 10)
print(f"Klasse: {obj1.__class__.__name__}")
print(f"Hat __Spielobjekt__x: {hasattr(obj1, '_Spielobjekt__x')}")
print(f"Hat x (public): {hasattr(obj1, 'x') and not 'x'.startswith('_')}")
print(f"Wert von _Spielobjekt__x: {getattr(obj1, '_Spielobjekt__x')}")

# Test 2: Falsche Implementierung (öffentliche Attribute)
print("\n=== Test 2: Öffentliche Attribute ===")
code_public = '''
class Spielobjekt2:
    def __init__(self, x, y):
        self.typ = "Spielobjekt"
        self.x = x
        self.y = y

    def get_typ(self):
        return self.typ
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def ist_passierbar(self):
        return False
'''

exec(code_public)
obj2 = Spielobjekt2(5, 10)
print(f"Klasse: {obj2.__class__.__name__}")
print(f"Hat __Spielobjekt2__x: {hasattr(obj2, '_Spielobjekt2__x')}")
print(f"Hat x (public): {hasattr(obj2, 'x') and not 'x'.startswith('_')}")
print(f"Wert von x: {getattr(obj2, 'x')}")

# Test check_privacy_requirements logic
print("\n=== Test privacy check logic ===")
req = {
    'attributes_private': {
        'x': True,
        'y': True,
        'typ': True
    },
    'methods': ['get_x', 'get_y', 'get_typ', 'ist_passierbar']
}

def check_privacy(obj, req):
    """Simplified version of _check_privacy_requirements"""
    private_attrs_req = req.get('attributes_private', {})
    student_class = obj.__class__
    
    for attr_name, required in private_attrs_req.items():
        if not required:
            continue
        
        # Check if attribute is actually private (starts with __)
        private_attr_name = f"_{student_class.__name__}__{attr_name}"
        has_private_attr = hasattr(obj, private_attr_name)
        
        # Also check if there's a non-private attribute with the same name (would be wrong)
        has_public_attr = hasattr(obj, attr_name) and not attr_name.startswith('_')
        
        print(f"  Checking {attr_name}:")
        print(f"    Private name: {private_attr_name}")
        print(f"    Has private: {has_private_attr}")
        print(f"    Has public: {has_public_attr}")
        print(f"    Valid: {has_private_attr and not has_public_attr}")
        
        if not has_private_attr or has_public_attr:
            return False
    
    return True

print("Check obj1 (private attributes):")
result1 = check_privacy(obj1, req)
print(f"Result: {result1} (should be True)")

print("\nCheck obj2 (public attributes):")
result2 = check_privacy(obj2, req)
print(f"Result: {result2} (should be False)")
