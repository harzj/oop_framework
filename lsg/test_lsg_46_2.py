"""
Level 46 Test 2: Knappe Privacy
Prüft ob private Attribute korrekt implementiert sind
"""
import os
import sys

def test_knappe_privacy():
    """Test dass Knappe private Attribute korrekt hat"""
    print("Test 2: Knappe Privacy")
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    try:
        # Clear modules
        for mod_name in list(sys.modules.keys()):
            if 'klassen' in mod_name:
                del sys.modules[mod_name]
        
        from klassen.knappe import Knappe
    except ImportError as e:
        print(f"  ✗ FEHLER: Kann Knappe nicht importieren: {e}")
        return False
    
    # Erstelle Knappe Instanz
    try:
        knappe = Knappe(5, 3, "down")
    except Exception as e:
        print(f"  ✗ FEHLER: Kann Knappe nicht instanziieren: {e}")
        return False
    
    print(f"  ✓ Knappe erfolgreich erstellt")
    
    # Prüfe dass x, y, richtung PRIVAT sind
    private_attrs = ['x', 'y', 'richtung']
    for attr in private_attrs:
        # Darf NICHT direkt zugreifbar sein
        if hasattr(knappe, attr):
            print(f"  ✗ FEHLER: Attribut '{attr}' ist öffentlich, sollte aber privat sein!")
            return False
        
        # Muss Getter haben
        getter_name = f'get_{attr}'
        if not hasattr(knappe, getter_name):
            print(f"  ✗ FEHLER: Getter '{getter_name}' nicht gefunden!")
            return False
        
        # Getter muss funktionieren
        try:
            getter = getattr(knappe, getter_name)
            value = getter()
            print(f"  ✓ Attribut '{attr}' ist privat mit Getter '{getter_name}' (Wert: {value})")
        except Exception as e:
            print(f"  ✗ FEHLER: Getter '{getter_name}' funktioniert nicht: {e}")
            return False
    
    # Prüfe dass name und typ ÖFFENTLICH sind
    public_attrs = ['name', 'typ']
    for attr in public_attrs:
        if not hasattr(knappe, attr):
            print(f"  ✗ FEHLER: Öffentliches Attribut '{attr}' nicht gefunden!")
            return False
        
        try:
            value = getattr(knappe, attr)
            print(f"  ✓ Attribut '{attr}' ist öffentlich (Wert: {value})")
        except Exception as e:
            print(f"  ✗ FEHLER: Kann '{attr}' nicht lesen: {e}")
            return False
    
    # Prüfe typ Wert
    if knappe.typ != 'Knappe':
        print(f"  ✗ FEHLER: typ sollte 'Knappe' sein, ist aber: {knappe.typ}")
        return False
    
    print(f"  ✓ typ Attribut hat korrekten Wert: 'Knappe'")
    
    # Prüfe dass weiblich NICHT existiert
    if hasattr(knappe, 'weiblich') or hasattr(knappe, '_Knappe__weiblich') or hasattr(knappe, 'get_weiblich'):
        print(f"  ✗ FEHLER: 'weiblich' Attribut oder Getter sollte NICHT existieren!")
        return False
    
    print(f"  ✓ Kein 'weiblich' Attribut (korrekt)")
    
    return True

if __name__ == '__main__':
    try:
        result = test_knappe_privacy()
        if result:
            print("\n✓ Test 2 bestanden")
            sys.exit(0)
        else:
            print("\n✗ Test 2 fehlgeschlagen")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
