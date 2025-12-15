import json
import os

# Template für die Standard-Settings aus Level 200
standard_settings = {
    "Held": {"public": True},
    "Knappe": {"public": True},
    "Monster": {"public": True},
    "Herz": {"public": True},
    "Tuer": {"public": True},
    "Zettel": {"public": True},
    "Villager": {"public": True},
    "Hindernis": {"public": True},
    "Schluessel": {"public": True},
    "Bogenschuetze": {"public": True},
    "victory": {
        "rebuild_mode": False,
        "collect_hearts": True,
        "move_to": None,
        "classes_present": True
    },
    "initial_gold": 0,
    "quest_max_kosten": 0,
    "quest_mode": "items",
    "quest_items_needed": 1,
    "random_door": False,
    "random_keys": False,
    "use_student_module": False,
    "student_classes_in_subfolder": False
}

# Erstelle Level 201-234 basierend auf Level 1-34
for i in range(1, 35):
    source_file = f"level/level{i}.json"
    target_file = f"level/level{i+200}.json"
    
    # Lese Quell-Level
    with open(source_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)
    
    # Erstelle neue Level-Daten
    new_data = {"tiles": source_data["tiles"]}
    
    # Füge Settings hinzu
    if "settings" in source_data:
        # Merge existing settings with standard settings
        new_data["settings"] = {**standard_settings}
        
        # Überschreibe mit spezifischen Settings aus Quell-Level
        for key, value in source_data["settings"].items():
            if key == "victory":
                # Merge victory settings, aber behalte classes_present: true
                new_data["settings"]["victory"] = {**standard_settings["victory"], **value}
                new_data["settings"]["victory"]["classes_present"] = True
            else:
                new_data["settings"][key] = value
    else:
        # Keine Settings vorhanden, nutze Standard
        new_data["settings"] = standard_settings
    
    # Schreibe Ziel-Level
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"Erstellt: {target_file}")

print("\nAlle Level 201-234 wurden erfolgreich erstellt!")
