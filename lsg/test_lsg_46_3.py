"""
Level 46 Test 3: Kompletter Level-Test
Prüft ob Level 46 mit der Knappe Klasse abgeschlossen werden kann
"""
import os
import sys

def test_level_46_complete():
    """Test dass Level 46 abgeschlossen werden kann"""
    print("Test 3: Level 46 Komplett-Test")
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    # Set test mode
    os.environ['OOP_TEST'] = '1'
    
    try:
        # Clear modules
        for mod_name in list(sys.modules.keys()):
            if 'framework' in mod_name or 'klassen' in mod_name:
                del sys.modules[mod_name]
        
        from framework.grundlage import level
        level.lade(46)
        spielfeld = level.framework.spielfeld
    except Exception as e:
        print(f"  ✗ FEHLER: Kann Level 46 nicht laden: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"  ✓ Level 46 erfolgreich geladen")
    
    # Prüfe dass Knappe gespawnt wurde
    knappe_objects = [obj for obj in spielfeld.objekte if obj.__class__.__name__ == 'Knappe']
    if not knappe_objects:
        print(f"  ✗ FEHLER: Kein Knappe-Objekt gefunden")
        return False
    
    knappe = knappe_objects[0]
    print(f"  ✓ Knappe-Objekt gefunden")
    
    # Prüfe Position
    try:
        x = knappe.get_x()
        y = knappe.get_y()
        print(f"  ✓ Knappe Position: ({x}, {y})")
    except Exception as e:
        print(f"  ✗ FEHLER: Kann Position nicht abrufen: {e}")
        return False
    
    # Prüfe typ für Rendering
    try:
        typ = getattr(knappe, 'typ', None)
        if typ != 'Knappe':
            print(f"  ✗ FEHLER: typ sollte 'Knappe' sein, ist aber: {typ}")
            return False
        print(f"  ✓ typ Attribut korrekt: '{typ}'")
    except Exception as e:
        print(f"  ✗ FEHLER: Kann typ nicht abrufen: {e}")
        return False
    
    # Prüfe dass _student_has_class funktioniert
    try:
        has_knappe = spielfeld._student_has_class('Knappe')
        if not has_knappe:
            print(f"  ✗ FEHLER: _student_has_class('Knappe') gibt False zurück")
            return False
        print(f"  ✓ _student_has_class('Knappe'): True")
    except Exception as e:
        print(f"  ✗ FEHLER: _student_has_class fehlgeschlagen: {e}")
        return False
    
    # Prüfe dass Held auch existiert
    if not spielfeld.held:
        print(f"  ✗ FEHLER: Kein Held gefunden")
        return False
    print(f"  ✓ Held gefunden")
    
    has_held = spielfeld._student_has_class('Held')
    if not has_held:
        print(f"  ✗ FEHLER: _student_has_class('Held') gibt False zurück")
        return False
    print(f"  ✓ _student_has_class('Held'): True")
    
    # Prüfe Victory
    try:
        victory = spielfeld.check_victory()
        if not victory:
            print(f"  ✗ FEHLER: Victory check fehlgeschlagen")
            return False
        print(f"  ✓ Victory check: True")
    except Exception as e:
        print(f"  ✗ FEHLER: Victory check Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Bewegung
    try:
        old_x = knappe.get_x()
        old_y = knappe.get_y()
        old_richtung = knappe.get_richtung()
        
        # Knappe schaut nach unten, rechts drehen = nach links schauen
        knappe.rechts()
        new_richtung = knappe.get_richtung()
        
        # Gehe in die neue Richtung
        knappe.geh()
        
        new_x = knappe.get_x()
        new_y = knappe.get_y()
        
        # Prüfe ob sich Position geändert hat
        if new_x != old_x or new_y != old_y:
            print(f"  ✓ Bewegung funktioniert: ({old_x}, {old_y}) -> ({new_x}, {new_y})")
        else:
            print(f"  ✗ FEHLER: Keine Bewegung. Position unverändert: ({old_x}, {old_y})")
            return False
    except Exception as e:
        print(f"  ✗ FEHLER: Bewegung fehlgeschlagen: {e}")
        return False
    
    return True

if __name__ == '__main__':
    try:
        result = test_level_46_complete()
        if result:
            print("\n✓ Test 3 bestanden")
            print("\n" + "="*60)
            print("ALLE TESTS BESTANDEN - Level 46 erfolgreich gelöst!")
            print("="*60)
            sys.exit(0)
        else:
            print("\n✗ Test 3 fehlgeschlagen")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
