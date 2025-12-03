"""Check _required_spawn_classes"""
import sys
import shutil

# Kopiere Musterlösungen
shutil.copy('klassen/spielobjekt_50.py', 'klassen/spielobjekt.py')
shutil.copy('klassen/charakter_51.py', 'klassen/charakter.py')
shutil.copy('klassen/held_52.py', 'klassen/held.py')

from framework.grundlage import level
level.lade(52, weiblich=True)
from framework.grundlage import framework
spielfeld = framework.spielfeld

print("=== _required_spawn_classes ===")
required = getattr(spielfeld, '_required_spawn_classes', None)
print(f"_required_spawn_classes: {required}")

print("\n=== Tiles ===")
print(f"Level tiles: {spielfeld.level.tiles}")

print("\n=== iter_entity_spawns ===")
for typ, x, y, sichtbar in spielfeld.level.iter_entity_spawns():
    print(f"  {typ} at ({x},{y}) sichtbar={sichtbar}")

print("\n=== Check class requirements ===")
for cls_name in ['Held', 'Hindernis', 'Zettel']:
    req = spielfeld.class_requirements.get(cls_name, {})
    if req:
        print(f"{cls_name}:")
        has_load = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
        has_inherit = req.get('inherits') and req.get('inherits') != 'None'
        has_methods = bool(req.get('methods') or req.get('methods_private'))
        has_attrs = bool(req.get('attributes') or req.get('attributes_private'))
        
        requires_student = has_load or has_inherit or has_methods or has_attrs
        print(f"  requires_student: {requires_student}")
        print(f"    load_flags: {has_load}")
        print(f"    inheritance: {has_inherit}")
        print(f"    methods: {has_methods}")
        print(f"    attributes: {has_attrs}")
