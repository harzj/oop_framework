"""
Level 46 Test 1: Knappe Klasse - Grundstruktur
Prüft ob die Knappe Klasse mit korrekter Signatur existiert
"""
import os
import sys
import ast

def test_knappe_class_structure():
    """Test dass Knappe Klasse existiert und korrekte Struktur hat"""
    print("Test 1: Knappe Klasse Grundstruktur")
    
    # Prüfe ob klassen/knappe.py existiert
    knappe_path = os.path.join('klassen', 'knappe.py')
    if not os.path.exists(knappe_path):
        print("  ✗ FEHLER: klassen/knappe.py nicht gefunden")
        return False
    
    # Parse die Datei
    with open(knappe_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  ✗ FEHLER: Syntax-Fehler in knappe.py: {e}")
        return False
    
    # Finde Knappe Klasse
    knappe_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'Knappe':
            knappe_class = node
            break
    
    if not knappe_class:
        print("  ✗ FEHLER: Knappe Klasse nicht gefunden")
        return False
    
    print("  ✓ Knappe Klasse gefunden")
    
    # Prüfe __init__ Signatur
    init_method = None
    for item in knappe_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
            init_method = item
            break
    
    if not init_method:
        print("  ✗ FEHLER: __init__ Methode nicht gefunden")
        return False
    
    # Prüfe Parameter: self, x, y, richtung (OHNE weiblich)
    args = init_method.args.args
    param_names = [arg.arg for arg in args]
    
    expected_params = ['self', 'x', 'y', 'richtung']
    if param_names != expected_params:
        print(f"  ✗ FEHLER: Falsche Parameter. Erwartet: {expected_params}, Gefunden: {param_names}")
        return False
    
    print(f"  ✓ __init__ Signatur korrekt: ({', '.join(param_names)})")
    
    # Prüfe erforderliche Methoden
    required_methods = ['get_x', 'get_y', 'get_richtung', 'get_typ', 'geh', 'links', 'rechts', 'set_richtung']
    found_methods = set()
    
    for item in knappe_class.body:
        if isinstance(item, ast.FunctionDef):
            found_methods.add(item.name)
    
    missing_methods = set(required_methods) - found_methods
    if missing_methods:
        print(f"  ✗ FEHLER: Fehlende Methoden: {missing_methods}")
        return False
    
    print(f"  ✓ Alle erforderlichen Methoden vorhanden")
    
    # Prüfe Attribute in __init__
    attributes_set = set()
    for stmt in ast.walk(init_method):
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                    attr_name = target.attr
                    # Remove private prefixes
                    if attr_name.startswith('_Knappe__'):
                        attr_name = attr_name[9:]
                    elif attr_name.startswith('__'):
                        attr_name = attr_name[2:]
                    attributes_set.add(attr_name)
    
    # Erwartete Attribute: x, y, richtung, name, typ
    expected_attrs = {'x', 'y', 'richtung', 'name', 'typ'}
    if not expected_attrs.issubset(attributes_set):
        missing = expected_attrs - attributes_set
        print(f"  ✗ FEHLER: Fehlende Attribute: {missing}")
        return False
    
    print(f"  ✓ Alle erforderlichen Attribute vorhanden")
    
    # Prüfe dass weiblich NICHT vorhanden ist
    if 'weiblich' in attributes_set:
        print(f"  ✗ FEHLER: Attribut 'weiblich' sollte NICHT vorhanden sein!")
        return False
    
    print(f"  ✓ Kein 'weiblich' Attribut (korrekt)")
    
    return True

if __name__ == '__main__':
    try:
        result = test_knappe_class_structure()
        if result:
            print("\n✓ Test 1 bestanden")
            sys.exit(0)
        else:
            print("\n✗ Test 1 fehlgeschlagen")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
