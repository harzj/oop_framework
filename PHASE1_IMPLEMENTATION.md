# Phase 1 Implementation: F4 Class Requirements Menu

## Summary

Phase 1 of the student-class overhaul has been successfully implemented. The level editor now has an F4 menu that allows configuring per-class requirements for student implementations.

## What Was Implemented

### 1. Data Structure
- Added `self.class_requirements` dictionary to store per-class configuration
- Format: `{"ClassName": {"use_student": bool, "inherits": str, "methods": [str], "attributes": [str]}}`

### 2. User Interface (F4 Menu)
- **Hotkey**: Press F4 in the level editor to open the class requirements dialog
- **Tabbed Interface**: One tab per class (Held, Herz, Tuer, Tor, Hindernis, Knappe, Monster, Bogenschuetze, Schluessel, Code, Villager)
- **Per Tab Configuration**:
  - Toggle: "Use student class" (whether to load student implementation for this class)
  - Dropdown: "Erbt von" (inheritance - which framework class this should inherit from)
  - Checkboxes: Required methods (e.g., geh, links, rechts, nimm, etc.)
  - Checkboxes: Required attributes (e.g., hp, x, y, gold, etc.)

### 3. Persistence
- **Saving**: Configuration is saved to level JSON under `settings.class_requirements`
- **Loading**: Configuration is loaded when opening a level file
- **Backward Compatibility**: Old levels without class_requirements work perfectly

### 4. Available Options Per Class

#### Held / Knappe
- Methods: geh, links, rechts, oben, unten, nimm, benutze, sage, gib
- Attributes: hp, gold, inventar, x, y
- Inheritance: Objekt, Charakter, None

#### Monster / Bogenschuetze
- Methods: geh, links, rechts, oben, unten, angriff, schiesse (archer only)
- Attributes: hp, x, y, pfeile (archer only)
- Inheritance: Objekt, Charakter, Monster (archer only), None

#### Herz / Schluessel
- Methods: sammeln, position
- Attributes: x, y, (farbe for Schluessel)
- Inheritance: Objekt, Gegenstand, None

#### Tuer / Tor
- Methods: oeffnen, schliessen, ist_offen
- Attributes: x, y, offen, (farbe for Tuer)
- Inheritance: Objekt, None

#### Hindernis
- Methods: position
- Attributes: x, y, typ
- Inheritance: Objekt, None

#### Code
- Methods: lesen, position
- Attributes: x, y, text
- Inheritance: Objekt, Gegenstand, None

#### Villager
- Methods: sprechen, quest_geben, quest_abschliessen
- Attributes: x, y, name, quest
- Inheritance: Objekt, None

## Testing

### Automated Tests
- Created `test_f4_requirements.py` to verify:
  - ✓ JSON data structure is correct
  - ✓ LevelEditor.from_json() loads class_requirements
  - ✓ LevelEditor.to_json() exports class_requirements
  - ✓ Data persists across save/load cycles

### Regression Testing
- ✓ All existing tests in `tests/run_lsg_tests.py` still pass (35/35)
- ✓ No breaking changes to existing functionality

## Example Level JSON

```json
{
  "tiles": ["wpw", "www"],
  "settings": {
    "Held": {"public": true},
    "class_requirements": {
      "Held": {
        "use_student": true,
        "inherits": "Charakter",
        "methods": ["geh", "links", "rechts", "nimm"],
        "attributes": ["hp", "x", "y"]
      }
    }
  }
}
```

## Usage Instructions

1. Open level editor: `python leveleditor.py`
2. Press **F4** to open class requirements dialog
3. Select a class tab (e.g., "Held")
4. Configure:
   - Check "Held-Schülerklasse verwenden" to enable student implementation
   - Select inheritance from dropdown (e.g., "Charakter")
   - Check required methods (e.g., geh, links, rechts)
   - Check required attributes (e.g., hp, x, y)
5. Click OK to save configuration
6. Press **S** to save the level (includes class_requirements in JSON)

## Files Modified

- `leveleditor.py`:
  - Added `self.class_requirements = {}` in `__init__`
  - Added F4 hotkey handler in `run()` event loop
  - Added `open_class_requirements_dialog()` method (150+ lines)
  - Added loading in `from_json()` method
  - Added saving in `to_json()` method

## Files Created

- `test_f4_requirements.py`: Automated test for F4 feature
- `level/level_test_f4_requirements.json`: Test level with class requirements

## Next Steps (Phase 2)

Phase 1 is complete and isolated from the framework core. The next phase will involve:

1. **Framework Dual-Mode Implementation**:
   - Modify `spielfeld.py` to read `class_requirements` from level JSON
   - Implement legacy mode: load framework classes as before when no class_requirements
   - Implement student mode: when `class_requirements` present and `use_student=True`, load student class instead
   - Use meta-wrappers to provide framework base class functionality

2. **Student Class Loader**:
   - Detect student classes in `schueler.py` or `klassen/` subfolder
   - Validate that student class has required methods/attributes
   - Validate inheritance hierarchy matches requirements
   - Provide helpful error messages when requirements not met

3. **Validation System** (Phase 3):
   - Check if student class implements all required methods
   - Check if student class has all required attributes
   - Verify inheritance chain is correct
   - Generate user-friendly validation reports

## Critical Constraints

- **Backward Compatibility**: All existing levels and tests must continue to work
- **Test Suite**: All 35 tests in `tests/run_lsg_tests.py` must pass after each phase
- **Robustness**: Framework should never crash due to student code issues
- **Clear Errors**: When student code is wrong, provide clear, educational error messages

## Status

✅ **Phase 1 Complete**: F4 menu for class requirements configuration
⏳ **Phase 2 Pending**: Framework dual-mode implementation
⏳ **Phase 3 Pending**: Validation system

All tests pass. Ready to proceed to Phase 2 when approved.
