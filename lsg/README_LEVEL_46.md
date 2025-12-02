# Level 46 Tests - Übersicht

## Musterlösung
- **Datei:** `lsg/lsg_46_knappe.py`
- **Beschreibung:** Vollständige Knappe-Klasse für Level 46

## Test-Dateien

### Test 1: Klassen-Struktur (`lsg/test_lsg_46_1.py`)
Prüft:
- ✓ Knappe Klasse existiert
- ✓ `__init__(self, x, y, richtung)` Signatur (OHNE weiblich!)
- ✓ Alle erforderlichen Methoden vorhanden:
  - `get_x()`, `get_y()`, `get_richtung()`, `get_typ()`
  - `geh()`, `links()`, `rechts()`, `set_richtung()`
- ✓ Alle erforderlichen Attribute gesetzt: x, y, richtung, name, typ
- ✓ KEIN weiblich Attribut vorhanden

### Test 2: Privacy (`lsg/test_lsg_46_2.py`)
Prüft:
- ✓ Private Attribute: x, y, richtung (mit Gettern)
- ✓ Öffentliche Attribute: name, typ
- ✓ typ Wert ist "Knappe"
- ✓ KEIN weiblich Attribut oder Getter

### Test 3: Vollständiger Level-Test (`lsg/test_lsg_46_3.py`)
Prüft:
- ✓ Level 46 lädt erfolgreich
- ✓ Knappe wird gespawnt
- ✓ Knappe hat korrektes typ Attribut für Rendering
- ✓ _student_has_class() funktioniert
- ✓ Victory check funktioniert
- ✓ Bewegung funktioniert

## Test ausführen

```bash
python test_lsg_46.py
```

Dieser Runner:
1. Erstellt Backup von `klassen/knappe.py`
2. Kopiert Musterlösung nach `klassen/knappe.py`
3. Führt alle drei Tests aus
4. Stellt das Original wieder her

## Wichtige Änderungen

### framework/spielfeld.py
- Knappe Spawn versucht zuerst `(x, y, richtung)` ohne weiblich
- Fallback auf `(x, y, richtung, weiblich)` für ältere Levels

### level/level46.json
- `load_from_klassen: true` für Knappe
- `attributes: []` (typ ist öffentlich, nicht zu validieren)
- `methods` enthält auch `get_typ`

### Knappe Klasse (Musterlösung)
- `__init__(self, x, y, richtung)` - OHNE weiblich
- Private: `__x`, `__y`, `__richtung`
- Öffentlich: `name`, `typ`
- Alle erforderlichen Getter und Bewegungsmethoden
