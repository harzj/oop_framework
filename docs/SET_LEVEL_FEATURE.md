# Set Level Funktionalität

## Überblick

Mit der neuen "Level setzen" Funktion können Charakterklassen (Held, Knappe, Monster, Bogenschuetze, Villager) eine Referenz zum Spielfeld-Objekt erhalten.

## Verwendung im Leveleditor

1. Öffne den Leveleditor
2. Drücke **F4** (Klassen-Anforderungen Dialog)
3. Wähle den Tab der gewünschten Charakter-Klasse (z.B. "Held")
4. Aktiviere die Checkbox **"Level setzen (set_level Methode)"** ganz oben im Dialog
5. Speichere das Level

## Was passiert?

Wenn "Level setzen" aktiviert ist:

### Im Level-JSON
```json
{
  "class_requirements": {
    "Held": {
      "expects_set_level": true,
      ...
    }
  }
}
```

### In der Schüler-Klasse

Die Schüler-Implementierung muss:

1. **`level` Attribut** im Konstruktor auf `None` setzen
2. **`set_level(spielfeld)` Methode** implementieren

**Beispiel (klassen/held.py):**
```python
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.level = None  # Wird später vom Framework gesetzt
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Mein Held"
    
    def set_level(self, spielfeld):
        """Wird vom Framework nach dem Spawn aufgerufen"""
        self.level = spielfeld
    
    def geh(self):
        """Beispiel: Bewegung mit Kollisionsprüfung"""
        if self.level is None:
            return  # Kein Level vorhanden
        
        # Berechne Zielposition
        ziel_x, ziel_y = self.x, self.y
        if self.richtung == "up":
            ziel_y -= 1
        elif self.richtung == "down":
            ziel_y += 1
        elif self.richtung == "left":
            ziel_x -= 1
        elif self.richtung == "right":
            ziel_x += 1
        
        # Prüfe ob Zielfeld frei ist
        if self.level.ist_feld_frei(ziel_x, ziel_y):
            self.x = ziel_x
            self.y = ziel_y
```

### Im Framework

Das Framework ruft automatisch `set_level(spielfeld)` nach dem Spawn auf:

```python
# In framework/spielfeld.py - Held Spawn
if expects_set_level and hasattr(student_inst, 'set_level'):
    try:
        student_inst.set_level(self)  # self = Spielfeld-Objekt
    except Exception as e:
        print(f"[WARNUNG] Fehler beim Aufruf von Held.set_level(): {e}")
```

## Vorteile

Mit `self.level` können Charaktere:

- **Kollisionserkennung**: Prüfen ob ein Feld passierbar ist
- **Objektabfrage**: Welche Objekte sind an einer Position?
- **Spielfeld-Informationen**: Breite, Höhe, etc.
- **Interaktion**: Mit anderen Objekten auf dem Spielfeld interagieren

## Verfügbare Spielfeld-Methoden

Wenn `self.level` gesetzt ist, sind z.B. folgende Methoden verfügbar:

- `self.level.ist_feld_frei(x, y)` - Prüft ob Position frei ist
- `self.level.objekte` - Liste aller Objekte
- `self.level.grid_w`, `self.level.grid_h` - Spielfeld-Dimensionen
- `self.level.gib_objekt_an(x, y)` - Objekt an Position

## Abwärtskompatibilität

- **Alte Levels ohne `expects_set_level`**: Funktionieren weiterhin normal
- **Alte `setze_level()` Methode**: Wird als Fallback noch unterstützt (Legacy)
- **Framework-Klassen**: Benötigen kein `set_level()`, funktionieren wie bisher

## Betroffene Klassen

Die Checkbox ist verfügbar für:
- Charakter (abstrakte Basisklasse)
- Held
- Knappe
- Monster
- Bogenschuetze
- Villager

## Implementation Details

### Leveleditor (leveleditor.py)
- Neue Checkbox in `open_class_requirements_dialog()` für Charakterklassen
- Speichert `expects_set_level: true/false` in Level-JSON

### Framework (framework/spielfeld.py)
- Prüft `expects_set_level` Flag für jede Charakterklasse
- Ruft `set_level(self)` nach Spawn auf (self = Spielfeld-Objekt)
- Fehlerbehandlung mit Warnung bei Exceptions
