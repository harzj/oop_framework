# OOP Framework - Objektorientierte Programmierung spielerisch lernen

Ein interaktives Lernframework zum Erlernen der objektorientierten Programmierung in Python. Schülerinnen und Schüler steuern einen Helden durch verschiedene Level, sammeln Herzen und lösen Rätsel – zunächst durch einfache Befehlssequenzen, später durch die Implementierung eigener Klassen.

## 🎯 Zielsetzung und Zweck

Dieses Framework wurde für den Informatikunterricht entwickelt, um:

- **Grundlagen der Programmierung** vermitteln (Schleifen, Bedingungen, Funktionsaufrufe)
- **Objektorientierte Konzepte** schrittweise einführen (Objekte, Attribute, Methoden)
- **Klassendesign** praktisch üben (Vererbung, Kapselung, Getter/Setter)
- **Problemlösendes Denken** fördern durch immer komplexere Level

Das Framework enthält über 50 Level mit steigendem Schwierigkeitsgrad sowie einen integrierten **Level-Editor** zum Erstellen eigener Aufgaben.

---

## 📚 Die zwei Phasen

### Phase 1: Befehle und Objekte (Level 0–34)

In dieser Phase lernen die Schüler:
- Objekte und ihre Methoden kennen
- Einfache Algorithmen zu entwickeln
- Mit Schleifen und Bedingungen zu arbeiten
- Objekte zu manipulieren und miteinander interagieren zu lassen

**Alle Programmierung erfolgt in der Datei `schueler.py`.**

### Phase 2: Klassen implementieren (Level 35–58)

In dieser Phase implementieren die Schüler eigene Klassen:
- Zunächst einfache Klassen mit öffentlichen Attributen
- Dann Klassen mit privaten Attributen und Getter/Setter
- Schließlich Vererbungshierarchien und komplexe Klassensysteme

**Die Klassen werden im Ordner `klassen/` erstellt.**

---

## 🎮 How-To: So wird programmiert

### Grundstruktur der `schueler.py`

```python
from framework.grundlage import level
level.lade(1, weiblich=False)  # Level-Nummer und Geschlecht des Helden
from framework.grundlage import *

# Ab hier darfst du programmieren:

# ... dein Code hier ...

# Dieser Befehl muss immer am Ende stehen
framework.starten()
```

### Verfügbare Objekte

| Objekt | Beschreibung |
|--------|--------------|
| `held` | Der Spieler-Charakter |
| `knappe` | Ein Begleiter (in manchen Levels) |
| `zettel` | Enthält Zaubersprüche |
| `tuer` | Kann mit Sprüchen oder Schlüsseln geöffnet werden |
| `tor` | Kann bedient werden |
| `level` | Das aktuelle Spielfeld |

### Befehle für den Helden und Knappen

```python
# Bewegung
held.geh()              # Ein Feld vorwärts gehen
held.links()            # Nach links drehen
held.rechts()           # Nach rechts drehen
held.zurueck()          # Ein Feld rückwärts gehen

# Aktionen
held.nimm_herz()        # Herz aufsammeln
held.ist_auf_herz()     # Prüfen, ob auf einem Herz

# Mit Animationsverzögerung (in Millisekunden)
held.geh(100)           # Langsamer gehen für sichtbare Animation
```

### Interaktion mit Objekten

```python
# Zettel und Sprüche
spruch = zettel.gib_spruch()      # Spruch vom Zettel lesen
tuer.spruch_anwenden(spruch)       # Spruch auf Tür anwenden

# Schlüssel und Türen
schluessel = level.gib_objekt_bei(x, y)  # Objekt an Position holen
schluessel.set_farbe("red")              # Farbe setzen
tuer.verwende_schluessel(schluessel)     # Tür mit Schlüssel öffnen

# Objekte vor dem Helden
objekt = held.gib_objekt_vor_dir()       # Objekt vor dem Helden

# Neue Objekte erstellen (ab Level 34)
neuer_schluessel = Schluessel(x, y)
level.objekt_hinzufuegen(neuer_schluessel)
```

### Schleifen und Bedingungen

```python
# For-Schleife
for i in range(10):
    held.geh()
    if held.ist_auf_herz():
        held.nimm_herz()

# While-Schleife
while not held.ist_auf_herz():
    held.geh()
```

---

## 🏗️ Klassen implementieren (Phase 2)

Ab Level 35 müssen eigene Klassen im Ordner `klassen/` erstellt werden.

### Beispiel: Einfache Held-Klasse (Level 35)

```python
# Datei: klassen/held.py
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Held"
        self.typ = "Held"
```

### Beispiel: Klasse mit privaten Attributen (Level 40+)

```python
# Datei: klassen/held.py
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.__x = x
        self.__y = y
        self.__richtung = richtung
        self.__weiblich = weiblich
        self.__name = "Held"
        self.__typ = "Held"
    
    def get_x(self):
        return self.__x
    
    def set_x(self, wert):
        self.__x = wert
    
    # ... weitere Getter und Setter
```

### Beispiel: Vererbung (Level 50+)

```python
# Datei: klassen/spielobjekt.py
class Spielobjekt:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
    
    def get_x(self):
        return self.__x

# Datei: klassen/hindernis.py
from spielobjekt import Spielobjekt

class Hindernis(Spielobjekt):
    def __init__(self, x, y, typ):
        super().__init__(x, y)
        self.__typ = typ
```

---

## 👩‍🏫 Hinweise für Lehrkräfte

### Enthaltene Werkzeuge

| Datei/Ordner | Beschreibung |
|--------------|--------------|
| `leveleditor.py` | Grafischer Level-Editor zum Erstellen und Bearbeiten von Levels |
| `run_tests_gui.py` | Test-Runner mit grafischer Oberfläche für alle Level |
| `make_distribution.py` | Erstellt ein ZIP-Archiv für die Verteilung an Schüler |
| `lsg/` | Musterlösungen für alle Level (lsg1.py bis lsg57.py) |
| `Material/` | Zusätzliches Unterrichtsmaterial |
| `docs/` | Technische Dokumentation |

### Level-Editor

Der Level-Editor (`leveleditor.py`) ermöglicht:
- Erstellen neuer Level mit Drag & Drop
- Konfiguration von Siegbedingungen
- Definition von Klassenanforderungen für Phase 2
- Export und Import von Level-Dateien

Starten mit:
```bash
python leveleditor.py
```

### Test-Runner

Der Test-Runner (`run_tests_gui.py`) führt automatisch alle Musterlösungen aus und prüft, ob die Level korrekt gelöst werden:
```bash
python run_tests_gui.py
```

### Distribution erstellen

Um ein Schüler-Paket ohne Lösungen zu erstellen:
```bash
python make_distribution.py
```

Dies erstellt ein ZIP-Archiv im `dist/`-Ordner.

### Ordnerstruktur

```
oop_framework/
├── schueler.py          # Hier programmieren die Schüler
├── leveleditor.py       # Level-Editor
├── framework/           # Framework-Code (nicht verändern!)
├── klassen/             # Schüler-Klassen für Phase 2
├── level/               # Level-Dateien (JSON)
├── sprites/             # Grafiken
├── lsg/                 # Musterlösungen
├── Material/            # Unterrichtsmaterial
├── tests/               # Automatische Tests
└── docs/                # Dokumentation
```

---

## 🚀 Installation

1. Python 3.8+ installieren
2. Pygame installieren: `pip install pygame`
3. Framework starten: `python schueler.py`

---

## 📝 Lizenz

Entwickelt für den Informatikunterricht.

© 2025 Johannes Harz  
Fachkonferenz Informatik  
Cusanus Gymnasium St. Wendel
