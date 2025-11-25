# OOP Framework - Schüler-Version

## Installation

1. **ZIP-Datei entpacken**
   - Entpacke die `framework_version_X.zip` in einen Ordner deiner Wahl
   - z.B. `C:\Benutzer\DeinName\oop_framework\`

2. **Python öffnen**
   - Öffne Thonny oder eine andere Python-Umgebung
   - Navigiere zum entpackten Ordner

3. **Programm starten**
   - Öffne `schueler.py` in Thonny
   - Klicke auf "Ausführen" (grüner Play-Button oder F5)
   - Das Spiel startet automatisch!

## Wichtig: Keine Installation von pygame nötig!

**pygame ist bereits enthalten!** 

Früher musstet ihr pygame über "Verwalte Pakete" installieren. 
Das ist jetzt **nicht mehr nötig**, da pygame direkt im Framework 
mitgeliefert wird (im `lib/` Ordner).

Falls pygame bereits installiert ist, wird automatisch die 
installierte Version verwendet. Falls nicht, nutzt das Framework 
die mitgelieferte Version.

## Ordnerstruktur

```
oop_framework/
├── framework/          # Framework-Code (nicht ändern!)
├── sprites/            # Grafiken für das Spiel
├── level/              # Level-Dateien (level0.json, level1.json, ...)
├── lib/                # Gebündelte Bibliotheken (pygame)
├── schueler.py         # HIER programmierst du!
├── leveleditor.py      # Level-Editor (optional)
└── setup_pygame.py     # Automatisches pygame-Setup
```

## Erste Schritte

1. Öffne `schueler.py` in Thonny
2. Ändere die Levelnummer in Zeile 7, z.B.:
   ```python
   level.lade(0, weiblich=False)  # Level 0 laden
   ```
3. Programmiere zwischen den Kommentaren:
   ```python
   # Ab hier darfst du programmieren:
   
   held.geh()
   held.links()
   
   # Dieser Befehl muss immer am Ende stehen
   ```
4. Starte das Programm mit F5

## Level-Editor

Der Level-Editor ist optional und kann verwendet werden, um eigene
Level zu erstellen:

1. Öffne `leveleditor.py` in Thonny
2. Starte mit F5
3. Erstelle dein eigenes Level
4. Speichere als `level/levelXX.json`

## Probleme?

### "ModuleNotFoundError: No module named 'pygame'"

Das sollte **nicht** mehr passieren, da pygame mitgeliefert wird.
Falls doch:
1. Stelle sicher, dass der `lib/` Ordner vorhanden ist
2. Stelle sicher, dass `setup_pygame.py` im Hauptordner liegt
3. Starte Thonny neu

### Das Spiel startet nicht

1. Überprüfe, dass Python 3.10 oder neuer installiert ist
2. Überprüfe, dass alle Dateien korrekt entpackt wurden
3. Öffne `schueler.py` in Thonny und nicht direkt per Doppelklick

## Support

Bei Fragen wende dich an deinen Lehrer/deine Lehrerin.

---

**Viel Erfolg beim Programmieren!** 🎮
