"""
Automatisches Setup für pygame aus lokalem lib/ Verzeichnis.

Dieses Modul fügt automatisch das lokale lib/ Verzeichnis zum Python-Pfad hinzu,
falls pygame dort vorhanden ist. Dadurch wird pygame aus der Distribution verwendet,
ohne dass eine separate Installation erforderlich ist.

Verwendung:
    - Wird automatisch von schueler.py und leveleditor.py geladen
    - Transparent für den Benutzer
"""

import sys
import os
from pathlib import Path

def setup_local_pygame():
    """Fügt lokales lib/ Verzeichnis zum sys.path hinzu, wenn pygame dort gefunden wird."""
    # Finde das Projektverzeichnis (Parent von framework/)
    current_dir = Path(__file__).parent.parent.absolute()
    lib_dir = current_dir / 'lib'
    
    # Prüfe, ob lib/pygame existiert
    if lib_dir.exists() and (lib_dir / 'pygame').exists():
        lib_dir_str = str(lib_dir)
        
        # Füge lib/ am Anfang des sys.path hinzu (höchste Priorität)
        if lib_dir_str not in sys.path:
            sys.path.insert(0, lib_dir_str)
            print(f"[Framework] Verwende gebündeltes pygame aus: {lib_dir}")
            return True
    
    return False

# Automatisch beim Import ausführen
setup_local_pygame()
