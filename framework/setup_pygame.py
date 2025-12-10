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
    """Versucht erst system-pygame, dann lokales lib/ Verzeichnis als Fallback."""
    # Prüfe zuerst, ob pygame bereits im System installiert ist
    try:
        import pygame as _pygame_test
        # pygame ist bereits verfügbar - verwende System-Installation
        print(f"[Framework] Verwende system-installiertes pygame {_pygame_test.version.ver}")
        return True
    except ImportError:
        pass
    
    # pygame nicht gefunden - versuche lokales lib/ Verzeichnis als Fallback
    current_dir = Path(__file__).parent.parent.absolute()
    lib_dir = current_dir / 'lib'
    
    # Prüfe, ob lib/pygame existiert
    if lib_dir.exists() and (lib_dir / 'pygame').exists():
        lib_dir_str = str(lib_dir)
        
        # Füge lib/ am Anfang des sys.path hinzu (für Fallback)
        if lib_dir_str not in sys.path:
            sys.path.insert(0, lib_dir_str)
            print(f"[Framework] System-pygame nicht gefunden - verwende gebündeltes pygame aus: {lib_dir}")
            return True
    
    print("[Framework] Warnung: Weder system-pygame noch gebündeltes pygame gefunden!")
    return False

# Automatisch beim Import ausführen
setup_local_pygame()
