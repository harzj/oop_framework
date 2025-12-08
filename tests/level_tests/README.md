# Level Test System

Ein strukturiertes Test-System für OOP-Framework Levels mit funktionalen Tests.

## Struktur

```
tests/level_tests/
├── level_40_private_attributes/
│   ├── schueler.py              # Hauptimplementierung
│   ├── held.py                  # Korrekte Held-Klasse
│   ├── held_fail_public.py      # Fehlvariante: öffentliche Attribute
│   └── test_config.json         # Funktionale Tests
├── level_47_inheritance_zettel/
│   ├── schueler.py
│   ├── spielobjekt.py
│   ├── zettel.py
│   ├── zettel_fail_public.py
│   └── test_config.json
└── ...
```

## Verwendung

1. **GUI starten:**
   ```bash
   python test_system.py
   ```

2. **Test-Verzeichnisse:**
   - Jedes Verzeichnis in `tests/level_tests/` repräsentiert einen Level-Test
   - Verzeichnis muss mindestens `schueler.py` ODER Klassendateien (`held.py`, etc.) enthalten

3. **Dateinamenskonventionen:**
   - `schueler.py` - Hauptimplementierung (wird nach `schueler.py` kopiert)
   - `<klasse>.py` - Klassendateien (z.B. `held.py`, `knappe.py`) → nach `klassen/<klasse>.py`
   - `schueler_fail*.py` - Fehlvarianten von schueler.py (sollten FAIL sein)
   - `<klasse>_fail*.py` - Fehlvarianten von Klassendateien (sollten FAIL sein)
   - `test_config.json` - Funktionale Tests (optional)

## test_config.json Format

```json
{
  "level": 40,
  "description": "Level 40 - Private Attribute ohne Getter",
  "functional_tests": [
    {
      "description": "Test geh() method moves hero down",
      "level_number": 40,
      "initial_state": {
        "held": {"x": 1, "y": 1, "richtung": "down"}
      },
      "actions": [
        {"type": "method_call", "target": "held", "method": "geh"}
      ],
      "assertions": [
        {"type": "position", "x": 1, "y": 2},
        {"type": "attribute", "name": "richtung", "value": "down"}
      ]
    },
    {
      "description": "Test privacy - attributes should not be directly accessible",
      "assertions": [
        {"type": "privacy", "attribute": "x", "should_be_private": true},
        {"type": "privacy", "attribute": "name", "should_be_private": false}
      ]
    }
  ]
}
```

### Assertion-Typen

#### 1. Position-Check
```json
{"type": "position", "x": 1, "y": 2}
```
Prüft Held-Position nach Aktionen.

#### 2. Attribute-Check
```json
{"type": "attribute", "name": "richtung", "value": "down"}
```
Prüft Attributwert (über Getter oder direkt).

#### 3. Privacy-Check
```json
{"type": "privacy", "attribute": "x", "should_be_private": true}
```
Prüft ob Attribut privat (mit `__`) oder öffentlich ist.

#### 4. Inheritance-Check
```json
{"type": "inheritance", "class": "Zettel", "parent": "Spielobjekt"}
```
Prüft Vererbungsbeziehung.

#### 5. Method-Exists-Check
```json
{"type": "method_exists", "class": "Held", "method": "geh"}
```
Prüft ob Methode existiert und aufrufbar ist.

#### 6. Method-Call mit Return-Check
```json
{
  "type": "method_call",
  "method": "get_spruch",
  "expected_return": "Sesam öffne dich"
}
```
Ruft Methode auf und prüft Rückgabewert.

### Action-Typen

#### 1. Method Call
```json
{"type": "method_call", "target": "held", "method": "geh"}
```
Ruft Methode auf Objekt auf.

#### 2. Method Call mit Args
```json
{"type": "method_call", "method": "set_spruch", "args": ["Neuer Text"]}
```

#### 3. Create Instance (für Unit-Tests)
```json
{"type": "create_instance", "args": [1, 2, "down"]}
```

## Test-Ablauf

1. **Backup:** Alle relevanten Dateien werden gesichert
2. **Copy:** Test-Dateien werden in Produktionsverzeichnisse kopiert
3. **Execute:** `schueler.py` wird ausgeführt (mit Timeout)
4. **Victory Check:** Prüft auf `[TEST] Level erfolgreich beendet` oder `Victory: True`
5. **Functional Tests:** Führt Tests aus `test_config.json` aus (falls vorhanden)
6. **Restore:** Alle Dateien werden wiederhergestellt
7. **Result:** Pass/Fail basierend auf erwarteten Outcomes

## Beispiele

### Einfacher Test (nur Victory-Check)
```
level_tests/level_10_basic/
├── schueler.py
└── held.py
```

### Mit Fehlvarianten
```
level_tests/level_40_private/
├── schueler.py
├── held.py
├── held_fail_public.py       # Sollte FAIL sein
└── held_fail_no_methods.py   # Sollte FAIL sein
```

### Mit funktionalen Tests
```
level_tests/level_40_private/
├── schueler.py
├── held.py
├── held_fail_public.py
└── test_config.json          # Funktionale Tests
```

## Vorteile gegenüber lsg-Tests

1. **Strukturiert:** Ein Verzeichnis pro Level mit allen Dateien
2. **Fail-Tests:** Automatische Erkennung von Fehlvarianten
3. **Funktionale Tests:** Methoden-Validierung ohne Level-Ausführung
4. **Wiederherstellung:** Automatisches Backup/Restore aller Dateien
5. **Flexibel:** Beliebige Klassendateien können getestet werden
6. **Dokumentiert:** test_config.json beschreibt was getestet wird
