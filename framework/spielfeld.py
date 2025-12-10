# framework/spielfeld.py
import sys
import pygame
from .level import Level
from .utils import richtung_offset, lade_sprite
from .tuer import Tuer
from .code import Code
from .tor import Tor
from .knappe import Knappe
from random import randint
import random
import importlib
import traceback
import threading
import tkinter as _tk
from tkinter import messagebox as _tk_messagebox
import os
import ast
import types
import math
 
class Spielfeld:
    def __init__(self, levelfile, framework, feldgroesse=64, auto_erzeuge_objekte=True):
        # basic initialization (rest of __init__ continues below)
        self.framework = framework
        self.levelfile = levelfile
        try:
            setattr(self.framework, 'spielfeld', self)
        except Exception:
            pass
        self.feldgroesse = feldgroesse
        try:
            self.level = Level(levelfile)
        except Exception:
            # best-effort fallback
            self.level = Level(levelfile)
        try:
            self.settings = self.level.settings
        except Exception:
            self.settings = {}
        try:
            # victory settings cached separately for compatibility with check_victory
            self.victory_settings = self.settings.get('victory', {}) if isinstance(self.settings, dict) else {}
        except Exception:
            self.victory_settings = {}
        try:
            # class_requirements from F4 menu (Phase 2 implementation)
            self.class_requirements = self.settings.get('class_requirements', {}) if isinstance(self.settings, dict) else {}
        except Exception:
            self.class_requirements = {}
        try:
            self._required_spawn_classes = self._compute_required_classes()
        except Exception:
            self._required_spawn_classes = set()
        self.objekte = []
        self.held = None
        self.knappe = None
        
        # Template objects for rebuild mode (rendered with 25% opacity)
        self.template_objects = []
        self.rebuild_mode = bool(self.victory_settings.get('rebuild_mode', False)) if self.victory_settings else False

        self._logged_broken_objects = set()
        #self.zufallscode = str(randint(1000,9999))
        self.zufallscode = self.random_zauberwort()
        self.orc_names = []
        
        # Initialize class validation state (will be set after spawning)
        self._class_validation_passed = False
        
        # Flag to prevent repeated victory messages
        self._victory_message_shown = False
        
        if auto_erzeuge_objekte:
            self._spawn_aus_level()
            # Validate student classes ONCE after spawning
            self._validate_classes_at_level_start()
            
    def random_zauberwort(self):
        zauberwoerter = [
            "Alohomora", "Ignis", "Fulgura", "Lumos", "Nox",
            "Aqua", "Ventus", "Terra", "Glacius", "Silencio",
            "Accio", "Protego", "Obliviate", "Impervius"
        ]

        # Wähle zufälligen Spruch
        spruch = random.choice(zauberwoerter) + " " + random.choice(zauberwoerter)
        return spruch 
        

    def _spawn_aus_level(self):
        from .held import Held
        from .herz import Herz
        from .monster import Monster, Bogenschuetze
        from .tor import Tor
        from .code import Code
        from .tuer import Tuer
        from .gegenstand import Gegenstand
        from .schluessel import Schluessel

        # Orientierungen evtl. in self.settings["orientations"] als {"x,y":"up"}
        orients = self.settings.get("orientations", {}) if isinstance(self.settings, dict) else {}
        # Tür-/Schlüssel-Farben in self.settings["colors"] (z.B. {"3,4":"golden"})
        colors = self.settings.get("colors", {}) if isinstance(self.settings, dict) else {}
        # Optional randomization settings (default False for backwards compatibility)
        random_doors = bool(self.settings.get('random_door', False))
        random_keys = bool(self.settings.get('random_keys', False))

        # If randomization requested, prepare an override mapping for colors
        colors_override = dict(colors) if isinstance(colors, dict) else {}
        if random_doors or random_keys:
            # Collect door and key positions with their original colors
            door_positions = []  # list of (x,y,color)
            key_positions = []   # list of (x,y,color)
            try:
                for yy, row in enumerate(self.level.tiles):
                    for xx, code in enumerate(row):
                        if isinstance(code, str) and code.lower() == 'd':
                            # Doors default to 'green' when no explicit color configured
                            c = colors.get(f"{xx},{yy}", "green")
                            door_positions.append((xx, yy, c))
                        elif isinstance(code, str) and code.lower() == 's':
                            # keys default to green if not specified
                            c = colors.get(f"{xx},{yy}", "green")
                            key_positions.append((xx, yy, c))
            except Exception:
                door_positions = []
                key_positions = []

            # Shuffle/mutate key colors if requested (compute keys first)
            key_color_map = {}
            if random_keys and key_positions:
                try:
                    origk = [c for (_, _, c) in key_positions]
                    shuffledk = list(origk)
                    random.shuffle(shuffledk)
                    for (pos, newc) in zip(key_positions, shuffledk):
                        xx, yy, _ = pos
                        key_color_map[f"{xx},{yy}"] = newc
                except Exception:
                    key_color_map = {}

            # Shuffle/mutate door colors if requested
            # Doors should be mapped to colors that actually exist among keys
            # (after any key-randomization above). If there are at least as many
            # distinct key colors as doors, choose a subset without replacement
            # so doors do not duplicate; otherwise recycle key colors as needed.
            door_color_map = {}
            if random_doors and door_positions:
                try:
                    # determine final set of key colors available
                    if key_color_map:
                        key_colors_final = list(set(key_color_map.values()))
                    else:
                        key_colors_final = list(set([c for (_, _, c) in key_positions]))

                    # fallback: if no keys at all, behave like previous door-shuffle
                    if not key_colors_final:
                        orig = [c for (_, _, c) in door_positions]
                        shuffled = list(orig)
                        random.shuffle(shuffled)
                        for (pos, newc) in zip(door_positions, shuffled):
                            xx, yy, _ = pos
                            door_color_map[f"{xx},{yy}"] = newc
                    else:
                        n_doors = len(door_positions)
                        n_keys = len(key_colors_final)
                        # create list of colors to assign to doors
                        if n_doors <= n_keys:
                            # sample a subset of key colors without replacement
                            chosen = random.sample(key_colors_final, n_doors)
                        else:
                            # need to reuse some key colors; build a list by
                            # repeating and then shuffling
                            repeats = (n_doors // n_keys) + 1
                            pool = (key_colors_final * repeats)[:n_doors]
                            chosen = list(pool)
                        random.shuffle(chosen)
                        for (pos, newc) in zip(door_positions, chosen):
                            xx, yy, _ = pos
                            door_color_map[f"{xx},{yy}"] = newc
                except Exception:
                    door_color_map = {}

            # If keys do not cover all door colors, ensure at least one key exists for each door color
            try:
                if door_color_map and (key_positions or key_color_map):
                    door_colors = set(door_color_map.values())
                    current_key_colors = set(key_color_map.values()) if key_color_map else set(c for (_,_,c) in key_positions)
                    missing = list(door_colors - current_key_colors)
                    if missing and key_positions:
                        # replace some key colors to ensure coverage
                        kp_iter = iter(key_positions)
                        for need in missing:
                            try:
                                xx, yy, _ = next(kp_iter)
                            except StopIteration:
                                # restart iterator
                                kp_iter = iter(key_positions)
                                xx, yy, _ = next(kp_iter)
                            key_color_map[f"{xx},{yy}"] = need
            except Exception:
                pass

            # Merge overrides into colors_override
            try:
                colors_override.update(door_color_map)
                colors_override.update(key_color_map)
            except Exception:
                pass
        else:
            colors_override = dict(colors)
        # Villager gender in self.settings["villagers"] as {"x,y": "female"/"male"}
        villagers = self.settings.get("villagers", {}) if isinstance(self.settings, dict) else {}
        # Quests in settings: self.settings["quests"]["x,y"] -> {"modus":"items"/"raetsel", "wuensche":[...], "anzahl":int}
        quests = self.settings.get("quests", {}) if isinstance(self.settings, dict) else {}

        # Level-wide quest/gold settings
        try:
            initial_gold = int(self.settings.get('initial_gold', 0) or 0)
        except Exception:
            initial_gold = 0
        try:
            quest_max_kosten = int(self.settings.get('quest_max_kosten', 0) or 0)
        except Exception:
            quest_max_kosten = 0
        quest_mode = self.settings.get('quest_mode', None)
        try:
            quest_items_needed = int(self.settings.get('quest_items_needed', 0) or 0)
        except Exception:
            quest_items_needed = 0

        # Detect whether the level requests student classes; we'll treat each
        # entity spawn independently: if a student class for that entity is
        # missing, we skip spawning that entity. The hero (Held) will be drawn
        # if its student class exists.
        try:
            student_mode_enabled = bool(self.settings.get('import_pfad') or self.settings.get('use_student_module') or self.settings.get('student_classes_in_subfolder'))
        except Exception:
            student_mode_enabled = False
        
        # Load template objects if in rebuild mode
        if self.rebuild_mode:
            try:
                template_data = self.settings.get('template_objects', [])
                if isinstance(template_data, list):
                    for tpl in template_data:
                        if isinstance(tpl, dict):
                            self.template_objects.append(tpl)
            except Exception as e:
                print(f"[FEHLER] Konnte template_objects nicht laden: {e}")

        # If quest_mode == 'items', prepare desired item names and prices
        ITEM_NAMES = ["Ring", "Apple", "Sword", "Shield", "Potion", "Scroll", "Bread", "Gem", "Torch", "Amulet"]
        desired_items = []
        desired_prices = {}
        if isinstance(quest_mode, str) and quest_mode.lower() == 'items':
            needed = max(1, min(len(ITEM_NAMES), quest_items_needed or 1))
            # If quest_max_kosten is set but too small for the requested number of items,
            # reduce the number of needed items so minimal total cost (10 per item) fits.
            min_price = 10
            if quest_max_kosten and quest_max_kosten <= (min_price * needed):
                needed = max(1, quest_max_kosten // min_price)
            # choose unique item names
            try:
                desired_items = random.sample(ITEM_NAMES, needed)
            except Exception:
                # fallback
                desired_items = ITEM_NAMES[:needed]

            # assign prices such that sum <= quest_max_kosten (if quest_max_kosten > 0)
            # minimal price per item = 10
            min_price = 10
            max_price = 80
            if quest_max_kosten and quest_max_kosten > min_price * needed:
                remaining_budget = quest_max_kosten - (min_price * needed)
                # distribute remaining_budget among items up to (max_price - min_price)
                adds = [0] * needed
                for i in range(needed):
                    if remaining_budget <= 0:
                        break
                    add = min(remaining_budget, random.randint(0, max_price - min_price))
                    adds[i] = add
                    remaining_budget -= add
                for i, name in enumerate(desired_items):
                    desired_prices[name] = min_price + adds[i]
            else:
                # fallback small prices
                for name in desired_items:
                    desired_prices[name] = min_price

        # collect villagers created so we can inject desired items afterwards
        spawned_villagers = []

        # --- Spawn fixed Hindernis objects for tiles (so level.gib_objekt_bei returns objects)
        # Skip in rebuild_mode - templates will be rendered instead
        if not self.rebuild_mode:
            # Map tile codes to human-readable types
            tile_to_type = {'b': 'Busch', 't': 'Baum', 'm': 'Berg'}
            try:
                HindernisClass = None
                student_mode_enabled = False
                hindernis_requirements = self.class_requirements.get('Hindernis', {})
                hindernis_class_valid = False
                
                # Initialize validation flag (True if not in student mode, False if in student mode until validated)
                self._hindernis_class_valid = True  # Default: valid if no requirements
                
                # Check if classes_present is enabled - if yes, only student classes allowed
                classes_present_mode = self.victory_settings.get('classes_present', False)
                
                # Check if student mode is enabled for Hindernis
                if hindernis_requirements:
                    # Check explicit load flags OR if requirements configured (same logic as _get_entity_class)
                    prefer_schueler = bool(hindernis_requirements.get('load_from_schueler', False))
                    prefer_klassen = bool(hindernis_requirements.get('load_from_klassen', False))
                    has_methods = bool(hindernis_requirements.get('methods', []))
                    has_attrs = bool(hindernis_requirements.get('attributes', []))
                    has_inheritance = hindernis_requirements.get('inherits') and hindernis_requirements.get('inherits') != 'None'
                    
                    student_mode_enabled = prefer_schueler or prefer_klassen or has_methods or has_attrs or has_inheritance
                    if student_mode_enabled:
                        self._hindernis_class_valid = False  # Will be set to True if validation passes
                elif classes_present_mode:
                    # classes_present is true but no Hindernis requirements:
                    # Check if Spielobjekt is implemented - if yes, try to load Hindernis (may inherit from it)
                    spielobjekt_req = self.class_requirements.get('Spielobjekt', {})
                    if spielobjekt_req.get('check_implementation', False):
                        # Spielobjekt is implemented, try to load Hindernis as it may inherit from Spielobjekt
                        student_mode_enabled = True
                        self._hindernis_class_valid = False  # Will be validated below
                    # else: No Spielobjekt and no Hindernis requirements - use framework implementation
                    # student_mode_enabled remains False, framework tiles will be rendered
                
                # Store the student mode flag for rendering logic
                self._hindernis_student_mode_enabled = student_mode_enabled
                
                # Try to get student Hindernis class and validate it ONCE
                if student_mode_enabled:
                    try:
                        # Special case: If no Hindernis requirements but Spielobjekt is implemented,
                        # try to load Hindernis from klassen/ (it may inherit from Spielobjekt)
                        HindernisClass = None
                        if not hindernis_requirements and classes_present_mode:
                            spielobjekt_req = self.class_requirements.get('Spielobjekt', {})
                            if spielobjekt_req.get('check_implementation', False):
                                # Try to load Hindernis from klassen/ directory directly
                                try:
                                    import sys
                                    import importlib
                                    # Try klassen.hindernis
                                    try:
                                        mod = importlib.import_module('klassen.hindernis')
                                        HindernisClass = getattr(mod, 'Hindernis', None)
                                    except Exception:
                                        # Try klassen/hindernis.py directly
                                        try:
                                            import os
                                            repo_root = os.path.dirname(os.path.dirname(__file__))
                                            klassen_path = os.path.join(repo_root, 'klassen')
                                            if klassen_path not in sys.path:
                                                sys.path.insert(0, klassen_path)
                                            mod = importlib.import_module('hindernis')
                                            HindernisClass = getattr(mod, 'Hindernis', None)
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                        
                        # If not loaded via special case, use normal method
                        if HindernisClass is None:
                            HindernisClass = self._get_entity_class('Hindernis', None)
                        
                        if HindernisClass is None:
                            print("Klasse Hindernis fehlt")
                        else:
                            # Validate class requirements ONCE (not per instance)
                            # Create a temporary instance to test validation
                            try:
                                test_inst = HindernisClass(0, 0, 't')
                            except TypeError:
                                try:
                                    test_inst = HindernisClass('t')
                                except Exception:
                                    try:
                                        test_inst = HindernisClass(self.level, 't')
                                    except Exception:
                                        try:
                                            test_inst = HindernisClass(self.level, 0, 0, 't')
                                        except Exception:
                                            test_inst = None
                            
                            if test_inst is not None:
                                validation_ok = True
                                missing_get_typ = False
                                
                                # Get required methods list to check if get_typ is explicitly required
                                required_methods = hindernis_requirements.get('methods', [])
                                get_typ_required = 'get_typ' in required_methods
                                
                                # Check private attributes - check in parent class hierarchy
                                private_attrs = hindernis_requirements.get('attributes_private', {})
                                for attr_name, required in private_attrs.items():
                                    if required:
                                        # Try to find the attribute in the class hierarchy
                                        # Check both own class and parent class name mangling
                                        found = False
                                        for cls in HindernisClass.__mro__:
                                            mangled_name = f"_{cls.__name__}__{attr_name}"
                                            if hasattr(test_inst, mangled_name):
                                                found = True
                                                break
                                        
                                        # Also check if attribute is public (which would be wrong)
                                        has_public = hasattr(test_inst, attr_name) and not attr_name.startswith('_')
                                        
                                        if not found or has_public:
                                            print(f"Hindernis: Attribut '{attr_name}' muss privat sein")
                                            validation_ok = False
                                            break
                                
                                # Check getters separately
                                if validation_ok and private_attrs:
                                    for attr_name, required in private_attrs.items():
                                        if required:
                                            getter_name = f'get_{attr_name}'
                                            has_getter = hasattr(test_inst, getter_name) and callable(getattr(test_inst, getter_name))
                                            
                                            if not has_getter:
                                                if attr_name == 'typ' and not get_typ_required:
                                                    # get_typ not in required methods: allow missing but render as '?'
                                                    print(f"Hindernis: Getter '{getter_name}' fehlt - wird als '?' gerendert")
                                                    missing_get_typ = True
                                                else:
                                                    # get_x, get_y or required get_typ missing is a validation failure
                                                    print(f"Hindernis: Getter '{getter_name}' fehlt")
                                                    validation_ok = False
                                                    break
                                
                                # Check required methods (excluding getters which were already checked above)
                                if validation_ok:
                                    for method_name in required_methods:
                                        # Skip getters that were already validated with attributes
                                        if method_name.startswith('get_') and method_name[4:] in private_attrs:
                                            continue
                                        if not (hasattr(test_inst, method_name) and callable(getattr(test_inst, method_name))):
                                            print(f"Hindernis: Methode '{method_name}' fehlt")
                                            validation_ok = False
                                            break
                                
                                # Check public attributes
                                if validation_ok:
                                    public_attrs = hindernis_requirements.get('attributes', [])
                                    for attr_name in public_attrs:
                                        if not hasattr(test_inst, attr_name):
                                            print(f"Hindernis: Attribut '{attr_name}' fehlt")
                                            validation_ok = False
                                            break
                                
                                hindernis_class_valid = validation_ok
                                
                                # Store validation result and missing_get_typ flag
                                self._hindernis_class_valid = validation_ok
                                self._hindernis_missing_get_typ = missing_get_typ if validation_ok else False
                    except Exception:
                        HindernisClass = None
                        print("Klasse Hindernis fehlt")
                        self._hindernis_class_valid = False

                class _InternalHindernis:
                    def __init__(self, art, x=None, y=None):
                        self.typ = art
                        self.name = art
                        self.x = x
                        self.y = y
                        self.framework = None
                        # object state expected by framework
                        self.tot = False
                    def ist_passierbar(self):
                        # Default: if student Hindernis class is available and provides
                        # ist_passierbar, defer to it; otherwise legacy behavior (not passierbar)
                        stud = getattr(self, '_student', None)
                        if stud is not None:
                            if hasattr(stud, 'ist_passierbar'):
                                try:
                                    return bool(stud.ist_passierbar())
                                except Exception:
                                    return True
                            else:
                                # student class present but no method -> tile remains passierbar
                                return True
                        # no student class -> legacy: not passierbar
                        return False
                    def attribute_als_text(self):
                        # hide from inspector by returning empty dict
                        return {}
                    def zeichne(self, screen, feldgroesse):
                        # If student class is used and we have a typ override (like '?'), 
                        # render it as an object instead of relying on tiles
                        if hasattr(self, '_student') and self.typ == '?':
                            # Render question mark
                            surf = pygame.Surface((feldgroesse, feldgroesse))
                            surf.fill((200, 200, 200))
                            font = pygame.font.SysFont('Arial', feldgroesse // 2)
                            text = font.render('?', True, (255, 0, 0))
                            text_rect = text.get_rect(center=(feldgroesse // 2, feldgroesse // 2))
                            surf.blit(text, text_rect)
                            screen.blit(surf, (self.x * feldgroesse, self.y * feldgroesse))
                        elif hasattr(self, '_student'):
                            # Student class present - render based on typ
                            try:
                                sprite_map = {'Baum': 'sprites/baum.png', 'Berg': 'sprites/berg.png', 'Busch': 'sprites/busch.png'}
                                from framework.utils import lade_sprite
                                surf = lade_sprite(sprite_map.get(self.typ, 'sprites/baum.png'), feldgroesse)
                                img = pygame.transform.scale(surf, (feldgroesse, feldgroesse))
                                screen.blit(img, (self.x * feldgroesse, self.y * feldgroesse))
                            except Exception:
                                pass
                        # Otherwise: Hindernisse werden vom Level-Tile gerendert by the framework

                for yy, row in enumerate(self.level.tiles):
                    for xx, code in enumerate(row):
                        art = tile_to_type.get(code)
                        if not art:
                            continue
                        obj = None
                        # Prefer student class if present and valid
                        try:
                            if HindernisClass is not None and hindernis_class_valid:
                                # Class exists and passed validation - instantiate
                                try:
                                    student_inst = HindernisClass(xx, yy, art)
                                except TypeError:
                                    try:
                                        student_inst = HindernisClass(art)
                                    except Exception:
                                        try:
                                            student_inst = HindernisClass(self.level, art)
                                        except Exception:
                                            try:
                                                student_inst = HindernisClass(self.level, xx, yy, art)
                                            except Exception:
                                                student_inst = None
                                
                                if student_inst is not None:
                                    obj = student_inst
                                    try:
                                        # do not forcibly set attributes on student object
                                        pass
                                    except Exception:
                                        pass
                                    # attach student marker for passability checks
                                    try:
                                        setattr(obj, '_student_present', True)
                                    except Exception:
                                        pass
                                    # but also keep a small proxy so framework can call ist_passierbar
                                    try:
                                        proxy = _InternalHindernis(art, xx, yy)
                                        proxy._student = obj
                                        # Mark if get_typ is missing (use stored flag or check on instance)
                                        missing_get_typ = getattr(self, '_hindernis_missing_get_typ', False)
                                        if missing_get_typ or not hasattr(obj, 'get_typ') or not callable(getattr(obj, 'get_typ', None)):
                                            proxy._missing_get_typ = True
                                            proxy.typ = '?'  # Override typ for rendering
                                        else:
                                            # Get typ value for rendering (but don't re-validate class)
                                            try:
                                                typ_value = obj.get_typ()
                                                if typ_value in ['Baum', 'Berg', 'Busch']:
                                                    proxy.typ = typ_value
                                                else:
                                                    # Typ value is wrong, but class was already validated
                                                    # This might be a student implementation error (e.g., name mangling)
                                                    # Render as '?' but don't fail validation
                                                    proxy.typ = '?'
                                            except Exception:
                                                proxy.typ = '?'
                                        obj = proxy
                                    except Exception:
                                        # fallback: use student_inst directly
                                        pass
                            elif student_mode_enabled:
                                # Student mode active but class missing/invalid - don't render
                                obj = None
                            else:
                                # No student mode - use framework hindernis
                                obj = _InternalHindernis(art, xx, yy)
                        except Exception as e:
                            # If student mode is enabled, don't fall back to framework hindernis
                            if not student_mode_enabled:
                                obj = _InternalHindernis(art, xx, yy)
                            else:
                                obj = None

                        # Only add object if it's not None
                        if obj is not None:
                            try:
                                obj.x = xx
                                obj.y = yy
                            except Exception:
                                pass
                            try:
                                obj.framework = self.framework
                            except Exception:
                                pass
                            try:
                                # ensure typ/name present for rendering
                                if not hasattr(obj, 'typ'):
                                    # Try to get typ via getter
                                    if hasattr(obj, 'get_typ') and callable(getattr(obj, 'get_typ', None)):
                                        try:
                                            obj.typ = obj.get_typ()
                                        except Exception:
                                            obj.typ = '?'  # Mark as unknown
                                    else:
                                        obj.typ = '?'  # get_typ missing
                                if not hasattr(obj, 'name'):
                                    obj.name = getattr(obj, 'typ', art)
                            except Exception:
                                pass
                            try:
                                self.objekte.append(obj)
                            except Exception:
                                pass
            except Exception:
                pass

        # --- Validate Zettel class (similar to Hindernis validation)
        if not self.rebuild_mode:
            try:
                ZettelClass = None
                zettel_student_mode_enabled = False
                zettel_requirements = self.class_requirements.get('Zettel', {})
                zettel_class_valid = False
                
                # Initialize validation flag (True if not in student mode, False if in student mode until validated)
                self._zettel_class_valid = True  # Default: valid if no requirements
                
                # Check if student mode is enabled for Zettel
                if zettel_requirements:
                    # Check explicit load flags OR if requirements configured (same logic as Hindernis)
                    prefer_schueler = bool(zettel_requirements.get('load_from_schueler', False))
                    prefer_klassen = bool(zettel_requirements.get('load_from_klassen', False))
                    has_methods = bool(zettel_requirements.get('methods', []))
                    has_attrs = bool(zettel_requirements.get('attributes', []))
                    has_inheritance = zettel_requirements.get('inherits') and zettel_requirements.get('inherits') != 'None'
                    
                    zettel_student_mode_enabled = prefer_schueler or prefer_klassen or has_methods or has_attrs or has_inheritance
                    if zettel_student_mode_enabled:
                        self._zettel_class_valid = False  # Will be set to True if validation passes
                
                # Try to get student Zettel class and validate it ONCE
                if zettel_student_mode_enabled:
                    try:
                        ZettelClass = self._get_entity_class('Zettel', None)
                        if ZettelClass is None:
                            print("Klasse Zettel fehlt")
                        else:
                            # Validate class requirements ONCE (not per instance)
                            # Create a temporary instance to test validation
                            try:
                                test_inst = ZettelClass(0, 0)
                            except Exception:
                                test_inst = None
                            
                            if test_inst is not None:
                                validation_ok = True
                                can_render = True  # Can render if x,y are present
                                
                                # Get required methods list
                                required_methods = zettel_requirements.get('methods', [])
                                
                                # Check private attributes - check in parent class hierarchy
                                private_attrs = zettel_requirements.get('attributes_private', {})
                                for attr_name, required in private_attrs.items():
                                    if required:
                                        # Try to find the attribute in the class hierarchy
                                        # Check both own class and parent class name mangling
                                        found = False
                                        for cls in ZettelClass.__mro__:
                                            mangled_name = f"_{cls.__name__}__{attr_name}"
                                            if hasattr(test_inst, mangled_name):
                                                found = True
                                                break
                                        
                                        # Also check if attribute is public (which would be wrong)
                                        has_public = hasattr(test_inst, attr_name) and not attr_name.startswith('_')
                                        
                                        if not found or has_public:
                                            print(f"Zettel: Attribut '{attr_name}' muss privat sein")
                                            validation_ok = False
                                            # Check if it's x or y - if so, can't render
                                            if attr_name in ('x', 'y'):
                                                can_render = False
                                            break
                                        
                                        # Check getter
                                        getter_name = f'get_{attr_name}'
                                        has_getter = hasattr(test_inst, getter_name) and callable(getattr(test_inst, getter_name))
                                        
                                        if not has_getter:
                                            print(f"Zettel: Getter '{getter_name}' fehlt")
                                            validation_ok = False
                                            # For x,y getters: can't render. For typ,spruch: can still render
                                            if attr_name in ('x', 'y'):
                                                can_render = False
                                            break
                                
                                # Check required methods (excluding getters which were already checked above)
                                if validation_ok:
                                    for method_name in required_methods:
                                        # Skip getters that were already validated with attributes
                                        if method_name.startswith('get_') and method_name[4:] in private_attrs:
                                            continue
                                        # Skip setters for private attributes (already covered)
                                        if method_name.startswith('set_') and method_name[4:] in private_attrs:
                                            setter_attr = method_name[4:]
                                            has_setter = hasattr(test_inst, method_name) and callable(getattr(test_inst, method_name))
                                            if not has_setter:
                                                print(f"Zettel: Setter '{method_name}' fehlt")
                                                validation_ok = False
                                                break
                                            continue
                                        if not (hasattr(test_inst, method_name) and callable(getattr(test_inst, method_name))):
                                            print(f"Zettel: Methode '{method_name}' fehlt")
                                            validation_ok = False
                                            break
                                
                                # Check public attributes
                                if validation_ok:
                                    public_attrs = zettel_requirements.get('attributes', [])
                                    for attr_name in public_attrs:
                                        if not hasattr(test_inst, attr_name):
                                            print(f"Zettel: Attribut '{attr_name}' fehlt")
                                            validation_ok = False
                                            break
                                
                                zettel_class_valid = validation_ok
                                
                                # Store validation result
                                self._zettel_class_valid = validation_ok
                                self._zettel_can_render = can_render  # Can render if x,y are accessible
                    except Exception:
                        ZettelClass = None
                        print("Klasse Zettel fehlt")
                        self._zettel_class_valid = False
                
                # Store Zettel class and student mode flag for later use in spawning
                self._ZettelClass = ZettelClass
                self._zettel_student_mode_enabled = zettel_student_mode_enabled
                
            except Exception:
                self._zettel_class_valid = True  # Default: valid if no validation configured
                self._zettel_can_render = True
                self._ZettelClass = None
                self._zettel_student_mode_enabled = False

        # --- Validate Knappe class before spawning (Phase 2 support)
        # Similar to Hindernis validation above
        try:
            KnappeClass = None
            knappe_student_mode_enabled = False
            knappe_requirements = self.class_requirements.get('Knappe', {})
            knappe_class_valid = False
            
            # Initialize validation flag
            self._knappe_class_valid = True  # Default: valid if no requirements
            
            # Check if classes_present is enabled
            classes_present_mode = self.victory_settings.get('classes_present', False)
            
            # Check if student mode is enabled for Knappe
            if knappe_requirements:
                prefer_schueler = bool(knappe_requirements.get('load_from_schueler', False))
                prefer_klassen = bool(knappe_requirements.get('load_from_klassen', False))
                has_methods = bool(knappe_requirements.get('methods', []))
                has_attrs = bool(knappe_requirements.get('attributes', []))
                has_inheritance = knappe_requirements.get('inherits') and knappe_requirements.get('inherits') != 'None'
                
                knappe_student_mode_enabled = prefer_schueler or prefer_klassen or has_methods or has_attrs or has_inheritance
                if knappe_student_mode_enabled:
                    self._knappe_class_valid = False  # Will be set to True if validation passes
            elif classes_present_mode:
                # classes_present is true but no Knappe requirements:
                # Check if Charakter is implemented - if yes, try to load Knappe (may inherit from it)
                charakter_req = self.class_requirements.get('Charakter', {})
                if charakter_req.get('check_implementation', False):
                    # Charakter is implemented, try to load Knappe as it may inherit from Charakter
                    knappe_student_mode_enabled = True
                    self._knappe_class_valid = False  # Will be validated below
                # else: No Charakter and no Knappe requirements - use framework implementation
                # knappe_student_mode_enabled remains False
            
            # Try to get student Knappe class and validate it
            if knappe_student_mode_enabled:
                try:
                    KnappeClass = self._get_entity_class('Knappe', None)
                    if KnappeClass is None:
                        print("Klasse Knappe fehlt")
                    else:
                        # Validate class requirements
                        # Try to create test instance with minimal signature
                        try:
                            test_inst = KnappeClass(0, 0, 'OBEN')
                        except Exception:
                            try:
                                test_inst = KnappeClass(self.level, 0, 0, 'OBEN')
                            except Exception:
                                try:
                                    test_inst = KnappeClass(self.framework, 0, 0, 'OBEN')
                                except Exception:
                                    test_inst = None
                        
                        if test_inst is not None:
                            validation_ok = True
                            
                            # Check private attributes
                            private_attrs = knappe_requirements.get('attributes_private', {})
                            for attr_name, required in private_attrs.items():
                                if required:
                                    # Check in class hierarchy
                                    found = False
                                    for cls in KnappeClass.__mro__:
                                        mangled_name = f"_{cls.__name__}__{attr_name}"
                                        if hasattr(test_inst, mangled_name):
                                            found = True
                                            break
                                    
                                    has_public = hasattr(test_inst, attr_name) and not attr_name.startswith('_')
                                    
                                    if not found or has_public:
                                        print(f"Knappe: Attribut '{attr_name}' muss privat sein")
                                        validation_ok = False
                                        break
                            
                            # Check getters
                            if validation_ok and private_attrs:
                                for attr_name, required in private_attrs.items():
                                    if required:
                                        getter_name = f'get_{attr_name}'
                                        has_getter = hasattr(test_inst, getter_name) and callable(getattr(test_inst, getter_name))
                                        
                                        if not has_getter:
                                            print(f"Knappe: Getter '{getter_name}' fehlt")
                                            validation_ok = False
                                            break
                            
                            # Check required methods
                            if validation_ok:
                                required_methods = knappe_requirements.get('methods', [])
                                for method_name in required_methods:
                                    # Skip getters already validated
                                    if method_name.startswith('get_') and method_name[4:] in private_attrs:
                                        continue
                                    if not (hasattr(test_inst, method_name) and callable(getattr(test_inst, method_name))):
                                        print(f"Knappe: Methode '{method_name}' fehlt")
                                        validation_ok = False
                                        break
                            
                            # Check public attributes
                            if validation_ok:
                                public_attrs = knappe_requirements.get('attributes', [])
                                for attr_name in public_attrs:
                                    if not hasattr(test_inst, attr_name):
                                        print(f"Knappe: Attribut '{attr_name}' fehlt")
                                        validation_ok = False
                                        break
                            
                            knappe_class_valid = validation_ok
                            self._knappe_class_valid = validation_ok
                except Exception:
                    KnappeClass = None
                    print("Klasse Knappe fehlt")
                    self._knappe_class_valid = False
            
            # Store Knappe class and student mode flag
            self._KnappeClass = KnappeClass
            self._knappe_student_mode_enabled = knappe_student_mode_enabled
            
        except Exception:
            self._knappe_class_valid = True
            self._KnappeClass = None
            self._knappe_student_mode_enabled = False

        for typ, x, y, sichtbar in self.level.iter_entity_spawns():
            # Skip entity spawning in rebuild mode
            if self.rebuild_mode:
                continue
                
            t = typ.lower() if isinstance(typ, str) else typ
            # Lese Richtung (default "down")
            richt = orients.get(f"{x},{y}", "down")

            if t == "p":
                # Phase 2: Check if student Held class is requested via class_requirements
                FrameworkHeld = Held
                cls = self._get_entity_class("Held", FrameworkHeld)
                
                # Check if student mode is enabled for Held via class_requirements
                req = self.class_requirements.get("Held", {})
                student_mode_for_held = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
                
                if student_mode_for_held:
                    # Student mode enabled for Held - different behavior required
                    if cls is None or cls == FrameworkHeld:
                        # Student class not found or couldn't be loaded
                        print("[FEHLER] Helden Klasse fehlt")
                        self.held = None
                        # Don't render anything, don't add to objekte
                        continue
                    
                    # Try to instantiate student Held with signature: (x, y, richtung, weiblich)
                    # Note: Level is NOT passed in constructor, will be added later via setze_level()
                    student_inst = None
                    try:
                        weiblich = getattr(self.framework, "weiblich", False)
                        student_inst = cls(x, y, richt, weiblich)
                    except TypeError as e:
                        # Wrong constructor signature
                        print(f"[FEHLER] Helden Klasse: Parameterliste nicht korrekt ({e})")
                        self.held = None
                        continue
                    except Exception as e:
                        # Other instantiation error
                        print(f"[FEHLER] Helden Klasse kann nicht instanziert werden: {e}")
                        self.held = None
                        continue
                    
                    if student_inst is None:
                        print("[FEHLER] Helden Klasse: Instanzierung fehlgeschlagen")
                        self.held = None
                        continue
                    
                    # Check which attributes the student set (or provides via getter methods)
                    # For each attribute, check direct access OR getter method
                    def has_attribute_or_getter(obj, attr_name):
                        """Check if object has attribute directly or via get_<attr> method"""
                        # Try direct access first
                        if hasattr(obj, attr_name):
                            return True
                        # Try getter method
                        getter_name = f'get_{attr_name}'
                        if hasattr(obj, getter_name):
                            getter = getattr(obj, getter_name)
                            if callable(getter):
                                return True
                        return False
                    
                    has_x = has_attribute_or_getter(student_inst, 'x')
                    has_y = has_attribute_or_getter(student_inst, 'y')
                    has_richtung = has_attribute_or_getter(student_inst, 'richtung')
                    has_weiblich = has_attribute_or_getter(student_inst, 'weiblich')
                    
                    # Store student instance wrapped in MetaHeld for framework integration
                    from .held import MetaHeld
                    self.held = MetaHeld(self.framework, student_inst, x, y, richt, weiblich=getattr(self.framework, "weiblich", False))
                    
                    # Mark the held with information about what's missing/present
                    # This will be used for rendering and victory checking
                    setattr(self.held, '_student_mode', True)
                    setattr(self.held, '_level_expected_x', x)
                    setattr(self.held, '_level_expected_y', y)
                    setattr(self.held, '_level_expected_richtung', richt)
                    setattr(self.held, '_class_requirements', req)
                    
                    # Set allowed getters based on class_requirements methods
                    # This enforces level-specific access control (e.g., Level 40 has no getters, Level 43 has all)
                    if req and 'methods' in req:
                        allowed_getters = set(req['methods'])
                        setattr(self.held, '_allowed_getters', allowed_getters)
                    else:
                        setattr(self.held, '_allowed_getters', None)  # No restrictions
                    
                    # Check if student's position matches level expectation and warn if not
                    if has_x and has_y:
                        # Try to get position via direct access or getter
                        def get_attribute_value(obj, attr_name, default=None):
                            """Get attribute value directly or via get_<attr> method"""
                            try:
                                return getattr(obj, attr_name)
                            except AttributeError:
                                # Try getter method
                                getter_name = f'get_{attr_name}'
                                if hasattr(obj, getter_name):
                                    getter = getattr(obj, getter_name)
                                    if callable(getter):
                                        try:
                                            return getter()
                                        except Exception:
                                            pass
                                return default
                        
                        student_x = get_attribute_value(student_inst, 'x', None)
                        student_y = get_attribute_value(student_inst, 'y', None)
                        if student_x is not None and student_y is not None and (student_x != x or student_y != y):
                            print(f"[WARNUNG] Held ist an Position ({student_x}, {student_y}), "
                                  f"aber Level erwartet ({x}, {y}). Level kann nicht abgeschlossen werden.")
                    
                    # Check if critical attributes are present for rendering
                    if has_x and has_y and has_richtung and not has_weiblich:
                        # Show red question mark sprite instead of hero
                        setattr(self.held, '_show_error_sprite', True)
                    elif not (has_x and has_y and has_richtung):
                        # Some critical attributes missing - don't render at all, but keep in inspector
                        setattr(self.held, '_dont_render', True)
                    
                    # Add Level reference via set_level() if configured
                    expects_set_level = req.get("expects_set_level", False) if req else False
                    if expects_set_level:
                        # New way: Call set_level(spielfeld) - student implements this method
                        if hasattr(student_inst, 'set_level') and callable(getattr(student_inst, 'set_level')):
                            try:
                                student_inst.set_level(self)
                            except Exception as e:
                                print(f"[WARNUNG] Fehler beim Aufruf von Held.set_level(): {e}")
                    else:
                        # Legacy way: Try setze_level() for backwards compatibility
                        if hasattr(student_inst, 'setze_level'):
                            try:
                                student_inst.setze_level(self)
                            except Exception:
                                pass
                    
                else:
                    # Legacy mode: Use framework Held
                    try:
                        self.held = FrameworkHeld(self.framework, x, y, richt, weiblich=getattr(self.framework, "weiblich", False))
                    except Exception:
                        raise

                # Only append the hero object if it was actually created.
                if getattr(self, 'held', None) is not None:
                    self.objekte.append(self.held)
                if sichtbar:
                    import framework.grundlage as grundlage
                    setattr(grundlage, self.held.typ.lower(), self.held)

            elif t == "h":
                cls = self._get_entity_class("Herz", Herz)
                if student_mode_enabled and cls is None:
                    # level explicitly requests student classes but none provided for Herz
                    continue
                try:
                    obj = cls(x, y)
                except Exception:
                    obj = Herz(x, y)
                obj.framework = self.framework
                cfg = self.settings.get(obj.typ, {})
                self.objekte.append(obj)
                if sichtbar:
                    import framework.grundlage as grundlage
                    setattr(grundlage, obj.typ.lower(), obj)

            elif t == "x":
                n = self.generate_orc_name()
                while n in self.orc_names:
                    n = self.generate_orc_name()
                self.orc_names.append(n)
                cls = self._get_entity_class("Monster", Monster)
                if student_mode_enabled and cls is None:
                    continue
                try:
                    m = cls(x, y, name=n)
                except Exception:
                    m = Monster(x, y, name=n)
                m.framework = self.framework
                # setze Richtung falls unterstützt
                try:
                    m.richtung = richt
                except Exception:
                    pass
                
                # Call set_level() if configured
                monster_req = self.class_requirements.get('Monster', {})
                expects_set_level = monster_req.get("expects_set_level", False) if monster_req else False
                if expects_set_level and hasattr(m, 'set_level') and callable(getattr(m, 'set_level')):
                    try:
                        m.set_level(self)
                    except Exception as e:
                        print(f"[WARNUNG] Fehler beim Aufruf von Monster.set_level(): {e}")
                
                self.objekte.append(m)
                if sichtbar:
                    import framework.grundlage as grundlage
                    setattr(grundlage, m.typ.lower(), m)

            elif t == "y":
                # Bogenschuetze (ranged monster)
                n = self.generate_orc_name()
                while n in self.orc_names:
                    n = self.generate_orc_name()
                self.orc_names.append(n)
                cls = self._get_entity_class("Bogenschuetze", Bogenschuetze)
                if student_mode_enabled and cls is None:
                    continue
                try:
                    m = cls(x, y, name=n)
                except Exception:
                    m = Bogenschuetze(x, y, name=n)
                m.framework = self.framework
                try:
                    m.richtung = richt
                except Exception:
                    pass
                
                # Call set_level() if configured
                bogenschuetze_req = self.class_requirements.get('Bogenschuetze', {})
                expects_set_level = bogenschuetze_req.get("expects_set_level", False) if bogenschuetze_req else False
                if expects_set_level and hasattr(m, 'set_level') and callable(getattr(m, 'set_level')):
                    try:
                        m.set_level(self)
                    except Exception as e:
                        print(f"[WARNUNG] Fehler beim Aufruf von Bogenschuetze.set_level(): {e}")
                
                self.objekte.append(m)
                if sichtbar:
                    import framework.grundlage as grundlage
                    setattr(grundlage, "bogenschuetze", m)

            elif t == "c":
                # Check if Zettel class is configured, otherwise use Code
                use_zettel_class = getattr(self, '_zettel_student_mode_enabled', False)
                zettel_can_render = getattr(self, '_zettel_can_render', True)
                
                if use_zettel_class and getattr(self, '_ZettelClass', None) is not None:
                    # Use student Zettel class - render if x,y are accessible
                    if zettel_can_render:
                        try:
                            code = self._ZettelClass(x, y)
                            code.framework = self.framework
                            
                            # Ensure x, y are accessible as properties (not just via getters)
                            if not hasattr(code, 'x'):
                                if hasattr(code, 'get_x') and callable(getattr(code, 'get_x', None)):
                                    try:
                                        code.x = code.get_x()
                                    except Exception:
                                        code.x = x
                            if not hasattr(code, 'y'):
                                if hasattr(code, 'get_y') and callable(getattr(code, 'get_y', None)):
                                    try:
                                        code.y = code.get_y()
                                    except Exception:
                                        code.y = y
                            
                            # Ensure typ is accessible for rendering
                            if not hasattr(code, 'typ'):
                                # Try to get typ via getter
                                if hasattr(code, 'get_typ') and callable(getattr(code, 'get_typ', None)):
                                    try:
                                        code.typ = code.get_typ()
                                    except Exception:
                                        code.typ = 'Zettel'  # Default
                                else:
                                    code.typ = 'Zettel'  # Default if no getter
                            
                            self.objekte.append(code)
                            if sichtbar:
                                import framework.grundlage as grundlage
                                setattr(grundlage, "zettel", code)
                        except Exception:
                            # Failed to create Zettel - skip
                            pass
                    # else: Zettel class can't render (x,y not accessible) - don't spawn
                elif use_zettel_class:
                    # Zettel class required but not found - don't spawn
                    pass
                else:
                    # Use framework Code class
                    cls = self._get_entity_class("Code", Code)
                    if student_mode_enabled and cls is None:
                        continue
                    try:
                        code = cls(x, y, c=self.zufallscode)
                    except Exception:
                        code = Code(x, y, c=self.zufallscode)
                    code.framework = self.framework
                    self.objekte.append(code)
                    if sichtbar:
                        import framework.grundlage as grundlage
                        setattr(grundlage, "zettel", code)

            elif t == "d":
                # prüfe, ob für diese Position eine Farbe konfiguriert ist (ggf. überschrieben durch random)
                color = colors_override.get(f"{x},{y}")
                # Wenn color gesetzt, erstelle farbige, schlüssel-verschlossene Tür
                cls = self._get_entity_class("Tuer", Tuer)
                if student_mode_enabled and cls is None:
                    continue
                try:
                    if color:
                        tuer = cls(x, y, code=None, color=color)
                    else:
                        tuer = cls(x, y, code=self.zufallscode)
                except Exception:
                    if color:
                        tuer = Tuer(x, y, code=None, color=color)
                    else:
                        tuer = Tuer(x, y, code=self.zufallscode)
                tuer.framework = self.framework
                self.objekte.append(tuer)
                # setze Richtung falls das Tür-Objekt diese Eigenschaft nutzt
                try:
                    tuer.richtung = richt
                except Exception:
                    pass
                if sichtbar:
                    import framework.grundlage as grundlage
                    setattr(grundlage, "tuer", tuer)

            elif t == "s":
                # Schlüssel-Spawn: Farbe aus settings oder default 'green' (ggf. überschrieben durch random)
                color = colors_override.get(f"{x},{y}", "green")
                cls = self._get_entity_class("Schluessel", Schluessel)
                if student_mode_enabled and cls is None:
                    continue
                try:
                    sch = cls(x, y, color=color)
                except Exception:
                    sch = Schluessel(x, y, color=color)
                sch.framework = self.framework
                self.objekte.append(sch)
                if sichtbar:
                    import framework.grundlage as grundlage
                    # früher wurde 'zettel'/'tuer' etc. genutzt; hier verwenden wir 'schluessel' singular
                    setattr(grundlage, "schluessel", sch)

            elif t == "v":
                # Villager (Dorfbewohner) – gender kann in settings konfiguriert sein
                key = f"{x},{y}"
                weiblich_flag = False
                val = villagers.get(key)
                if isinstance(val, str) and val.lower() in ("female", "weiblich", "w"):
                    weiblich_flag = True
                try:
                    from .villager import Villager
                    cls = self._get_entity_class("Villager", Villager)
                    if student_mode_enabled and cls is None:
                        continue
                    try:
                        vill = cls(self.framework, x, y, richtung=richt, weiblich=weiblich_flag)
                    except Exception:
                        vill = Villager(self.framework, x, y, richtung=richt, weiblich=weiblich_flag)
                    vill.framework = self.framework
                    
                    # Call set_level() if configured
                    villager_req = self.class_requirements.get('Villager', {})
                    expects_set_level = villager_req.get("expects_set_level", False) if villager_req else False
                    if expects_set_level and hasattr(vill, 'set_level') and callable(getattr(vill, 'set_level')):
                        try:
                            vill.set_level(self)
                        except Exception as e:
                            print(f"[WARNUNG] Fehler beim Aufruf von Villager.set_level(): {e}")
                    
                    self.objekte.append(vill)
                    # If quest mode==items, populate villager with random offers (2-5 items, 10-80 Gold)
                    if isinstance(quest_mode, str) and quest_mode.lower() == 'items':
                        offer_count = random.randint(2, 5)
                        for _ in range(offer_count):
                            item_name = random.choice(ITEM_NAMES)
                            price = random.randint(10, 80)
                            try:
                                item = Gegenstand(item_name, price)
                                vill.biete_item_an(item, price)
                            except Exception:
                                pass
                    spawned_villagers.append(vill)
                    if sichtbar:
                        import framework.grundlage as grundlage
                        setattr(grundlage, "villager", vill)
                except Exception:
                    pass

            elif t == "q":
                # Questgeber spawn
                key = f"{x},{y}"
                qcfg = quests.get(key, {})
                modus = qcfg.get("modus", "items")
                wuensche = qcfg.get("wuensche", [])
                anzahl = qcfg.get("anzahl", None)
                # weiblich flag may be in villagers settings
                weiblich_flag = False
                val = villagers.get(key)
                if isinstance(val, str) and val.lower() in ("female", "weiblich", "w"):
                    weiblich_flag = True
                try:
                    from .villager import Questgeber
                    # If global quest_mode is 'raetsel' and no explicit puzzle provided in qcfg,
                    # generate a simple arithmetic puzzle here and attach it to the Questgeber.
                    initial_raetsel = None
                    if isinstance(quest_mode, str) and quest_mode.lower() == 'raetsel':
                        # generate a question 'a op b=' where a,b in 1..9 and op in +,-,*,/
                        ops = ['+', '-', '*', '/']
                        attempt = 0
                        while attempt < 50:
                            a = random.randint(1, 9)
                            b = random.randint(1, 9)
                            op = random.choice(ops)
                            if op == '/':
                                if b == 0:
                                    attempt += 1
                                    continue
                                if a % b != 0:
                                    attempt += 1
                                    continue
                                sol = a // b
                            elif op == '+':
                                sol = a + b
                            elif op == '-':
                                sol = a - b
                            else:
                                sol = a * b
                            initial_raetsel = (f"{a}{op}{b}=", sol)
                            break
                    cls = self._get_entity_class("Questgeber", Questgeber)
                    if student_mode_enabled and cls is None:
                        continue
                    try:
                        quest = cls(self.framework, x, y, richtung=richt, modus=modus, wuensche=wuensche, anzahl_items=anzahl, weiblich=weiblich_flag)
                    except Exception:
                        quest = Questgeber(self.framework, x, y, richtung=richt, modus=modus, wuensche=wuensche, anzahl_items=anzahl, weiblich=weiblich_flag)
                    # Ensure the Questgeber uses the dedicated quest sprite if available
                    try:
                        quest.sprite_pfad = "sprites/villager_quest.png"
                        # preload the image into .bild to make drawing deterministic
                        try:
                            quest.bild = lade_sprite(quest.sprite_pfad, self.feldgroesse)
                        except Exception:
                            # fallback: try without size
                            try:
                                quest.bild = lade_sprite(quest.sprite_pfad)
                            except Exception:
                                pass
                    except Exception:
                        pass
                    # attach generated puzzle if present
                    if initial_raetsel is not None:
                        try:
                            quest._vorgegebene_frage = initial_raetsel[0]
                            quest._letzte_raetsel = int(initial_raetsel[1])
                        except Exception:
                            pass
                    quest.framework = self.framework
                    # set explicit type for drawing/lookup
                    try:
                        quest.typ = "Questgeber"
                    except Exception:
                        pass
                    self.objekte.append(quest)
                    if sichtbar:
                        import framework.grundlage as grundlage
                        setattr(grundlage, "questgeber", quest)
                except Exception:
                    pass

            elif t == "g":
                cls = self._get_entity_class("Tor", Tor)
                if student_mode_enabled and cls is None:
                    continue
                try:
                    tor = cls(x, y, offen=False)
                except Exception:
                    tor = Tor(x, y, offen=False)
                tor.framework = self.framework
                self.objekte.append(tor)
                if sichtbar:
                    import framework.grundlage as grundlage
                    setattr(grundlage, "tor", tor)

            elif t == "k":
                # Check if Knappe should be spawned (based on validation done before loop)
                knappe_student_mode = getattr(self, '_knappe_student_mode_enabled', False)
                knappe_valid = getattr(self, '_knappe_class_valid', True)
                
                # Skip spawning if student mode is active but class is invalid/missing
                if knappe_student_mode and not knappe_valid:
                    continue
                
                # Get Knappe class (prefer pre-validated class)
                cls = getattr(self, '_KnappeClass', None)
                if cls is None:
                    cls = self._get_entity_class("Knappe", Knappe)
                
                # Old global student_mode_enabled check (for Phase 1 compatibility)
                if student_mode_enabled and cls is None:
                    continue
                
                # Instantiate student-provided Knappe if available.
                # Important: student classes often expect a Level object as first
                # argument (their API). The framework historically passed the
                # Framework instance and a generated name. To avoid forcing the
                # student to accept a random name, we try several constructor
                # signatures in a safe order and avoid passing the auto-generated
                # name to student classes. If all attempts fail, fall back to
                # the framework's Knappe implementation (which still receives
                # the generated name).
                try:
                    inst = None
                    if cls is not None:
                        # If cls is the framework Knappe, use the correct framework signature
                        if cls is Knappe:
                            inst = Knappe(self.framework, x, y, richt, name=self.generate_knappe_name())
                        else:
                            # Try various student class signatures
                            # Try: student wants (x, y, richtung) - Level 46 style (no weiblich)
                            try:
                                inst = cls(x, y, richt)
                            except Exception:
                                inst = None
                            # Try: student wants (x, y, richtung, weiblich) - older style
                            if inst is None:
                                try:
                                    weiblich = getattr(self.framework, "weiblich", False)
                                    inst = cls(x, y, richt, weiblich)
                                except Exception:
                                    inst = None
                            # Try: student wants Level as first arg
                            if inst is None:
                                try:
                                    inst = cls(self.level, x, y, richt)
                                except Exception:
                                    inst = None
                            # Try: student wants Framework as first arg
                            if inst is None:
                                try:
                                    inst = cls(self.framework, x, y, richt)
                                except Exception:
                                    inst = None
                            # Try other common variant: level + kwargs (no name)
                            if inst is None:
                                try:
                                    inst = cls(self.level, x, y, richt, **{})
                                except Exception:
                                    inst = None
                    if inst is not None:
                        self.knappe = inst
                    elif not knappe_student_mode:
                        # Only use framework fallback if NOT in student mode
                        self.knappe = Knappe(self.framework, x, y, richt, name=self.generate_knappe_name())
                    else:
                        # Student mode active but no valid class - don't spawn
                        self.knappe = None
                except Exception:
                    # If anything unexpected fails, only spawn framework Knappe if NOT in student mode
                    if not knappe_student_mode:
                        try:
                            self.knappe = Knappe(self.framework, x, y, richt, name=self.generate_knappe_name())
                        except Exception:
                            self.knappe = None
                    else:
                        self.knappe = None
                
                # Only add to objekte if knappe was created
                if self.knappe is not None:
                    # Call set_level() if configured
                    knappe_req = self.class_requirements.get('Knappe', {})
                    expects_set_level = knappe_req.get("expects_set_level", False) if knappe_req else False
                    if expects_set_level and hasattr(self.knappe, 'set_level') and callable(getattr(self.knappe, 'set_level')):
                        try:
                            self.knappe.set_level(self)
                        except Exception as e:
                            print(f"[WARNUNG] Fehler beim Aufruf von Knappe.set_level(): {e}")
                    
                    self.objekte.append(self.knappe)
                    if sichtbar:
                        import framework.grundlage as grundlage
                        setattr(grundlage, "knappe", self.knappe)
                    # If a hero was already spawned, attach this Knappe to the hero immediately.
                    try:
                        if getattr(self, 'held', None) is not None:
                            # Ensure the held has a knappen list
                            if not hasattr(self.held, 'knappen'):
                                try:
                                    setattr(self.held, 'knappen', [])
                                except Exception:
                                    pass
                            try:
                                self.held.add_knappe(self.knappe)
                            except Exception:
                                pass
                    except Exception:
                        pass

        # Extract level number from filename for display
        try:
            import re
            match = re.search(r'level(\d+)', self.levelfile)
            level_num = match.group(1) if match else "?"
            print(f"Level {level_num} erfolgreich geladen.")
        except Exception:
            print("Level erfolgreich geladen.")
        # After spawning, set initial hero gold and, if in item-quest mode, distribute desired items to villagers
        try:
            if hasattr(self, 'held') and self.held is not None:
                self.held.gold = initial_gold
        except Exception:
            pass

        # --- Apply privacy settings per-object immediately after spawn ---
        try:
            # Provide a best-effort pass that enforces per-type 'public'/'privat' settings
            for o in list(self.objekte):
                try:
                    typ_name = getattr(o, 'typ', None)
                except Exception:
                    try:
                        typ_name = o.__class__.__name__
                    except Exception:
                        typ_name = None
                cfg = {}
                try:
                    if isinstance(self.settings, dict) and typ_name:
                        cfg = self.settings.get(typ_name, {}) or {}
                except Exception:
                    cfg = {}

                is_private = False
                try:
                    if 'public' in cfg:
                        is_private = (cfg.get('public') is False)
                    elif 'privat' in cfg:
                        is_private = bool(cfg.get('privat'))
                except Exception:
                    is_private = False

                if not is_private:
                    continue

                # If object exposes set_privatmodus, call it; otherwise replace with proxy
                try:
                    if hasattr(o, 'set_privatmodus'):
                        try:
                            o.set_privatmodus(True)
                        except Exception:
                            pass
                    else:
                        proxy = self._privatisiere(o)
                        try:
                            idx = self.objekte.index(o)
                            self.objekte[idx] = proxy
                        except ValueError:
                            pass
                        try:
                            if getattr(self, 'held', None) is o:
                                self.held = proxy
                        except Exception:
                            pass
                        try:
                            if getattr(self, 'knappe', None) is o:
                                self.knappe = proxy
                        except Exception:
                            pass
                        try:
                            import framework.grundlage as grundlage
                            for name in ('held','knappe','zettel','tuer','schluessel','villager','tor'):
                                try:
                                    if getattr(grundlage, name, None) is o:
                                        setattr(grundlage, name, proxy)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

    # --- Student-class override helpers ---
    def _get_entity_class(self, canonical_name: str, framework_cls):
        """Try to load a student-provided class according to level settings.

        Behavior (Phase 2 with class_requirements support):
        - If class_requirements exists for this canonical_name:
            * For Held: check load_from_schueler/load_from_klassen flags
            * For other classes: check if any methods/attributes configured (indicates student class)
        - If no class_requirements or no student class requested, fall back to old logic:
            * If 'import_pfad' provided, try that
            * If 'use_student_module' is True, use editor flags
        - If no student flags are present, return the framework class.
        
        Returning None signals the caller that student classes were enabled but none found; callers
        can decide whether to fall back to framework classes (we will for most entities) or to
        omit the entity (special-case: Held when student mode is on should not fall back).
        """
        try:
            settings = self.settings or {}
            
            # Phase 2: Check class_requirements first (new F4 menu configuration)
            class_reqs = getattr(self, 'class_requirements', {}) or {}
            req = class_reqs.get(canonical_name, {})
            
            # Determine if student class should be loaded based on class_requirements
            load_student_from_requirements = False
            prefer_schueler = False
            prefer_klassen = False
            
            if req:
                # For Held: explicit load flags
                if canonical_name == "Held":
                    prefer_schueler = bool(req.get('load_from_schueler', False))
                    prefer_klassen = bool(req.get('load_from_klassen', False))
                    load_student_from_requirements = prefer_schueler or prefer_klassen
                else:
                    # For other classes: check explicit load flags OR if methods/attributes configured
                    prefer_schueler = bool(req.get('load_from_schueler', False))
                    prefer_klassen = bool(req.get('load_from_klassen', False))
                    has_methods = bool(req.get('methods', []))
                    has_attrs = bool(req.get('attributes', []))
                    has_inheritance = req.get('inherits') and req.get('inherits') != 'None'
                    
                    # Load student class if explicitly requested OR if requirements configured
                    load_student_from_requirements = prefer_schueler or prefer_klassen or has_methods or has_attrs or has_inheritance
                    
                    # Determine source: prioritize explicit flags, fallback to klassen/ if requirements present
                    if not (prefer_schueler or prefer_klassen) and (has_methods or has_attrs or has_inheritance):
                        prefer_klassen = True

            # If an explicit import path is provided, prefer it (backwards-compatible)
            import_pfad = None
            try:
                import_pfad = settings.get('import_pfad')
            except Exception:
                import_pfad = None

            use_student_flag = bool(settings.get('use_student_module', False))
            subfolder_flag = bool(settings.get('student_classes_in_subfolder', False))

            # If nothing requests student classes (neither explicit import path nor
            # the student flags nor class_requirements), return the framework class.
            if not import_pfad and not (use_student_flag or subfolder_flag) and not load_student_from_requirements:
                return framework_cls

            # Helper: import module with caching per module name
            if not hasattr(self, '_student_module_cache'):
                self._student_module_cache = {}
            
            # Define repo_root once for use in try_import
            repo_root = os.path.dirname(os.path.dirname(__file__))

            def try_import(candidates, required_class_name=None):
                """Try to load candidate modules, but only return a module that
                actually contains the required_class_name (if provided). This
                prevents returning an earlier module (e.g. `schueler`) that was
                loaded but does not define the requested class while a later
                candidate (e.g. `klassen.held`) does.
                """
                for cand in candidates:
                    if cand in self._student_module_cache:
                        mod = self._student_module_cache.get(cand)
                        # if we have a cached module but a required class name is
                        # given, ensure the module actually defines it
                        if mod and required_class_name:
                            if getattr(mod, required_class_name, None) is None:
                                # cached module doesn't have the class -> continue
                                continue
                        return mod
                    # If candidate corresponds to a file in the repo, prefer a
                    # safe loader that executes only imports, class and function
                    # definitions to avoid running top-level student scripts.
                    try:
                        # helper to safely load only definitions from a file
                        def _safe_load_from_path(path, mod_name=None):
                            try:
                                src = open(path, 'r', encoding='utf-8').read()
                                tree = ast.parse(src, path)
                                new_nodes = []
                                for node in tree.body:
                                    # keep function and class defs, and simple assignments
                                    # but avoid executing imports that pull in framework internals
                                    # (e.g. `from framework.grundlage import *`) which would
                                    # expose framework classes into the student module namespace.
                                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                        new_nodes.append(node)
                                    elif isinstance(node, ast.Import):
                                        # keep only imports that don't import from the 'framework' package
                                        keep = True
                                        for alias in node.names:
                                            if alias.name.startswith('framework'):
                                                keep = False
                                                break
                                        if keep:
                                            new_nodes.append(node)
                                    elif isinstance(node, ast.ImportFrom):
                                        # Skip imports from framework package to avoid pollution
                                        modname = getattr(node, 'module', '') or ''
                                        if modname.startswith('framework'):
                                            continue
                                        # Allow `from ... import *` for student classes (e.g., from spielobjekt import *)
                                        # This is needed for inheritance in klassen/ directory
                                        # Only skip wildcard imports from framework
                                        new_nodes.append(node)
                                    elif isinstance(node, ast.Assign):
                                        # avoid assignments that call functions at top-level
                                        val = getattr(node, 'value', None)
                                        if not isinstance(val, ast.Call):
                                            new_nodes.append(node)
                                    elif isinstance(node, ast.AnnAssign):
                                        val = getattr(node, 'value', None)
                                        if val is None or not isinstance(val, ast.Call):
                                            new_nodes.append(node)

                                new_mod = ast.Module(body=new_nodes, type_ignores=[])
                                ast.fix_missing_locations(new_mod)
                                module = types.ModuleType(mod_name or os.path.splitext(os.path.basename(path))[0])
                                module.__file__ = path
                                
                                # If loading from klassen/ directory, add it to sys.path temporarily
                                # so that relative imports like "from spielobjekt import *" work
                                klassen_dir = os.path.join(repo_root, 'klassen')
                                added_to_path = False
                                if 'klassen' in path and klassen_dir not in sys.path:
                                    sys.path.insert(0, klassen_dir)
                                    added_to_path = True
                                
                                try:
                                    # execute only the trimmed AST
                                    code_obj = compile(new_mod, path, 'exec')
                                    exec(code_obj, module.__dict__)
                                finally:
                                    # Remove klassen/ from sys.path after loading
                                    if added_to_path and klassen_dir in sys.path:
                                        sys.path.remove(klassen_dir)
                                
                                return module
                            except Exception:
                                return None

                        # If cand refers to a dotted package (like klassen.x), try normal import first
                        if '.' in cand:
                            try:
                                # For klassen.* imports, add klassen/ to sys.path temporarily
                                _repo_root = os.path.dirname(os.path.dirname(__file__))
                                klassen_dir = os.path.join(_repo_root, 'klassen')
                                added_to_path = False
                                if cand.startswith('klassen.') and klassen_dir not in sys.path:
                                    sys.path.insert(0, klassen_dir)
                                    added_to_path = True
                                
                                try:
                                    mod = importlib.import_module(cand)
                                    
                                    self._student_module_cache[cand] = mod
                                    if required_class_name is None or getattr(mod, required_class_name, None) is not None:
                                        return mod
                                    # module loaded but doesn't define the required class -> try next candidate
                                    continue
                                finally:
                                    # Remove klassen/ from sys.path after import
                                    if added_to_path and klassen_dir in sys.path:
                                        sys.path.remove(klassen_dir)
                            except Exception:
                                self._student_module_cache[cand] = None
                                continue

                        # Resolve plain module name to possible file paths
                        repo_root = os.path.dirname(os.path.dirname(__file__))
                        fp_root = os.path.join(repo_root, f"{cand}.py")
                        fp_klassen = os.path.join(repo_root, 'klassen', f"{cand}.py")

                        if os.path.exists(fp_root):
                            mod = _safe_load_from_path(fp_root, mod_name=cand)
                            self._student_module_cache[cand] = mod
                            if mod and (required_class_name is None or getattr(mod, required_class_name, None) is not None):
                                return mod
                            else:
                                continue
                        if os.path.exists(fp_klassen):
                            mod = _safe_load_from_path(fp_klassen, mod_name=f"klassen.{cand}")
                            self._student_module_cache[cand] = mod
                            if mod and (required_class_name is None or getattr(mod, required_class_name, None) is not None):
                                return mod
                            else:
                                continue

                        # fallback: try normal import
                        try:
                            mod = importlib.import_module(cand)
                            self._student_module_cache[cand] = mod
                            if required_class_name is None or getattr(mod, required_class_name, None) is not None:
                                return mod
                            continue
                        except Exception:
                            self._student_module_cache[cand] = None
                            continue
                    except Exception:
                        self._student_module_cache[cand] = None
                        continue
                return None

            # Build candidate modules depending on provided settings
            candidates = []
            
            # Phase 2: class_requirements takes precedence over old flags
            if load_student_from_requirements:
                cname = canonical_name.lower()
                spath = os.path.join(repo_root, 'schueler.py')
                kpath = os.path.join(repo_root, 'klassen', f"{cname}.py")
                
                if prefer_schueler:
                    # Explicitly requested from schueler.py
                    if os.path.exists(spath):
                        candidates.append('schueler')
                    else:
                        # File doesn't exist, still try to import (might be installed package)
                        candidates.append('schueler')
                elif prefer_klassen:
                    # Explicitly requested from klassen/<name>.py
                    if os.path.exists(kpath):
                        candidates.append(f"klassen.{cname}")
                    else:
                        # File doesn't exist, still try to import
                        candidates.append(f"klassen.{cname}")
            elif import_pfad:
                # import_pfad may be a dotted module path or a simple module name
                if isinstance(import_pfad, str) and '.' in import_pfad:
                    candidates.append(import_pfad)
                else:
                    # check repo-root file
                    rp = os.path.join(repo_root, f"{import_pfad}.py")
                    if os.path.exists(rp):
                        candidates.append(import_pfad)
                    kp = os.path.join(repo_root, 'klassen', f"{import_pfad}.py")
                    if os.path.exists(kp):
                        candidates.append(f"klassen.{import_pfad}")
                    # fallback names
                    candidates.append(import_pfad)
                    candidates.append(f"klassen.{import_pfad}")
            else:
                # use_student_flag is True
                cname = canonical_name.lower()
                spath = os.path.join(repo_root, 'schueler.py')
                kpath = os.path.join(repo_root, 'klassen', f"{cname}.py")

                # If the editor/lavel indicates student classes are in the subfolder,
                # prefer `klassen/<cname>.py`. If that file exists, try it only; if it
                # doesn't exist but `schueler.py` is present, try `schueler` instead.
                # Symmetrically, if the subfolder flag is False and `schueler.py`
                # exists, try `schueler` only and do NOT silently fall back to
                # `klassen/<cname>.py`. This enforces the level/editor preference and
                # avoids surprising fallbacks when the student intentionally provided
                # a root `schueler.py` without the requested class.
                if subfolder_flag:
                    if os.path.exists(kpath):
                        candidates.append(f"klassen.{cname}")
                    elif os.path.exists(spath):
                        candidates.append('schueler')
                    else:
                        # neither file exists: try both names (import fallback)
                        candidates.extend([f"klassen.{cname}", 'schueler'])
                else:
                    if os.path.exists(spath):
                        candidates.append('schueler')
                    elif os.path.exists(kpath):
                        candidates.append(f"klassen.{cname}")
                    else:
                        candidates.extend(['schueler', f"klassen.{cname}"])

            # Ask try_import to return the first module that defines the
            # requested student class (if present). If none of the candidates
            # define the class, try_import will return None.
            mod = try_import(candidates, required_class_name=canonical_name)
            if not mod:
                # No student module found
                return None

            # Determine class name (allow mapping)
            class_map = settings.get('student_class_map', {}) or {}
            student_cls_name = class_map.get(canonical_name, canonical_name)
            cls = getattr(mod, student_cls_name, None)
            if cls is None:
                return None
            return cls
        except Exception:
            return None

    def _student_has_class(self, canonical_name: str) -> bool:
        """Check (by filesystem/AST) whether a student-provided class with the
        given canonical_name exists either in `schueler.py` or in `klassen/<name>.py`.
        This avoids importing/running student top-level code and provides a
        reliable presence test for tile-drawing logic.
        """
        try:
            repo_root = os.path.dirname(os.path.dirname(__file__))
            cname = canonical_name
            # 1) explicit import_pfad may point to a module name
            import_pfad = None
            try:
                import_pfad = (self.settings or {}).get('import_pfad')
            except Exception:
                import_pfad = None

            def _file_has_class(path, cls_name):
                try:
                    if not os.path.exists(path):
                        return False
                    src = open(path, 'r', encoding='utf-8').read()
                    tree = ast.parse(src, path)
                    
                    # helper: check whether the class __init__ sets required attributes
                    # Also checks for getter methods (get_<attr>) if attribute is private
                    def _class_has_required_attrs(class_node, required):
                        found = set()
                        getters = set()
                        
                        # First pass: find all attributes set in __init__
                        for item in class_node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                                for stmt in ast.walk(item):
                                    # self.x = ... or self.__x = ...
                                    if isinstance(stmt, ast.Assign):
                                        for t in stmt.targets:
                                            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == 'self':
                                                attr_name = t.attr
                                                # Handle private attributes: __x -> x
                                                if attr_name.startswith('_' + class_node.name + '__'):
                                                    # Double underscore name mangling (own class)
                                                    attr_name = attr_name[len('_' + class_node.name + '__'):]
                                                elif attr_name.startswith('_') and '__' in attr_name:
                                                    # Name mangling from parent class (e.g., _Spielobjekt__typ -> typ)
                                                    # Extract the attribute name after the last __
                                                    parts = attr_name.split('__')
                                                    if len(parts) >= 2:
                                                        attr_name = parts[-1]  # Get the part after __
                                                elif attr_name.startswith('__'):
                                                    # Private attribute __x -> x
                                                    attr_name = attr_name[2:]
                                                found.add(attr_name)
                                    # setattr(self, 'x', ...)
                                    if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name) and stmt.func.id == 'setattr':
                                        args = stmt.args
                                        if len(args) >= 2:
                                            if isinstance(args[0], ast.Name) and args[0].id == 'self':
                                                # second arg may be a constant/string
                                                a1 = args[1]
                                                if isinstance(a1, ast.Constant) and isinstance(a1.value, str):
                                                    found.add(a1.value)
                                                elif isinstance(a1, ast.Str):
                                                    found.add(a1.s)
                        
                        # Second pass: find getter methods in this class
                        for item in class_node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith('get_'):
                                    attr_name = item.name[4:]  # Remove 'get_' prefix
                                    getters.add(attr_name)
                        
                        # Third pass: if not all attributes found, check parent classes RECURSIVELY
                        # Helper function to recursively collect attributes from parent chain
                        def collect_parent_attrs(base_class_name, visited=None):
                            """Recursively collect attributes from parent class and its parents"""
                            if visited is None:
                                visited = set()
                            if base_class_name in visited:
                                return set(), set()  # Avoid infinite loops
                            visited.add(base_class_name)
                            
                            parent_attrs = set()
                            parent_getters = set()
                            
                            try:
                                parent_file = os.path.join(repo_root, 'klassen', f'{base_class_name.lower()}.py')
                                if os.path.exists(parent_file):
                                    parent_src = open(parent_file, 'r', encoding='utf-8').read()
                                    parent_tree = ast.parse(parent_src, parent_file)
                                    
                                    for parent_node in parent_tree.body:
                                        if isinstance(parent_node, ast.ClassDef) and parent_node.name == base_class_name:
                                            # Get parent's attributes from __init__
                                            for item in parent_node.body:
                                                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                                                    for stmt in ast.walk(item):
                                                        if isinstance(stmt, ast.Assign):
                                                            for t in stmt.targets:
                                                                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == 'self':
                                                                    attr_name = t.attr
                                                                    # Handle private attributes from parent
                                                                    if attr_name.startswith('_' + base_class_name + '__'):
                                                                        attr_name = attr_name[len('_' + base_class_name + '__'):]
                                                                    elif attr_name.startswith('__'):
                                                                        attr_name = attr_name[2:]
                                                                    parent_attrs.add(attr_name)
                                            
                                            # Get parent's getter methods
                                            for item in parent_node.body:
                                                if isinstance(item, ast.FunctionDef):
                                                    if item.name.startswith('get_'):
                                                        attr_name = item.name[4:]
                                                        parent_getters.add(attr_name)
                                            
                                            # RECURSIVELY check parent's parents
                                            for grandparent_base in parent_node.bases:
                                                grandparent_name = None
                                                if isinstance(grandparent_base, ast.Name):
                                                    grandparent_name = grandparent_base.id
                                                elif isinstance(grandparent_base, ast.Attribute):
                                                    grandparent_name = grandparent_base.attr
                                                
                                                if grandparent_name:
                                                    gp_attrs, gp_getters = collect_parent_attrs(grandparent_name, visited)
                                                    parent_attrs |= gp_attrs
                                                    parent_getters |= gp_getters
                            except Exception:
                                pass
                            
                            return parent_attrs, parent_getters
                        
                        available = found | getters
                        if not set(required).issubset(available):
                            # Get base class names and recursively collect their attributes
                            for base in class_node.bases:
                                base_name = None
                                if isinstance(base, ast.Name):
                                    base_name = base.id
                                elif isinstance(base, ast.Attribute):
                                    base_name = base.attr
                                
                                if base_name:
                                    parent_attrs, parent_getters = collect_parent_attrs(base_name)
                                    found |= parent_attrs
                                    getters |= parent_getters
                            
                            available = found | getters
                        
                        return set(required).issubset(available)
                    
                    # helper: check whether the class has required methods (including inherited) - RECURSIVE
                    def _class_has_required_methods(class_node, required_methods):
                        # Helper function to recursively collect methods from parent chain
                        def collect_parent_methods(base_class_name, visited=None):
                            """Recursively collect methods from parent class and its parents"""
                            if visited is None:
                                visited = set()
                            if base_class_name in visited:
                                return set()  # Avoid infinite loops
                            visited.add(base_class_name)
                            
                            parent_methods = set()
                            
                            try:
                                parent_file = os.path.join(repo_root, 'klassen', f'{base_class_name.lower()}.py')
                                if os.path.exists(parent_file):
                                    parent_src = open(parent_file, 'r', encoding='utf-8').read()
                                    parent_tree = ast.parse(parent_src, parent_file)
                                    
                                    for parent_node in parent_tree.body:
                                        if isinstance(parent_node, ast.ClassDef) and parent_node.name == base_class_name:
                                            # Get parent's methods
                                            for item in parent_node.body:
                                                if isinstance(item, ast.FunctionDef):
                                                    parent_methods.add(item.name)
                                            
                                            # RECURSIVELY check parent's parents
                                            for grandparent_base in parent_node.bases:
                                                grandparent_name = None
                                                if isinstance(grandparent_base, ast.Name):
                                                    grandparent_name = grandparent_base.id
                                                elif isinstance(grandparent_base, ast.Attribute):
                                                    grandparent_name = grandparent_base.attr
                                                
                                                if grandparent_name:
                                                    gp_methods = collect_parent_methods(grandparent_name, visited)
                                                    parent_methods |= gp_methods
                            except Exception:
                                pass
                            
                            return parent_methods
                        
                        found_methods = set()
                        # Check methods defined in this class
                        for item in class_node.body:
                            if isinstance(item, ast.FunctionDef):
                                found_methods.add(item.name)
                        
                        # If not all methods found, check parent classes RECURSIVELY
                        if not set(required_methods).issubset(found_methods):
                            # Get base class names and recursively collect their methods
                            for base in class_node.bases:
                                base_name = None
                                if isinstance(base, ast.Name):
                                    base_name = base.id
                                elif isinstance(base, ast.Attribute):
                                    base_name = base.attr
                                
                                if base_name:
                                    parent_methods = collect_parent_methods(base_name)
                                    found_methods |= parent_methods
                        
                        return set(required_methods).issubset(found_methods)
                    
                    # helper: check whether the class inherits from the required base class
                    def _class_has_required_inheritance(class_node, required_base):
                        if required_base == "None" or not required_base:
                            return True  # No inheritance required
                        
                        # Check if the class has any base classes
                        if not class_node.bases:
                            return False  # No inheritance but required
                        
                        # Check each base class
                        for base in class_node.bases:
                            # Simple name (e.g., Spielobjekt)
                            if isinstance(base, ast.Name) and base.id == required_base:
                                return True
                            # Attribute access (e.g., module.Spielobjekt)
                            if isinstance(base, ast.Attribute) and base.attr == required_base:
                                return True
                        
                        return False  # Required base class not found

                    for node in tree.body:
                        if isinstance(node, ast.ClassDef) and node.name == cls_name:
                            # Check class_requirements for ANY class that has requirements defined
                            req = self.class_requirements.get(cls_name, {})
                            required_attrs = req.get('attributes', [])
                            required_methods = req.get('methods', [])
                            required_inheritance = req.get('inherits', 'None')
                            
                            # Also include private attributes and methods
                            private_attrs = req.get('attributes_private', {})
                            private_methods = req.get('methods_private', {})
                            
                            # Combine public and private requirements
                            all_required_attrs = list(required_attrs)
                            if isinstance(private_attrs, dict):
                                all_required_attrs.extend([attr for attr, is_private in private_attrs.items() if is_private])
                            
                            all_required_methods = list(required_methods)
                            if isinstance(private_methods, dict):
                                all_required_methods.extend([method for method, is_private in private_methods.items() if is_private])
                            
                            # Special case: Held - if no requirements defined, use legacy minimal set
                            if cls_name == 'Held' and not all_required_attrs and not all_required_methods:
                                all_required_attrs = ['x', 'y', 'richtung', 'weiblich', 'typ']
                            
                            # Check if any requirements are defined (attributes, methods, or inheritance)
                            has_requirements = (all_required_attrs or all_required_methods or 
                                              (required_inheritance and required_inheritance != 'None'))
                            
                            # If we have any requirements, validate them
                            if has_requirements:
                                try:
                                    # Check inheritance first (most important constraint)
                                    if required_inheritance and required_inheritance != 'None':
                                        if not _class_has_required_inheritance(node, required_inheritance):
                                            return False
                                    
                                    # Check attributes
                                    if all_required_attrs and not _class_has_required_attrs(node, all_required_attrs):
                                        return False
                                    
                                    # Check methods
                                    if all_required_methods and not _class_has_required_methods(node, all_required_methods):
                                        return False
                                    
                                    return True
                                except Exception:
                                    return False
                            
                            # No requirements defined for this class - just check that it exists
                            return True
                    return False
                except Exception:
                    return False

            # If import_pfad points to a specific file/module, check it first
            if import_pfad:
                # dotted module
                if isinstance(import_pfad, str) and '.' in import_pfad:
                    # try to resolve file via importlib
                    try:
                        spec = importlib.util.find_spec(import_pfad)
                        if spec and spec.origin:
                            return _file_has_class(spec.origin, cname)
                    except Exception:
                        pass
                else:
                    # check repo-root file and klassen/<import_pfad>.py
                    rp = os.path.join(repo_root, f"{import_pfad}.py")
                    if _file_has_class(rp, cname):
                        return True
                    kp = os.path.join(repo_root, 'klassen', f"{import_pfad}.py")
                    if _file_has_class(kp, cname):
                        return True

            # Align presence-check with the editor/level preference flags:
            # First check class_requirements for load_from_klassen / load_from_schueler
            # Otherwise fall back to student_classes_in_subfolder setting
            lower = canonical_name.lower()
            kp = os.path.join(repo_root, 'klassen', f"{lower}.py")
            sp = os.path.join(repo_root, 'schueler.py')

            # Check class_requirements for this specific class
            req = self.class_requirements.get(canonical_name, {})
            load_from_klassen = req.get('load_from_klassen', False)
            load_from_schueler = req.get('load_from_schueler', False)
            check_implementation = req.get('check_implementation', False)
            
            # Check if class has any requirements (inheritance, methods, attributes)
            has_inheritance = req.get('inherits') and req.get('inherits') != 'None'
            has_methods = bool(req.get('methods') or req.get('methods_private'))
            has_attributes = bool(req.get('attributes') or req.get('attributes_private'))
            has_any_requirements = has_inheritance or has_methods or has_attributes
            
            # For abstract classes with check_implementation, always search in klassen/
            if check_implementation and canonical_name in ['Spielobjekt', 'Charakter']:
                if os.path.exists(kp):
                    return _file_has_class(kp, canonical_name)
                # Also check schueler.py as fallback
                if os.path.exists(sp):
                    return _file_has_class(sp, canonical_name)
                return False
            
            # If class has ANY requirements defined, search in klassen/ first
            if has_any_requirements and not load_from_schueler:
                if os.path.exists(kp):
                    return _file_has_class(kp, canonical_name)
                # Also check schueler.py as fallback
                if os.path.exists(sp):
                    return _file_has_class(sp, canonical_name)
                return False
            
            # If class_requirements explicitly sets load location, use that
            if load_from_klassen or load_from_schueler:
                if load_from_klassen:
                    # Must load from klassen/<name>.py
                    if os.path.exists(kp):
                        return _file_has_class(kp, canonical_name)
                    return False
                elif load_from_schueler:
                    # Must load from schueler.py
                    if os.path.exists(sp):
                        return _file_has_class(sp, canonical_name)
                    return False
            
            # Fall back to student_classes_in_subfolder setting
            subfolder_flag = bool((self.settings or {}).get('student_classes_in_subfolder', False))

            if subfolder_flag:
                # prefer klassen; if it exists, require it to have the class
                if os.path.exists(kp):
                    return _file_has_class(kp, canonical_name)
                # klassen file doesn't exist; if schueler exists, check it
                if os.path.exists(sp):
                    return _file_has_class(sp, canonical_name)
                # neither file exists -> false
                return False

            else:
                # prefer schueler; if schueler.py exists, require it to have the class
                if os.path.exists(sp):
                    return _file_has_class(sp, canonical_name)
                # schueler not present; if klassen file exists, check it
                if os.path.exists(kp):
                    return _file_has_class(kp, canonical_name)
                return False

        except Exception:
            return False

    def _compute_required_classes(self):
        """Return set of canonical class names required by the level based on
        the original tile data. This reads `self.level.tiles` without
        mutating it (we only examine, not yield/alter), so callers can use
        the result after spawning has occurred.
        """
        try:
            # Check if Zettel student mode will be enabled
            zettel_requirements = self.class_requirements.get('Zettel', {})
            prefer_schueler = bool(zettel_requirements.get('load_from_schueler', False))
            prefer_klassen = bool(zettel_requirements.get('load_from_klassen', False))
            has_methods = bool(zettel_requirements.get('methods', []))
            has_attrs = bool(zettel_requirements.get('attributes', []))
            has_inheritance = zettel_requirements.get('inherits') and zettel_requirements.get('inherits') != 'None'
            zettel_student_mode = prefer_schueler or prefer_klassen or has_methods or has_attrs or has_inheritance
            
            # Map tile codes to class names
            mapping = { 
                'p': 'Held', 
                'h': 'Herz', 
                'x': 'Monster', 
                'c': 'Zettel' if zettel_student_mode else 'Code',  # Use Zettel if student mode
                'd': 'Tuer', 
                's': 'Schluessel', 
                'v': 'Villager', 
                'k': 'Knappe', 
                'g': 'Tor', 
                'q': 'Questgeber', 
                't': 'Hindernis', 
                'm': 'Hindernis', 
                'b': 'Hindernis' 
            }
            needed = set()
            for y, zeile in enumerate(self.level.tiles):
                for x, code in enumerate(zeile):
                    if not isinstance(code, str):
                        continue
                    key = code.lower()
                    cn = mapping.get(key)
                    if cn:
                        needed.add(cn)
            return needed
        except Exception:
            return set()

        # Ensure desired items are available among villagers (inject if missing)
        if desired_items and spawned_villagers:
            for name in desired_items:
                # if no villager offers this yet, inject into a random villager
                offered = False
                for v in spawned_villagers:
                    # search v.preisliste for item names
                    try:
                        for it in v.inventar:
                            if getattr(it, 'name', None) == name:
                                offered = True
                                break
                        if offered:
                            break
                    except Exception:
                        continue
                if not offered:
                    # choose a random villager and add the desired item with decided price
                    target = random.choice(spawned_villagers)
                    price = desired_prices.get(name, random.randint(10, 80))
                    try:
                        target.biete_item_an(Gegenstand(name, price), price)
                    except Exception:
                        pass
        # Ensure we have a reference to the spawned Held (some code-paths may set it earlier,
        # but in case it wasn't set due to ordering, try to find it among spawned objects).
        if getattr(self, 'held', None) is None:
            for obj in self.objekte:
                try:
                    if getattr(obj, 'typ', None) == 'Held':
                        self.held = obj
                        break
                except Exception:
                    continue

        for o in self.objekte:
            # Determine object type name defensively (student objects may raise on attribute access)
            try:
                typ_name = getattr(o, 'typ', None)
            except Exception:
                try:
                    typ_name = o.__class__.__name__
                except Exception:
                    typ_name = None

            # Safely read settings for this type
            cfg = {}
            try:
                if isinstance(self.settings, dict) and typ_name:
                    cfg = self.settings.get(typ_name, {}) or {}
            except Exception:
                cfg = {}

            # Only call set_privatmodus if the flag is explicitly False (legacy keys handled above).
            # If the object does not implement set_privatmodus, fall back to creating a Proxy wrapper
            # that blocks critical attributes. This enforces privacy regardless of the object's API.
            try:
                # Consider both old ('privat') and new ('public') setting names.
                is_private = False
                try:
                    if 'public' in cfg:
                        is_private = (cfg.get('public') is False)
                    elif 'privat' in cfg:
                        is_private = bool(cfg.get('privat'))
                    else:
                        is_private = False
                except Exception:
                    is_private = False
                if is_private:
                    try:
                        if hasattr(o, 'set_privatmodus'):
                            try:
                                o.set_privatmodus(True)
                            except Exception:
                                pass
                        else:
                            # replace object in the list with a proxy wrapper
                            proxy = self._privatisiere(o)
                            try:
                                idx = self.objekte.index(o)
                                self.objekte[idx] = proxy
                            except ValueError:
                                pass
                            # update references to held/knappe if necessary
                            try:
                                if getattr(self, 'held', None) is o:
                                    self.held = proxy
                            except Exception:
                                pass
                            try:
                                if getattr(self, 'knappe', None) is o:
                                    self.knappe = proxy
                            except Exception:
                                pass
                            # also try to update names in framework.grundlage if present
                            try:
                                import framework.grundlage as grundlage
                                for name in ('held','knappe','zettel','tuer','schluessel','villager','tor'):
                                    try:
                                        if getattr(grundlage, name, None) is o:
                                            setattr(grundlage, name, proxy)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass

            # Attach Knappe to hero if possible. Use defensive attribute access to avoid triggering
            # student-provided __getattribute__ implementations unexpectedly.
            try:
                is_knappe = False
                try:
                    is_knappe = (typ_name == "Knappe")
                except Exception:
                    is_knappe = False

                if is_knappe:
                    if getattr(self, 'held', None) is None:
                        # no hero to attach to; leave for the post-spawn scan or hero-to-knappe attach
                        continue
                    # ensure held has knappen list
                    try:
                        if not hasattr(self.held, 'knappen'):
                            try:
                                setattr(self.held, 'knappen', [])
                            except Exception:
                                pass
                        try:
                            self.held.add_knappe(o)
                        except Exception:
                            pass
                    except Exception:
                        pass
            except Exception:
                pass
            


    # --- Zeichnen ---
    def _render_template_objects(self, screen):
        """Rendert Template-Objekte mit 25% Opacity im rebuild_mode."""
        from .utils import lade_sprite
        
        # Sprite-Mapping für Template-Objekte
        sprite_map = {
            'Held': 'sprites/held.png',
            'Knappe': 'sprites/knappe.png',
            'Monster': 'sprites/monster.png',
            'Bogenschuetze': 'sprites/archer.png',
            'Herz': 'sprites/herz.png',
            'Tuer': 'sprites/tuer.png',
            'Tor': 'sprites/tor_zu.png',
            'Schluessel': 'sprites/key_green.png',
            'Zettel': 'sprites/code.png',
            'Villager': 'sprites/villager.png',
            'Hindernis': 'sprites/baum.png',  # default, wird überschrieben
        }
        
        for tpl in self.template_objects:
            # Überspringe erfüllte Templates
            if tpl.get('_fulfilled', False):
                continue
            
            try:
                typ = tpl.get('typ')
                x = tpl.get('x', 0)
                y = tpl.get('y', 0)
                richtung = tpl.get('richtung', 'down')
                
                # Bestimme Sprite
                sprite_path = sprite_map.get(typ, 'sprites/gras.png')
                
                # Spezialbehandlung für Hindernis
                if typ == 'Hindernis':
                    hindernis_typ = tpl.get('hindernis_typ', 'Baum')
                    sprite_map_hindernis = {'Baum': 'sprites/baum.png', 'Berg': 'sprites/berg.png', 'Busch': 'sprites/busch.png'}
                    sprite_path = sprite_map_hindernis.get(hindernis_typ, 'sprites/baum.png')
                
                # Spezialbehandlung für farbige Türen/Schlüssel
                if typ in ('Tuer', 'Schluessel'):
                    farbe = tpl.get('farbe', 'green')
                    if typ == 'Tuer':
                        sprite_path = f'sprites/locked_door_{farbe}.png'
                    else:
                        sprite_path = f'sprites/key_{farbe}.png'
                
                # Spezialbehandlung für richtungsabhängige Sprites (Held, Knappe, Monster, etc.)
                if typ in ('Held', 'Knappe', 'Monster', 'Bogenschuetze'):
                    # Verwende richtungsspezifische Sprites
                    base_name = sprite_path.replace('.png', '')
                    sprite_path = f'{base_name}_{richtung}.png'
                
                # Lade und skaliere Sprite
                sprite = lade_sprite(sprite_path)
                if sprite:
                    scaled = pygame.transform.scale(sprite, (self.feldgroesse, self.feldgroesse))
                    
                    # Erstelle Surface mit Alpha für Transparenz
                    alpha_surface = scaled.copy()
                    alpha_surface.set_alpha(64)  # 25% opacity (255 * 0.25 = 64)
                    
                    # Zeichne an Position
                    screen.blit(alpha_surface, (x * self.feldgroesse, y * self.feldgroesse))
            except Exception as e:
                # Fehler beim Rendern eines einzelnen Templates ignorieren
                pass
    
    def zeichne(self, screen):
        # If rendering was explicitly disabled (student classes requested but missing),
        # show a small overlay and skip normal drawing.
        try:
            if getattr(self, '_render_disabled', False):
                try:
                    screen.fill((0, 0, 0))
                except Exception:
                    pass
                if getattr(self, 'framework', None) and getattr(self.framework, 'font', None):
                    try:
                        msg = "Level deaktiviert: Schülerklassen fehlen"
                        txt = self.framework.font.render(msg, True, (255, 80, 80))
                        screen.blit(txt, (8, 8))
                    except Exception:
                        pass
                return
        except Exception:
            pass
        # Sortierte Zeichnung: zuerst Boden / Hindernisse, dann Items, dann Lebewesen
        # Use canonical type names (matching Objekt.typ) so objects are drawn.
        zeichenreihenfolge = ["Berg", "Baum", "Busch", "Hindernis", "?", "Spruch", "Zettel", "Herz", "Tuer", "Tor", "Schluessel", "Monster", "Held", "Knappe", "Questgeber", "Dorfbewohner", "Dorfbewohnerin"]

        # Determine whether student mode requests are active and whether a student
        # Hindernis class is valid. 
        # - If class missing or validation failed: don't draw obstacle tiles
        # - If get_typ missing: draw as question marks (handled in object drawing)
        # - If all getters present: draw normally via object drawing
        hide_obstacles = False
        try:
            # Use the pre-validated flags from spawn logic
            student_mode_enabled = getattr(self, '_hindernis_student_mode_enabled', False)
            hindernis_valid = getattr(self, '_hindernis_class_valid', False)
            
            if student_mode_enabled and not hindernis_valid:
                # Student mode is active but class is missing or invalid - hide tiles
                hide_obstacles = True
        except Exception:
            hide_obstacles = False

        # Draw tiles with optional obstacle hiding
        try:
            # Draw grass and optionally obstacle overlays
            for y, zeile in enumerate(self.level.tiles):
                for x, code in enumerate(zeile):
                    # Always draw grass base
                    gras = self.level.texturen.get('w')
                    if gras:
                        img = pygame.transform.scale(gras, (self.feldgroesse, self.feldgroesse))
                        screen.blit(img, (x * self.feldgroesse, y * self.feldgroesse))
                    # Draw obstacle textures unless hidden
                    if code in ('m','b','t','g'):
                        # Skip obstacle tiles in rebuild_mode - templates will be rendered instead
                        if self.rebuild_mode and code in ('m','b','t'):
                            continue
                        if hide_obstacles and code in ('m','b','t'):
                            continue
                        tex = self.level.texturen.get(code)
                        if tex:
                            img = pygame.transform.scale(tex, (self.feldgroesse, self.feldgroesse))
                            screen.blit(img, (x * self.feldgroesse, y * self.feldgroesse))
        except Exception:
            # fallback to level's drawing if something goes wrong
            try:
                self.level.zeichne(screen, self.feldgroesse)
            except Exception:
                pass
        
        # Draw template objects with 25% opacity in rebuild mode
        if self.rebuild_mode and self.template_objects:
            try:
                self._render_template_objects(screen)
            except Exception as e:
                print(f"[FEHLER] Template-Rendering fehlgeschlagen: {e}")
        
        for typ in zeichenreihenfolge:
            # Iterate defensively: student-provided objects may raise on attribute access
            # (or miss attributes). Avoid list comprehensions that access obj attributes
            # inside the generator expression; instead query each object in a try/except
            # and skip misbehaving ones.
            for o in list(self.objekte):
                try:
                    # NOTE: do not skip dead objects here; dead characters should still be
                    # rendered (KO sprite) so the student sees the result of combat.
                    # must match requested type
                    if getattr(o, 'typ', None) != typ:
                        continue
                except Exception:
                    # object misbehaved when reading attributes; skip it
                    continue

                # Previously we skipped rendering MetaHeld objects whose student
                # implementation was marked '_student_incomplete'. That hid the
                # student-provided class entirely and could make the framework
                # appear to have used the integrated Held. Instead, always
                # attempt to render the object (so incomplete student heroes are
                # visible and exercised); if the student's draw raises, we'll
                # fall back to the default rendering below.

                # Prefer calling student-provided zeichne() if present, otherwise use
                # framework fallback drawing to ensure student objects without
                # zeichne() still appear correctly.
                try:
                    if hasattr(o, 'zeichne') and callable(getattr(o, 'zeichne')):
                        try:
                            o.zeichne(screen, self.feldgroesse)
                        except Exception:
                            # If student's draw raises, fall through to overlay + popup
                            raise
                    else:
                        # Use framework default rendering for objects lacking zeichne()
                        try:
                            self._draw_object_default(o, screen, self.feldgroesse)
                        except Exception:
                            # fallthrough to error handling below
                            raise
                except Exception:
                    # best-effort: don't let a single broken draw break the whole frame
                    try:
                        # Draw a red question-mark overlay above the tile if we know x/y
                        if hasattr(o, 'x') and hasattr(o, 'y'):
                            ox = int(getattr(o, 'x', 0))
                            oy = int(getattr(o, 'y', 0))
                            rx = ox * self.feldgroesse
                            ry = oy * self.feldgroesse
                            try:
                                # translucent circle behind marker
                                surf = pygame.Surface((self.feldgroesse, self.feldgroesse), pygame.SRCALPHA)
                                surf.fill((0,0,0,0))
                                pygame.draw.circle(surf, (220,20,20,180), (self.feldgroesse//2, self.feldgroesse//2), max(8, self.feldgroesse//4))
                                screen.blit(surf, (rx, ry))
                                # question mark
                                qfont = pygame.font.SysFont(None, max(12, self.feldgroesse//2))
                                qsurf = qfont.render("?", True, (255,255,255))
                                qrect = qsurf.get_rect(center=(rx + self.feldgroesse//2, ry + self.feldgroesse//2))
                                screen.blit(qsurf, qrect)
                            except Exception:
                                pass

                        # Log and show a tkinter error popup once per problematic object
                        try:
                            oid = id(o)
                            if oid not in self._logged_broken_objects:
                                self._logged_broken_objects.add(oid)
                                typ = getattr(o, 'typ', None)
                                name = getattr(o, 'name', None)
                                pos = f"{getattr(o, 'x', '?')},{getattr(o, 'y', '?')}"
                                tb = traceback.format_exc()
                                msg = f"Fehler beim Zeichnen des Objekts {typ} ({name}) an Position {pos}\n\n{tb}"

                                # Avoid showing a Tkinter popup from a background
                                # thread (this is not thread-safe and can make the
                                # application window unresponsive on some platforms).
                                # Instead, log the error to the console so it can be
                                # inspected by developers; the in-game visual marker
                                # already indicates a broken object.
                                try:
                                    print("[ERROR] Objektfehler:")
                                    print(msg)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                    except Exception:
                        pass

        # Draw move-to victory target if configured
        try:
            vic = (self.settings or {}).get('victory', {}) or {}
            mv = vic.get('move_to') if isinstance(vic, dict) else None
            if mv and isinstance(mv, dict) and mv.get('enabled'):
                tx = int(mv.get('x', -999))
                ty = int(mv.get('y', -999))
                if 0 <= tx < self.level.breite and 0 <= ty < self.level.hoehe:
                    rect = pygame.Rect(tx * self.feldgroesse, ty * self.feldgroesse, self.feldgroesse, self.feldgroesse)
                    try:
                        highlight = pygame.Surface((self.feldgroesse, self.feldgroesse), pygame.SRCALPHA)
                        highlight.fill((255, 0, 0, 48))
                        screen.blit(highlight, rect.topleft)
                        pygame.draw.rect(screen, (255, 0, 0), rect, max(2, self.feldgroesse // 16))
                    except Exception:
                        # best-effort only
                        pygame.draw.rect(screen, (255, 0, 0), rect, 4)
        except Exception:
            pass

        # Draw transient projectiles (arrows) defined on the framework (brown moving lines)
        try:
            fw = getattr(self, 'framework', None)
            if fw is not None and hasattr(fw, '_projectiles'):
                now = pygame.time.get_ticks()
                remaining = []
                for p in list(getattr(fw, '_projectiles') or []):
                    try:
                        st = p.get('start_time', now)
                        dur = int(p.get('duration', 200) or 200)
                        t = float(now - st) / float(max(1, dur))
                        if t >= 1.0:
                            # finalize: mark victim KO and load KO-sprite
                            victim = p.get('victim')
                            attacker = p.get('attacker')
                            try:
                                if victim is not None:
                                    victim.tot = True
                                    try:
                                        victim._update_sprite_richtung()
                                    except Exception:
                                        pass
                                    # load KO sprite if available
                                    try:
                                        base_opf = os.path.splitext(victim.sprite_pfad)[0]
                                        ko_pfad = f"{base_opf}_ko.png"
                                        if os.path.exists(ko_pfad):
                                            victim.bild = pygame.image.load(ko_pfad).convert_alpha()
                                    except Exception:
                                        pass
                                    # set framework hint / block actions for hero/knappe
                                    try:
                                        vtyp = (getattr(victim, 'typ', '') or '').lower()
                                        if vtyp in ('held', 'knappe'):
                                            try:
                                                fw._hinweis = f"{victim.name} wurde von {getattr(attacker,'name', 'Bogenschütze')} überrascht!"
                                            except Exception:
                                                fw._hinweis = "Ein Schütze hat getroffen!"
                                            fw._aktion_blockiert = True
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            # projectile finished; don't re-add
                            continue

                        # draw partial projectile from start to current position
                        sx, sy = p.get('start', (0, 0))
                        ex, ey = p.get('end', (0, 0))
                        # compute partial travel point (cap visible arrow length to half a tile)
                        color = (139, 69, 19)  # brown (shaft)
                        width = max(2, self.feldgroesse // 12)
                        try:
                            vx = ex - sx
                            vy = ey - sy
                            dist = math.hypot(vx, vy)
                            if dist <= 0.001:
                                ux, uy = 0.0, 0.0
                            else:
                                ux, uy = vx / dist, vy / dist

                            # limit visible projectile length to ~half a tile
                            max_vis_len = max(8, self.feldgroesse * 0.5)
                            travel_len = min(dist * t, max_vis_len)

                            # tip length small relative to tile
                            tip_len = max(4, int(self.feldgroesse * 0.12))

                            # tip position (capped)
                            tip_x = sx + ux * travel_len
                            tip_y = sy + uy * travel_len

                            # base point for triangle (a bit behind the tip)
                            base_x = tip_x - ux * tip_len
                            base_y = tip_y - uy * tip_len

                            # perpendicular vector for triangle base width
                            px, py = -uy, ux
                            half_w = max(2, int(tip_len // 2))

                            p1 = (int(tip_x), int(tip_y))
                            p2 = (int(base_x + px * half_w), int(base_y + py * half_w))
                            p3 = (int(base_x - px * half_w), int(base_y - py * half_w))

                            # draw shaft from start to base of triangle
                            try:
                                pygame.draw.line(screen, color, (int(sx), int(sy)), (int(base_x), int(base_y)), width)
                            except Exception:
                                pass

                            # draw triangular silver tip
                            try:
                                silver = (200, 200, 200)
                                pygame.draw.polygon(screen, silver, [p1, p2, p3])
                                pygame.draw.polygon(screen, (120,120,120), [p1, p2, p3], 1)
                            except Exception:
                                pass

                            # trailing white lines (two thin lines slightly behind the tip)
                            try:
                                trail_a = max(3, tip_len // 2)
                                trail_b = max(6, tip_len)
                                off = max(2, half_w)
                                ta_start = (int(tip_x - ux * trail_a + px * off), int(tip_y - uy * trail_a + py * off))
                                ta_end   = (int(tip_x - ux * trail_b + px * off), int(tip_y - uy * trail_b + py * off))
                                tb_start = (int(tip_x - ux * trail_a - px * off), int(tip_y - uy * trail_a - py * off))
                                tb_end   = (int(tip_x - ux * trail_b - px * off), int(tip_y - uy * trail_b - py * off))
                                pygame.draw.line(screen, (255,255,255), ta_start, ta_end, max(1, width//2))
                                pygame.draw.line(screen, (255,255,255), tb_start, tb_end, max(1, width//2))
                            except Exception:
                                pass
                        except Exception:
                            # fallback: simple brown line using previous calculation
                            try:
                                cx = float(sx + (ex - sx) * t)
                                cy = float(sy + (ey - sy) * t)
                                pygame.draw.line(screen, color, (sx, sy), (int(cx), int(cy)), width)
                            except Exception:
                                pass
                        remaining.append(p)
                    except Exception:
                        continue
                try:
                    fw._projectiles = remaining
                except Exception:
                    pass
        except Exception:
            pass


        """
        for o in self.objekte:
            if not o.tot:
                o.zeichne(screen, self.feldgroesse)
                """
    
    def _privatisiere(self, obj):
    # perform privatization without noisy debug prints
        blocked_attrs = {"x", "y", "r", "richtung"}
        class Proxy:
            def __init__(self, original):
                super().__setattr__("_original", original)

            def __getattribute__(self, name):
                if name == "_original":
                    return super().__getattribute__(name)
                original = super().__getattribute__("_original")
                # If attribute is private by naming convention, block
                if name.startswith("_"):
                    raise AttributeError(f"Privates Attribut '{name}' – Zugriff nicht erlaubt")
                # Block specific movement/critical attributes
                try:
                    typ = getattr(original, 'typ', None)
                except Exception:
                    typ = None
                if name in blocked_attrs:
                    raise AttributeError(f"Attribut '{name}' ist privat – Zugriff nicht erlaubt")
                if typ == 'Tuer' and name == 'offen':
                    raise AttributeError(f"Attribut '{name}' ist privat – Zugriff nicht erlaubt")
                return getattr(original, name)

            def __setattr__(self, name, value):
                if name == "_original":
                    super().__setattr__(name, value)
                    return
                original = super().__getattribute__("_original")
                if name.startswith("_"):
                    raise AttributeError(f"Privates Attribut '{name}' – Zugriff nicht erlaubt")
                try:
                    typ = getattr(original, 'typ', None)
                except Exception:
                    typ = None
                if name in blocked_attrs:
                    raise AttributeError(f"Attribut '{name}' ist privat – Schreiben nicht erlaubt")
                if typ == 'Tuer' and name == 'offen':
                    raise AttributeError(f"Attribut '{name}' ist privat – Schreiben nicht erlaubt")
                setattr(original, name, value)

            def __dir__(self):
                return [n for n in dir(super().__getattribute__("_original")) if not n.startswith("_")]

            def __repr__(self):
                try:
                    orig = super().__getattribute__("_original")
                    return "<Proxy({})>".format(repr(orig))
                except Exception:
                    return "<Proxy(unknown)>"

        return Proxy(obj)


    
    def generate_orc_name(self):
        prefixes = ["Gor", "Thr", "Mok", "Grim", "Rag", "Dur", "Zug", "Kra", "Lok", "Ur", "Gar", "Vor"]
        middles = ["'", "a", "o", "u", "ra", "ok", "ug", "ar", "th", "ruk", ""]
        suffixes = ["lok", "grim", "thar", "gash", "rok", "dush", "mok", "zug", "rak", "grom", "nash"]

        name = random.choice(prefixes) + random.choice(middles) + random.choice(suffixes)
        return name.capitalize()
    
    def generate_knappe_name(self):
        names = ["Page Skywalker","Jon Snowflake","Sir Lancelame","Rick Rollins",
                 "Ben of the Rings","Tony Stork","Bucky Stables","Frodolin Beutelfuss","Jamie Lameister","Gerold of Trivia",
                 "Arthur Denton","Samwise the Slacker","Obi-Wan Knappobi","Barry Slow","Knight Fury","Grogulette",
                 "Sir Bean of Gondor","Thorin Eichensohn","Legoless","Knappernick",
                 "Knapptain Iglo","Ritterschorsch","Helm Mut","Sigi von Schwertlingen","Klaus der Kleingehauene","Egon Eisenfaust","Ben Knied","Rainer Zufallsson","Dietmar Degenhart","Uwe von Ungefähr","Hartmut Helmrich","Bodo Beinhart","Kai der Kurze","Knapphart Stahl","Tobi Taschenmesser","Fridolin Fehlschlag","Gernot Gnadenlos","Ralf Rüstungslos","Gustav Gürtelschwert","Kuno Knickbein"]
        return random.choice(names).capitalize()

    def _get_attribute_value(self, obj, attr_name, default=None):
        """Get attribute value from object, trying getter method first, then direct access."""
        # Try direct attribute access first
        if hasattr(obj, attr_name):
            try:
                return getattr(obj, attr_name)
            except AttributeError:
                pass
        # Try getter method
        getter_name = f'get_{attr_name}'
        if hasattr(obj, getter_name):
            try:
                getter = getattr(obj, getter_name)
                if callable(getter):
                    return getter()
            except Exception:
                pass
        return default
    
    def _draw_object_default(self, o, screen, feldgroesse):
        """Best-effort drawing for objects that don't implement zeichne().
        Uses available object.bild or falls back to canonical sprites by type.
        """
        try:
            ox = int(self._get_attribute_value(o, 'x', 0))
            oy = int(self._get_attribute_value(o, 'y', 0))
        except Exception:
            return

        # prefer an existing loaded surface on the object
        surf = getattr(o, 'bild', None)
        if surf is None:
            # try student-provided sprite path
            spf = getattr(o, 'sprite_pfad', None)
            if spf:
                try:
                    surf = lade_sprite(spf, feldgroesse)
                except Exception:
                    surf = None

        if surf is None:
            # choose default by type
            typ = getattr(o, 'typ', None) or o.__class__.__name__
            try:
                if typ == 'Knappe':
                    surf = lade_sprite('sprites/knappe.png', feldgroesse)
                elif typ == 'Held':
                    weib = getattr(o, 'weiblich', False)
                    surf = lade_sprite('sprites/held2.png' if weib else 'sprites/held.png', feldgroesse)
                elif typ == 'Monster':
                    surf = lade_sprite('sprites/monster.png', feldgroesse)
                elif typ in ('Herz', 'Spruch', 'Tuer', 'Tor', 'Schluessel'):
                    # use level textures where available
                    tex = None
                    try:
                        # mapping of typ to tile keys
                        keymap = {'Herz': 'h', 'Spruch': 's', 'Tuer': 't', 'Tor': 'r', 'Schluessel': 'k'}
                        k = keymap.get(typ)
                        if k:
                            tex = self.level.texturen.get(k)
                    except Exception:
                        tex = None
                    if tex:
                        surf = tex
                    else:
                        surf = lade_sprite(None, feldgroesse)
                elif typ == '?':
                    # Render question mark for unknown/invalid typ
                    surf = pygame.Surface((feldgroesse, feldgroesse))
                    surf.fill((200, 200, 200))
                    font = pygame.font.SysFont('Arial', feldgroesse // 2)
                    text = font.render('?', True, (255, 0, 0))
                    text_rect = text.get_rect(center=(feldgroesse // 2, feldgroesse // 2))
                    surf.blit(text, text_rect)
                elif typ in ('Baum', 'Berg', 'Busch'):
                    # Render Hindernis types
                    sprite_map = {'Baum': 'sprites/baum.png', 'Berg': 'sprites/berg.png', 'Busch': 'sprites/busch.png'}
                    surf = lade_sprite(sprite_map.get(typ, 'sprites/baum.png'), feldgroesse)
                elif typ == 'Zettel':
                    # Render Zettel (Code)
                    surf = lade_sprite('sprites/code.png', feldgroesse)
                else:
                    surf = lade_sprite(None, feldgroesse)
            except Exception:
                surf = lade_sprite(None, feldgroesse)

        try:
            # Let the object update its directional sprite (if it has per-direction files)
            try:
                if hasattr(o, '_update_sprite_richtung'):
                    try:
                        o._update_sprite_richtung()
                        surf = getattr(o, 'bild', surf)
                    except Exception:
                        pass
            except Exception:
                pass

            img = pygame.transform.scale(surf, (feldgroesse, feldgroesse))
            screen.blit(img, (ox * feldgroesse, oy * feldgroesse))
        except Exception:
            pass

    # --- Kollisionen / Logik ---
    def innerhalb(self, x, y):
        return 0 <= x < self.level.breite and 0 <= y < self.level.hoehe

    def ist_innerhalb(self, x, y):
        return 0 <= x < self.level.breite and 0 <= y < self.level.hoehe
    
    def ist_weg(self,x,y):
        if not self.innerhalb(x, y): return False
        return self.level.tiles[y][x] == "w"

    def terrain_art_an(self, x, y):
        if not self.innerhalb(x, y): return None
        return {"w":"Weg", "m":"Berg", "b":"Busch", "t":"Baum"}.get(self.level.tiles[y][x])

    def kann_betreten(self, obj, x, y):
        """Prüft, ob ein Feld betreten werden darf."""
        # Grenzen prüfen
        if y < 0 or y >= len(self.level.tiles) or x < 0 or x >= len(self.level.tiles[y]):
            return False

        # Feste Hindernisse im Level
        tile = self.level.tiles[y][x]
        if tile in ("b", "t", "m"):
            # If student mode requests Hindernis classes, defer to object-level
            # ist_passierbar() if available; otherwise legacy behaviour.
            try:
                student_mode_enabled = bool(self.settings.get('import_pfad') or self.settings.get('use_student_module') or self.settings.get('student_classes_in_subfolder'))
            except Exception:
                student_mode_enabled = False
            if student_mode_enabled and self._student_has_class('Hindernis'):
                # find hindernis object at (x,y)
                for o in self.objekte:
                    if getattr(o, 'x', None) == x and getattr(o, 'y', None) == y:
                            # if object has ist_passierbar: use its result
                            if hasattr(o, 'ist_passierbar'):
                                try:
                                    # allow level to request a compatibility inversion
                                    invert = False
                                    try:
                                        cfg = self.settings.get('Hindernis', {}) if isinstance(self.settings, dict) else {}
                                        invert = bool(cfg.get('invert_passierbar', False))
                                    except Exception:
                                        invert = False
                                    val = bool(o.ist_passierbar())
                                    if invert:
                                        val = not val
                                    # debug trace when passability seems unexpected
                                    try:
                                        print(f"[DEBUG] Hindernis at ({x},{y}) -> ist_passierbar()={val} (raw={bool(o.ist_passierbar())}, invert={invert})")
                                    except Exception:
                                        pass
                                    return val
                                except Exception:
                                    return True
                            else:
                                # student hindernis present but no method -> tile remains passierbar
                                return True
                # no hindernis object found: default to passable
                return True
            else:
                # legacy behaviour: tiles are not passierbar
                return False

        # Alle Objekte am Ziel prüfen (defensiv: skip None/misbehaving entries)
        for o in list(self.objekte):
            try:
                if getattr(o, 'tot', False):
                    # dead objects don't block movement
                    continue
            except Exception:
                continue

            try:
                ox, oy = getattr(o, 'x', None), getattr(o, 'y', None)
            except Exception:
                ox, oy = None, None

            if (ox, oy) == (x, y) and o is not obj:
                # Door handling: Tür is only passable if offen is True
                try:
                    oname = getattr(o, 'name', '') or ''
                except Exception:
                    oname = ''
                if 'Tür' in str(oname) or oname == 'Tuer':
                    try:
                        if hasattr(o, 'offen') and not getattr(o, 'offen', False):
                            return False
                    except Exception:
                        return False

                try:
                    otyp = getattr(o, 'typ', '') or ''
                except Exception:
                    otyp = ''

                # If the object exposes ist_passierbar(), use it as the authoritative
                # source of passability. This allows student-created Hindernis
                # instances (and any other custom objects) to control whether
                # they block movement regardless of their `typ` string.
                try:
                    if hasattr(o, 'ist_passierbar'):
                        try:
                            ok = bool(o.ist_passierbar())
                            # ist_passierbar() == True means passable, False means blocked
                            if not ok:
                                return False
                            else:
                                # explicit passable -> continue checking other objects
                                continue
                        except Exception:
                            # On error, be conservative and treat as passable
                            pass
                except Exception:
                    pass

                if str(otyp) in ("Monster", "Knappe"):
                    # monster and knappe block movement
                    return False

                if str(otyp) in ("Code", "Herz"):
                    # items/flags are allowed to be stood on
                    continue

                if str(otyp) == "Tor":
                    try:
                        # if tor is NOT passierbar, block movement
                        if not getattr(o, 'ist_passierbar', lambda: True)():
                            return False
                    except Exception:
                        return False

        return True


    def ist_frontal_zu_monster(self, held, monster):
        # Monster schaut in monster.richtung – frontal wenn Held aus dieser Richtung hineinläuft
        mdx, mdy = richtung_offset(monster.richtung)
        hdx, hdy = held.x - monster.x, held.y - monster.y
        return (hdx, hdy) == (mdx, mdy)

    # --- Objekt-Suchen ---
    def finde_herz(self, x, y):
        for o in self.objekte:
            if o.name == "Herz" and (o.x, o.y) == (x, y):
                return o
        return None
    
    def finde_tor_vor(self, held):
        dx, dy = richtung_offset(held.richtung)
        ziel_x, ziel_y = held.x + dx, held.y + dy
        for obj in self.objekte:
            if isinstance(obj, Tor) and obj.x == ziel_x and obj.y == ziel_y:
                return obj
        return None


    def finde_monster(self, x, y):
        for o in self.objekte:
            if o.typ == "Monster" and (o.x, o.y) == (x, y):
                return o
        return None

    def objekt_an(self, x, y):
        for o in self.objekte:
            if (o.x, o.y) == (x, y):
                return o
        return None
    
    def ist_innerhalb(self, x, y):
        return self.innerhalb(x, y)

    def gib_objekt_bei(self,x,y):
        return self.objekt_an(x,y)
    
    def finde_tuer(self, x, y):
        for o in self.objekte:
            if o.name == "Tür" and (o.x, o.y) == (x, y):
                return o
        return None

    def finde_code(self, x, y):
        for o in self.objekte:
            if o.name == "Spruch" and (o.x, o.y) == (x, y):
                return o
        return None


    def objekt_art_an(self, x, y):
        o = self.objekt_an(x, y)
        return o.name if o else None

    def entferne_objekt(self, obj):
        if obj in self.objekte:
            self.objekte.remove(obj)

    def gib_objekte(self):
        """Gibt alle Objekte im Spielfeld zurück (shallow copy).

        Rückgabe ist eine Kopie der internen Liste, damit Aufrufer die Liste
        nicht versehentlich verändern. Dies steuert nur den logischen Zugriff
        auf Objekte; keine Darstellung oder Platzierungs-Logik wird verändert.
        """
        try:
            return list(self.objekte)
        except Exception:
            return []

    def set_objekt(self, x: int, y: int, obj) -> bool:
        """Platziert `obj` logisch auf Position (x,y) falls das Terrain begehbar ist.

        Regeln:
        - Die Koordinaten müssen innerhalb des Spielfelds liegen.
        - Das Terrain an (x,y) muss begehbar sein (z.B. 'Weg').
        - Wenn bereits ein anderes Objekt auf dem Feld steht, wird das Placement
          abgelehnt (kein Überschreiben).
        - Bei Erfolg werden `obj.x` und `obj.y` gesetzt; das Objekt wird der
          internen Objektliste hinzugefügt, falls es dort noch nicht existiert.

        Diese Methode verändert ausschließlich die logische Platzierung; sie
        führt kein Rendering, Delay oder sonstige UI-Operationen aus.
        """
        try:
            # 1) Grenzen prüfen
            if not self.innerhalb(x, y):
                return False

            # 2) Terrain prüfen (nur 'Weg' gilt als begehbar)
            if self.terrain_art_an(x, y) != "Weg":
                return False

            # 3) Prüfe, ob Feld bereits belegt ist (mit anderem Objekt)
            occupant = self.objekt_an(x, y)
            if occupant is not None and occupant is not obj:
                return False

            # 4) Setze Position und füge Objekt der Liste hinzu, falls nötig
            try:
                obj.x = int(x)
                obj.y = int(y)
            except Exception:
                # fallback: set attributes directly
                try:
                    setattr(obj, 'x', x)
                    setattr(obj, 'y', y)
                except Exception:
                    return False

            if obj not in self.objekte:
                self.objekte.append(obj)

            # Falls möglich, setze framework-Referenz auf dem Objekt
            try:
                obj.framework = self.framework
            except Exception:
                pass

            return True
        except Exception:
            return False

    def gibt_noch_herzen(self):
        return any(o.name == "Herz" for o in self.objekte)
    
    def anzahl_herzen(self):
        c = 0
        for o in self.objekte:
            if o.name == "Herz":
                c+=1
        return c

    def _check_privacy_requirements(self, class_name, obj):
        """Check if privacy requirements for attributes and methods are met.
        
        Returns True if all requirements are satisfied, False otherwise.
        """
        try:
            req = self.class_requirements.get(class_name, {})
            if not req:
                return True  # No requirements = always satisfied
            
            # Get private attribute/method requirements
            private_attrs_req = req.get('attributes_private', {})
            private_methods_req = req.get('methods_private', {})
            required_methods = req.get('methods', [])
            
            if not private_attrs_req and not private_methods_req:
                return True  # No privacy requirements
            
            # Get the actual student object (not wrapper)
            student_obj = obj
            if hasattr(obj, '_student'):
                student_obj = getattr(obj, '_student')
            
            student_class = student_obj.__class__
            
            # Check private attributes
            for attr_name, required in private_attrs_req.items():
                if not required:
                    continue
                
                # Check if attribute is actually private (starts with __)
                private_attr_name = f"_{student_class.__name__}__{attr_name}"
                has_private_attr = hasattr(student_obj, private_attr_name)
                
                # Also check if there's a non-private attribute with the same name (would be wrong)
                has_public_attr = hasattr(student_obj, attr_name) and not attr_name.startswith('_')
                
                if not has_private_attr or has_public_attr:
                    return False
                
                # Only check getter/setter if they are in the required methods list
                getter_name = f'get_{attr_name}'
                if getter_name in required_methods:
                    if not (hasattr(student_obj, getter_name) and callable(getattr(student_obj, getter_name))):
                        return False
                
                # Only check setter if it's in the required methods list
                setter_name = f'set_{attr_name}'
                if setter_name in required_methods:
                    if not (hasattr(student_obj, setter_name) and callable(getattr(student_obj, setter_name))):
                        return False
            
            # Check private methods
            for method_name, required in private_methods_req.items():
                if not required:
                    continue
                
                # Check if method is actually private (starts with __)
                private_method_name = f"_{student_class.__name__}__{method_name}"
                has_private_method = hasattr(student_obj, private_method_name)
                
                # Also check if there's a non-private method with the same name (would be wrong)
                has_public_method = hasattr(student_obj, method_name) and not method_name.startswith('_')
                
                if not has_private_method or has_public_method:
                    return False
            
            return True
        except Exception:
            return False

    def _validate_typ_attribute(self, expected_class_name: str, obj) -> bool:
        """
        Validate that an object's typ attribute matches the expected class name.
        
        For Hindernis, allows: 'Baum', 'Berg', 'Busch'
        For other classes, expects exact match (e.g., 'Held', 'Knappe', 'Monster', etc.)
        
        Supports both public and private typ attributes. If typ is private and no getter
        is available, validation is skipped (to avoid breaking levels like Level 40).
        
        Args:
            expected_class_name: The canonical class name ('Held', 'Knappe', 'Hindernis', etc.)
            obj: The object to validate
            
        Returns:
            True if typ is valid or validation is skipped, False if typ is wrong
        """
        try:
            # Get the student object if this is a wrapper
            student_obj = obj
            if hasattr(obj, '_student'):
                student_obj = getattr(obj, '_student')
            
            typ_value = None
            
            # Try to get typ value in various ways
            # 1. Try direct attribute access (public typ)
            if hasattr(student_obj, 'typ'):
                try:
                    typ_value = getattr(student_obj, 'typ')
                except AttributeError:
                    pass
            
            # 2. If not found, try getter method
            if typ_value is None and hasattr(student_obj, 'get_typ'):
                try:
                    getter = getattr(student_obj, 'get_typ')
                    if callable(getter):
                        typ_value = getter()
                except Exception:
                    pass
            
            # 3. If still not found, check if typ is private without getter
            if typ_value is None:
                student_class = student_obj.__class__
                private_typ_name = f"_{student_class.__name__}__typ"
                if hasattr(student_obj, private_typ_name):
                    # typ is private and no getter available - skip validation
                    # This is needed for levels like Level 40 which only require private attributes
                    # without getters
                    return True
            
            # 4. If we still can't get typ, it's missing - validation fails
            if typ_value is None:
                return False
            
            # Validate the typ value
            if expected_class_name == 'Hindernis':
                # Hindernis allows multiple valid types
                valid_types = ['Baum', 'Berg', 'Busch']
                return typ_value in valid_types
            else:
                # All other classes must have exact match
                return typ_value == expected_class_name
                
        except Exception:
            # On any error, default to True to avoid breaking existing levels
            return True

    def check_victory_backup(self) -> bool:
        """BACKUP: Original victory check - kept for rollback if needed.
        
        Evaluate configured victory conditions.

        The configured conditions are combined with logical AND: all enabled
        conditions must be satisfied for the level to be considered won.

        Supported keys in self.victory_settings:
        - collect_hearts: bool (default True)
        - move_to: dict or None: {'enabled': True, 'x': int, 'y': int}
        - classes_present: bool (default False)
        """
        try:
            vs = self.victory_settings or {}
            # By default, if no config present, require collecting hearts (backwards compatible)
            collect_req = True if 'collect_hearts' not in vs else bool(vs.get('collect_hearts', True))

            # 1) collect_hearts
            if collect_req:
                if self.gibt_noch_herzen():
                    return False

            # 2) move_to coordinate
            mv = vs.get('move_to') if isinstance(vs, dict) else None
            if mv and isinstance(mv, dict) and mv.get('enabled'):
                try:
                    tx = int(mv.get('x', -999))
                    ty = int(mv.get('y', -999))
                except Exception:
                    return False
                # require a hero and that the framework is not blocking actions
                try:
                    held = getattr(self, 'held', None)
                    if held is None:
                        return False
                    # Use getter methods for private attributes
                    hx = self._get_attribute_value(held, 'x', None)
                    hy = self._get_attribute_value(held, 'y', None)
                    if hx is None or hy is None:
                        return False
                    hx = int(hx)
                    hy = int(hy)
                    if hx != tx or hy != ty:
                        return False
                    # also ensure framework not blocking student actions
                    if getattr(self.framework, '_aktion_blockiert', False):
                        return False
                except Exception as e:
                    return False

            # 3) classes_present: require that all canonical classes used in the level
            # (by entity spawn) are present in student files (AST check)
            if bool(vs.get('classes_present', False)):
                try:
                    # build canonical set
                    mapping = {
                        'p': 'Held', 'k': 'Knappe', 'x': 'Monster', 'h': 'Herz',
                        'd': 'Tuer', 'v': 'Villager', 'g': 'Tor',
                        's': 'Schluessel', 'q': 'Questgeber',
                        't': 'Hindernis', 'm': 'Hindernis', 'b': 'Hindernis'
                    }
                    # Check if Zettel class is configured, otherwise use Code
                    if getattr(self, '_zettel_student_mode_enabled', False):
                        mapping['c'] = 'Zettel'
                    else:
                        mapping['c'] = 'Code'
                    # Prefer the precomputed required classes (computed before
                    # _spawn_aus_level runs and mutates tiles). Fall back to
                    # scanning iter_entity_spawns only when the precomputed set
                    # is not available.
                    needed = getattr(self, '_required_spawn_classes', None)
                    if not needed:
                        needed = set()
                        for typ, x, y, sichtbar in self.level.iter_entity_spawns():
                            if not isinstance(typ, str):
                                continue
                            key = typ.lower()
                            cn = mapping.get(key)
                            if cn:
                                needed.add(cn)
                    # for each needed canonical name, require _student_has_class True
                    # if the class has ANY requirements defined (load flags, inheritance, methods, or attributes)
                    for cn in needed:
                        req = self.class_requirements.get(cn, {})
                        
                        # Check if student implementation is required based on:
                        # 1. Explicit load flags
                        # 2. Inheritance requirement
                        # 3. Method requirements
                        # 4. Attribute requirements
                        has_load_flags = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
                        has_inheritance = req.get('inherits') and req.get('inherits') != 'None'
                        has_methods = bool(req.get('methods') or req.get('methods_private'))
                        has_attributes = bool(req.get('attributes') or req.get('attributes_private'))
                        
                        requires_student = has_load_flags or has_inheritance or has_methods or has_attributes
                        
                        if requires_student:
                            has_class = self._student_has_class(cn)
                            if not has_class:
                                return False
                    
                    # Check for abstract classes (Spielobjekt, Charakter) if check_implementation is enabled
                    abstract_classes = ["Spielobjekt", "Charakter"]
                    for abstract_class in abstract_classes:
                        req = self.class_requirements.get(abstract_class, {})
                        if req.get('check_implementation', False):
                            # Check if student has implemented this abstract class
                            has_class = self._student_has_class(abstract_class)
                            if not has_class:
                                return False
                            
                            # Check privacy requirements for abstract classes even if no objects spawned
                            # This is necessary for levels like Level 47 which only require Spielobjekt
                            # implementation without spawning any Spielobjekt-derived objects
                            private_attrs_req = req.get('attributes_private', {})
                            if private_attrs_req:
                                # Try to import and validate the class directly
                                try:
                                    import importlib
                                    import sys
                                    
                                    # Determine module name based on class name
                                    module_name = abstract_class.lower()
                                    
                                    # Try to import from klassen directory
                                    if f'klassen.{module_name}' in sys.modules:
                                        mod = sys.modules[f'klassen.{module_name}']
                                    else:
                                        mod = importlib.import_module(f'klassen.{module_name}')
                                    
                                    # Get the class
                                    if hasattr(mod, abstract_class):
                                        student_class = getattr(mod, abstract_class)
                                        
                                        # Create a dummy instance to check privacy
                                        # For Spielobjekt, we need x, y parameters
                                        if abstract_class == "Spielobjekt":
                                            test_obj = student_class(0, 0)
                                        elif abstract_class == "Charakter":
                                            test_obj = student_class(0, 0, "up")
                                        else:
                                            continue
                                        
                                        # Check privacy requirements
                                        if not self._check_privacy_requirements(abstract_class, test_obj):
                                            return False
                                except Exception as e:
                                    # If we can't import/validate, fail the check
                                    return False
                    
                    # Additional validation for student Held: check required attributes and values
                    if 'Held' in needed:
                        held = getattr(self, 'held', None)
                        if held is None:
                            return False
                        
                        # Check if this is student mode with requirements
                        req = self.class_requirements.get("Held", {})
                        student_mode_for_held = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
                        
                        if student_mode_for_held:
                            # Check all required attributes exist on student object
                            # Must check the student object directly, not the MetaHeld wrapper,
                            # because MetaHeld inherits attributes from base Held class
                            required_attrs = req.get('attributes', [])
                            
                            # Get student object from MetaHeld wrapper
                            student_obj = getattr(held, '_student', None)
                            if student_obj is None:
                                return False
                            
                            for attr in required_attrs:
                                # Check if attribute is accessible on student object
                                # (either directly or via getter method)
                                accessible = False
                                # Try direct attribute access
                                if hasattr(student_obj, attr):
                                    accessible = True
                                else:
                                    # Try getter method
                                    getter_name = f'get_{attr}'
                                    if hasattr(student_obj, getter_name):
                                        try:
                                            getter = getattr(student_obj, getter_name)
                                            if callable(getter):
                                                accessible = True
                                        except Exception:
                                            pass
                                
                                if not accessible:
                                    return False
                            
                            # Check that position/direction values match level expectations
                            # ONLY if move_to victory is NOT enabled (if move_to is enabled,
                            # the student is supposed to move from initial to target position)
                            # ALSO skip if attributes are private without getters (Level 40)
                            mv_enabled = mv and isinstance(mv, dict) and mv.get('enabled')
                            if not mv_enabled:
                                expected_x = getattr(held, '_level_expected_x', None)
                                expected_y = getattr(held, '_level_expected_y', None)
                                expected_richtung = getattr(held, '_level_expected_richtung', None)
                                
                                # Only validate position if attributes are accessible (public or via getter)
                                # For Level 40: private attributes without getters → skip validation
                                required_methods = req.get('methods', [])
                                has_position_getters = ('get_x' in required_methods or 'get_y' in required_methods)
                                
                                # Skip position validation if:
                                # 1. No getter methods defined AND
                                # 2. Attributes are private (can't access directly)
                                skip_position_check = not has_position_getters and not hasattr(student_obj, 'x')
                                
                                if not skip_position_check:
                                    if expected_x is not None:
                                        try:
                                            actual_x = getattr(held, 'x')
                                        except AttributeError:
                                            return False
                                        if actual_x != expected_x:
                                            return False
                                    
                                    if expected_y is not None:
                                        try:
                                            actual_y = getattr(held, 'y')
                                        except AttributeError:
                                            return False
                                        if actual_y != expected_y:
                                            return False
                                    
                                    if expected_richtung is not None:
                                        try:
                                            actual_richtung = getattr(held, 'richtung')
                                        except AttributeError:
                                            return False
                                        if actual_richtung != expected_richtung:
                                            return False
                            
                            # Check privacy requirements (private attributes/methods with getters/setters)
                            if not self._check_privacy_requirements('Held', held):
                                return False
                            
                            # Validate typ attribute matches 'Held'
                            if not self._validate_typ_attribute('Held', held):
                                return False
                    
                    # Remap 'Code' to 'Zettel' if Zettel student mode is active
                    if getattr(self, '_zettel_student_mode_enabled', False) and 'Code' in needed:
                        needed.remove('Code')
                        needed.add('Zettel')
                    
                    # Check privacy requirements for other classes (Hindernis, etc.)
                    for class_name in needed:
                        if class_name == 'Held':
                            continue  # Already checked above
                        
                        # Check if this class has privacy requirements
                        req = self.class_requirements.get(class_name, {})
                        if not req:
                            continue
                        
                        # Check if it's student mode for this class (same logic as spawn validation)
                        has_load_flags = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
                        has_inheritance = req.get('inherits') and req.get('inherits') != 'None'
                        has_methods = bool(req.get('methods') or req.get('methods_private'))
                        has_attributes = bool(req.get('attributes') or req.get('attributes_private'))
                        
                        student_mode = has_load_flags or has_inheritance or has_methods or has_attributes
                        if not student_mode:
                            continue
                        # Find all objects of this class type
                        objects_to_check = []
                        if class_name == 'Hindernis':
                            # Check if Hindernis class validation passed during spawn
                            if not getattr(self, '_hindernis_class_valid', True):
                                return False
                            # Hindernisse are in self.objekte, filter by class
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ == 'Hindernis']
                        elif class_name == 'Herz':
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ == 'Herz']
                        elif class_name == 'Tuer':
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ == 'Tuer']
                        elif class_name == 'Tor':
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ == 'Tor']
                        elif class_name == 'Schluessel':
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ == 'Schluessel']
                        elif class_name == 'Knappe':
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ == 'Knappe']
                        elif class_name == 'Monster' or class_name == 'Bogenschuetze':
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ in ['Monster', 'Bogenschuetze']]
                        elif class_name == 'Villager':
                            objects_to_check = [obj for obj in self.objekte if obj.__class__.__name__ == 'Villager']
                        
                        # For Hindernis and Zettel, we already checked validation during spawn and stored result
                        # Don't check objects_to_check as they might be proxy objects
                        if class_name == 'Hindernis':
                            # Already validated during spawn - but also do functional test
                            # Test that get_typ() returns correct values
                            if 'get_typ' in req.get('methods', []):
                                # Find at least one Hindernis object and check get_typ()
                                hindernisse = [o for o in self.objekte if hasattr(o, '_student') and hasattr(o._student, 'get_typ')]
                                if hindernisse:
                                    # Test first Hindernis
                                    h = hindernisse[0]._student
                                    try:
                                        typ_value = h.get_typ()
                                        # Must return one of the valid obstacle types
                                        if typ_value not in ['Baum', 'Berg', 'Busch']:
                                            return False
                                    except Exception:
                                        # get_typ() threw an exception - fail
                                        return False
                            continue
                        elif class_name == 'Zettel':
                            # Check validation result from spawn
                            if not getattr(self, '_zettel_class_valid', True):
                                return False
                            # Also do functional test for get_spruch() and set_spruch()
                            if 'get_spruch' in req.get('methods', []) and 'set_spruch' in req.get('methods', []):
                                # Find a Zettel object and test set/get
                                zettel = [o for o in self.objekte if hasattr(o, 'get_spruch') and hasattr(o, 'set_spruch')]
                                if zettel:
                                    z = zettel[0]
                                    try:
                                        # Test set_spruch and get_spruch
                                        original = z.get_spruch() if callable(getattr(z, 'get_spruch', None)) else None
                                        test_text = "VICTORY_TEST"
                                        z.set_spruch(test_text)
                                        retrieved = z.get_spruch()
                                        # Restore original
                                        if original is not None:
                                            z.set_spruch(original)
                                        # Check if set/get worked
                                        if retrieved != test_text:
                                            return False
                                    except Exception:
                                        # set/get threw an exception - fail
                                        return False
                            continue
                        elif class_name == 'Knappe':
                            # Check validation result from spawn
                            if not getattr(self, '_knappe_class_valid', True):
                                return False
                            # Movement functionality is tested via move_to if enabled
                            # No additional functional test needed here
                            continue
                        else:
                            # Check privacy for at least one object of this class
                            if objects_to_check:
                                # Check privacy requirements for the first object
                                if not self._check_privacy_requirements(class_name, objects_to_check[0]):
                                    return False
                                
                                # Validate typ attribute matches expected class name
                                if not self._validate_typ_attribute(class_name, objects_to_check[0]):
                                    return False
                
                except Exception:
                    return False

            # 4) rebuild_mode: require that all template objects have been created by student
            if bool(vs.get('rebuild_mode', False)):
                if not self.template_objects:
                    return False
                
                for tpl in self.template_objects:
                    try:
                        x, y = tpl.get('x'), tpl.get('y')
                        expected_typ = tpl.get('typ')
                        
                        # Helper für Attributzugriff mit Getter-Support
                        def get_obj_attr(obj, attr_name):
                            try:
                                return getattr(obj, attr_name)
                            except AttributeError:
                                getter_name = f'get_{attr_name}'
                                if hasattr(obj, getter_name):
                                    getter = getattr(obj, getter_name)
                                    if callable(getter):
                                        return getter()
                            return None
                        
                        found = False
                        for obj in self.objekte:
                            obj_x = get_obj_attr(obj, 'x')
                            obj_y = get_obj_attr(obj, 'y')
                            
                            if obj_x == x and obj_y == y:
                                # Prüfe Typ
                                obj_typ = getattr(obj, 'typ', None) or obj.__class__.__name__
                                if obj_typ == expected_typ:
                                    found = True
                                    
                                    # Prüfe optionale Attribute wie Richtung
                                    if 'richtung' in tpl:
                                        expected_richt = tpl.get('richtung')
                                        actual_richt = get_obj_attr(obj, 'richtung')
                                        if actual_richt != expected_richt:
                                            return False
                                    break
                        
                        if not found:
                            return False
                    except Exception:
                        return False

            # all enabled conditions satisfied
            return True
        except Exception:
            return False
    
    def check_victory(self) -> bool:
        """NEW: Try-except based victory check with precise error messages.
        
        Phase 1: Framework not blocked + hearts collected (kept from original)
        Phase 2: Check if class validation passed (validated once at level start)
        """
        try:
            vs = self.victory_settings or {}
            
            # ===== PHASE 1: Basic Victory Conditions (from original) =====
            # 1) Collect hearts requirement
            collect_req = True if 'collect_hearts' not in vs else bool(vs.get('collect_hearts', True))
            if collect_req:
                if self.gibt_noch_herzen():
                    return False
            
            # 2) Move to coordinate requirement
            mv = vs.get('move_to') if isinstance(vs, dict) else None
            if mv and isinstance(mv, dict) and mv.get('enabled'):
                try:
                    tx = int(mv.get('x', -999))
                    ty = int(mv.get('y', -999))
                except Exception:
                    return False
                
                held = getattr(self, 'held', None)
                if held is None:
                    return False
                
                hx = self._get_attribute_value(held, 'x', None)
                hy = self._get_attribute_value(held, 'y', None)
                if hx is None or hy is None:
                    return False
                
                hx, hy = int(hx), int(hy)
                if hx != tx or hy != ty:
                    return False
                
                if getattr(self.framework, '_aktion_blockiert', False):
                    return False
            
            # ===== PHASE 2: Class Implementation Check =====
            # Check if class validation passed (set during level initialization)
            if bool(vs.get('classes_present', False)):
                if not getattr(self, '_class_validation_passed', False):
                    # Class validation failed - error messages already printed during init
                    return False
            
            # 3) rebuild_mode check (kept from original)
            if bool(vs.get('rebuild_mode', False)):
                if not self._check_rebuild_mode():
                    return False
            
            # All checks passed - print message only once
            if not self._victory_message_shown:
                print("[VICTORY] Alle Siegbedingungen erfüllt!")
                self._victory_message_shown = True
            return True
            
        except Exception as e:
            import os
            if os.getenv("OOP_TEST", "") == "1":
                print(f"[VICTORY ERROR] Unerwarteter Fehler in check_victory(): {e}")
                import traceback
                traceback.print_exc()
            return False
    
    def _get_needed_classes(self):
        """Ermittelt alle benötigten Klassen für das Level."""
        mapping = {
            'p': 'Held', 'k': 'Knappe', 'x': 'Monster', 'h': 'Herz',
            'd': 'Tuer', 'v': 'Villager', 'g': 'Tor',
            's': 'Schluessel', 'q': 'Questgeber',
            't': 'Hindernis', 'm': 'Hindernis', 'b': 'Hindernis'
        }
        
        if getattr(self, '_zettel_student_mode_enabled', False):
            mapping['c'] = 'Zettel'
        else:
            mapping['c'] = 'Code'
        
        needed = getattr(self, '_required_spawn_classes', None)
        if not needed:
            needed = set()
            # Check spawn_entities
            for typ, x, y, sichtbar in self.level.iter_entity_spawns():
                if isinstance(typ, str):
                    cn = mapping.get(typ.lower())
                    if cn:
                        needed.add(cn)
            
            # Also check tiles for Hindernis, Zettel, etc.
            for row in self.level.tiles:
                for code in row:
                    if code in mapping:
                        needed.add(mapping[code])
        
        # Add abstract/utility classes if check_implementation enabled
        for abstract_class in ["Spielobjekt", "Charakter", "Inventar", "Gegenstand"]:
            req = self.class_requirements.get(abstract_class, {})
            if req.get('check_implementation', False):
                needed.add(abstract_class)
        
        return needed
    
    def _requires_student_implementation(self, class_name, req):
        """Prüft ob Schüler-Implementierung erforderlich ist."""
        # For utility classes (Inventar, Gegenstand), only check if check_implementation is explicitly set
        if class_name in ["Inventar", "Gegenstand"]:
            return bool(req.get('check_implementation', False))
        
        has_load_flags = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
        has_inheritance = req.get('inherits') and req.get('inherits') != 'None'
        has_methods = bool(req.get('methods') or req.get('methods_private'))
        has_attributes = bool(req.get('attributes') or req.get('attributes_private'))
        
        return has_load_flags or has_inheritance or has_methods or has_attributes
    
    def _get_test_objects_for_class(self, class_name):
        """Holt vorhandene Objekte der Klasse aus dem Level."""
        if class_name == 'Held':
            held = getattr(self, 'held', None)
            if held:
                # Get student object from MetaHeld wrapper
                student_obj = getattr(held, '_student', held)
                return [student_obj]
        
        # Search in self.objekte
        objects = []
        for obj in self.objekte:
            if obj.__class__.__name__ == class_name:
                # Unwrap if it's a proxy
                student_obj = getattr(obj, '_student', obj)
                objects.append(student_obj)
        
        return objects
    
    def _create_test_object(self, class_name, req):
        """Erstellt ein Test-Objekt der Klasse für Validierung."""
        try:
            import importlib
            import sys
            
            module_name = class_name.lower()
            if f'klassen.{module_name}' in sys.modules:
                mod = sys.modules[f'klassen.{module_name}']
            else:
                mod = importlib.import_module(f'klassen.{module_name}')
            
            if not hasattr(mod, class_name):
                return None
            
            student_class = getattr(mod, class_name)
            
            # Create test instance with default parameters
            if class_name == "Spielobjekt":
                return student_class(0, 0)
            elif class_name == "Charakter":
                return student_class(0, 0, "up")
            elif class_name == "Held":
                return student_class(0, 0, "up", False)
            elif class_name == "Knappe":
                return student_class(0, 0, "up")
            elif class_name == "Hindernis":
                return student_class(0, 0, "Baum")
            elif class_name == "Zettel":
                return student_class(0, 0)
            elif class_name == "Inventar":
                return student_class()
            elif class_name == "Gegenstand":
                return student_class("TestItem")
            else:
                # Try with minimal params
                return student_class(0, 0)
                
        except Exception as e:
            print(f"[VICTORY] Konnte Test-Objekt für '{class_name}' nicht erstellen: {e}")
            return None
    
    def _validate_classes_at_level_start(self):
        """Validates student classes ONCE at level start.
        
        Runs functional tests on SEPARATE test objects (not game objects!).
        Called once after _spawn_aus_level() in __init__.
        """
        import os
        
        vs = self.victory_settings or {}
        
        # Only validate if classes_present is enabled
        if not bool(vs.get('classes_present', False)):
            self._class_validation_passed = True
            return
        
        try:
            # Get required classes
            needed_classes = self._get_needed_classes()
            
            # Check each required class
            for class_name in needed_classes:
                req = self.class_requirements.get(class_name, {})
                
                # Skip if no requirements
                if not self._requires_student_implementation(class_name, req):
                    continue
                
                # Check if class exists
                if not self._student_has_class(class_name):
                    print(f"[VICTORY] Klasse '{class_name}' nicht gefunden.")
                    self._class_validation_passed = False
                    return
                
                # ALWAYS create a SEPARATE test object for validation
                # Never use game objects (self.held, etc.) for functional tests!
                test_obj = self._create_test_object(class_name, req)
                
                if not test_obj:
                    print(f"[VICTORY] Konnte Test-Objekt für Klasse '{class_name}' nicht erstellen.")
                    self._class_validation_passed = False
                    return
                
                # Check attributes (public and private)
                if not self._check_attributes_new(class_name, test_obj, req):
                    self._class_validation_passed = False
                    return
                
                # Check methods (including functional tests)
                if not self._check_methods_new(class_name, test_obj, req):
                    self._class_validation_passed = False
                    return
                
                # Check inheritance
                if not self._check_inheritance_new(class_name, test_obj, req):
                    self._class_validation_passed = False
                    return
            
            # All validations passed
            self._class_validation_passed = True
            if os.getenv("OOP_TEST", "") == "1":
                print("[VICTORY] Klassenvalidierung erfolgreich abgeschlossen.")
                
        except Exception as e:
            print(f"[VICTORY ERROR] Fehler bei Klassenvalidierung: {e}")
            import traceback
            traceback.print_exc()
            self._class_validation_passed = False
    
    def _check_attributes_new(self, class_name, test_obj, req):
        """Prüft Attribute mit try-except für präzise Fehlermeldungen."""
        # Public attributes
        public_attrs = req.get('attributes', [])
        for attr in public_attrs:
            try:
                # Try to access attribute directly
                value = getattr(test_obj, attr)
                
                # Special validation for 'rucksack' attribute (Inventar)
                if attr == 'rucksack' and value is not None:
                    # Check if it's an Inventar instance
                    if not hasattr(value, 'items') or not hasattr(value, 'item_hinzufuegen'):
                        print(f"[VICTORY] Klasse '{class_name}': Attribut 'rucksack' ist kein gültiges Inventar-Objekt.")
                        return False
                    
                    # Held-specific check: must have a Schwert in inventory
                    if class_name == 'Held':
                        has_schwert = False
                        try:
                            for item in value.items:
                                if hasattr(item, 'art') and item.art == 'Schwert':
                                    has_schwert = True
                                    break
                        except Exception:
                            pass
                        
                        if not has_schwert:
                            print(f"[VICTORY] Klasse 'Held': Inventar (rucksack) muss ein Schwert enthalten.")
                            return False
                    
                    # Knappe-specific check: inventory must be empty
                    elif class_name == 'Knappe':
                        try:
                            if len(value.items) > 0:
                                print(f"[VICTORY] Klasse 'Knappe': Inventar (rucksack) muss leer sein.")
                                return False
                        except Exception:
                            pass
                
                # Success - attribute is accessible
            except AttributeError:
                print(f"[VICTORY] Klasse '{class_name}': Öffentliches Attribut '{attr}' nicht vorhanden oder nicht erreichbar.")
                return False
        
        # Private attributes
        # Note: attributes_private: {x: true} only means "x should be private (__x)"
        # It does NOT mean "x needs a getter" - getters are checked in methods list
        private_attrs = req.get('attributes_private', {})
        for attr, is_private in private_attrs.items():
            # Only check if is_private is True (it's just a flag)
            if not is_private:
                continue
                
            # First check: attribute should NOT be directly accessible
            try:
                value = getattr(test_obj, attr)
                # If we get here, attribute is public (BAD!)
                print(f"[VICTORY] Klasse '{class_name}': Attribut '{attr}' sollte privat sein (mit __), ist aber öffentlich zugänglich.")
                return False
            except AttributeError:
                # Good - attribute is not directly accessible
                # Now check if it exists as private attribute via name mangling
                mangled_name = f"_{class_name}__{attr}"
                if not hasattr(test_obj, mangled_name):
                    print(f"[VICTORY] Klasse '{class_name}': Privates Attribut '__{attr}' nicht vorhanden.")
                    return False
        
        return True
    
    def _check_methods_new(self, class_name, test_obj, req):
        """Prüft Methoden mit funktionalen Tests."""
        # Public methods
        public_methods = req.get('methods', [])
        for method_name in public_methods:
            if not hasattr(test_obj, method_name):
                print(f"[VICTORY] Klasse '{class_name}': Methode '{method_name}()' nicht vorhanden.")
                return False
            
            method = getattr(test_obj, method_name)
            if not callable(method):
                print(f"[VICTORY] Klasse '{class_name}': '{method_name}' ist keine Methode.")
                return False
        
        # Private methods with setters
        private_methods = req.get('methods_private', {})
        for method_name, should_have_setter in private_methods.items():
            # Check if method exists
            if not hasattr(test_obj, method_name):
                print(f"[VICTORY] Klasse '{class_name}': Methode '{method_name}()' nicht vorhanden.")
                return False
        
        # Functional tests for movement methods
        if class_name in ['Held', 'Knappe', 'Charakter']:
            if not self._test_movement_methods(class_name, test_obj, req):
                return False
        
        # Functional tests for setter/getter methods
        if not self._test_setter_getter_methods(class_name, test_obj, req):
            return False
        
        return True
    
    def _test_geh_realistic_collision(self, class_name, test_obj, req):
        """Testet ob geh() korrekt Kollisionen mit Level-Objekten erkennt.
        
        Testet mit den tatsächlichen Objekten aus dem Level:
        1. Kann Level-Grenzen nicht verlassen
        2. Wird von nicht-passierbaren Objekten blockiert (außer Zettel - Polymorphie-Beispiel)
        3. Kann durch passierbare Objekte laufen
        
        NOTE: set_level() wurde bereits in _test_movement_methods() aufgerufen!
        """
        try:
            # Collect unique object types from level (excluding Zettel for polymorphism teaching)
            level_object_types = set()
            for obj in self.objekte:
                obj_type = getattr(obj, 'typ', None) or obj.__class__.__name__
                if obj_type and obj_type.lower() != 'zettel':
                    level_object_types.add(obj_type)
            
            # Debug: Print object types found
            # print(f"[DEBUG] Testing {class_name} collision with object types: {level_object_types}")
            
            # Test 1: Cannot leave level bounds
            if not self._test_level_boundary_collision(class_name, test_obj):
                return False
            
            # Test 2: Check collision with each object type in level (except Zettel)
            for obj_type in level_object_types:
                if not self._test_object_type_collision(class_name, test_obj, obj_type):
                    return False
            
            return True
            
        except Exception as e:
            print(f"[VICTORY] Klasse '{class_name}': Kollisionstest fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_level_boundary_collision(self, class_name, test_obj):
        """Testet ob Test-Objekt die Level-Grenzen respektiert."""
        try:
            # Save original position
            original_x = self._get_attr_value(test_obj, 'x', class_name)
            original_y = self._get_attr_value(test_obj, 'y', class_name)
            original_richtung = self._get_attr_value(test_obj, 'richtung', class_name)
            
            # Test boundary: Try to move outside level to the left (x=-1)
            try:
                if hasattr(test_obj, 'x'):
                    test_obj.x = 0
                    test_obj.richtung = 'left'
                else:
                    test_obj.set_x(0)
                    test_obj.set_richtung('left')
                
                test_obj.geh()
                
                new_x = self._get_attr_value(test_obj, 'x', class_name)
                if new_x < 0:
                    # Restore position
                    if hasattr(test_obj, 'x'):
                        test_obj.x = original_x
                        test_obj.y = original_y
                        test_obj.richtung = original_richtung
                    print(f"[VICTORY] Klasse '{class_name}': {class_name} kann das Level verlassen (x={new_x} ist außerhalb).")
                    return False
            except Exception as e:
                # Restore position
                if hasattr(test_obj, 'x'):
                    test_obj.x = original_x
                    test_obj.y = original_y
                    test_obj.richtung = original_richtung
                print(f"[VICTORY] Klasse '{class_name}': geh() wirft Fehler beim Boundary-Test: {e}")
                return False
            
            # Restore original position
            if hasattr(test_obj, 'x'):
                test_obj.x = original_x
                test_obj.y = original_y
                test_obj.richtung = original_richtung
            else:
                test_obj.set_x(original_x)
                test_obj.set_y(original_y)
                test_obj.set_richtung(original_richtung)
            
            return True
            
        except Exception as e:
            print(f"[VICTORY] Klasse '{class_name}': Boundary-Test fehlgeschlagen: {e}")
            return False
    
    def _test_object_type_collision(self, class_name, test_obj, obj_type):
        """Testet Kollision mit einem bestimmten Objekt-Typ."""
        try:
            # Find an object of this type in the level
            target_obj = None
            for obj in self.objekte:
                obj_t = getattr(obj, 'typ', None) or obj.__class__.__name__
                if obj_t == obj_type:
                    target_obj = obj
                    break
            
            if not target_obj:
                return True  # No object of this type, skip
            
            # Get target position
            target_x = self._get_attr_value(target_obj, 'x', obj_type)
            target_y = self._get_attr_value(target_obj, 'y', obj_type)
            
            # Check if object is passable
            is_passable = False
            if hasattr(target_obj, 'ist_passierbar') and callable(getattr(target_obj, 'ist_passierbar')):
                try:
                    is_passable = target_obj.ist_passierbar()
                except:
                    is_passable = False
            
            # Save original position
            original_x = self._get_attr_value(test_obj, 'x', class_name)
            original_y = self._get_attr_value(test_obj, 'y', class_name)
            original_richtung = self._get_attr_value(test_obj, 'richtung', class_name)
            
            # Position test object next to target and face it
            test_x, test_y, direction = target_x - 1, target_y, 'right'
            if test_x < 0:  # Try from right
                test_x, test_y, direction = target_x + 1, target_y, 'left'
            if test_x >= self.level.breite:  # Try from top
                test_x, test_y, direction = target_x, target_y - 1, 'down'
            if test_y < 0:  # Try from bottom
                test_x, test_y, direction = target_x, target_y + 1, 'up'
            
            # Set test position
            try:
                if hasattr(test_obj, 'x'):
                    test_obj.x = test_x
                    test_obj.y = test_y
                    test_obj.richtung = direction
                else:
                    test_obj.set_x(test_x)
                    test_obj.set_y(test_y)
                    test_obj.set_richtung(direction)
            except Exception as e:
                # Restore and skip this test
                if hasattr(test_obj, 'x'):
                    test_obj.x = original_x
                    test_obj.y = original_y
                    test_obj.richtung = original_richtung
                return True
            
            # Try to move into target object
            try:
                test_obj.geh()
            except Exception as e:
                # Restore position
                if hasattr(test_obj, 'x'):
                    test_obj.x = original_x
                    test_obj.y = original_y
                    test_obj.richtung = original_richtung
                print(f"[VICTORY] Klasse '{class_name}': geh() wirft Fehler beim Test mit {obj_type}: {e}")
                return False
            
            # Check new position
            new_x = self._get_attr_value(test_obj, 'x', class_name)
            new_y = self._get_attr_value(test_obj, 'y', class_name)
            
            # Verify behavior based on passability
            if is_passable:
                # Should have moved into target position
                if new_x != target_x or new_y != target_y:
                    # Restore position
                    if hasattr(test_obj, 'x'):
                        test_obj.x = original_x
                        test_obj.y = original_y
                        test_obj.richtung = original_richtung
                    print(f"[VICTORY] Klasse '{class_name}': {class_name} kann nicht durch passierbares Objekt '{obj_type}' laufen.")
                    return False
            else:
                # Should NOT have moved
                if new_x != test_x or new_y != test_y:
                    # Restore position
                    if hasattr(test_obj, 'x'):
                        test_obj.x = original_x
                        test_obj.y = original_y
                        test_obj.richtung = original_richtung
                    print(f"[VICTORY] Klasse '{class_name}': {class_name} kann in nicht-passierbare Objekte vom Typ '{obj_type}' laufen.")
                    return False
            
            # Restore original position
            if hasattr(test_obj, 'x'):
                test_obj.x = original_x
                test_obj.y = original_y
                test_obj.richtung = original_richtung
            else:
                test_obj.set_x(original_x)
                test_obj.set_y(original_y)
                test_obj.set_richtung(original_richtung)
            
            return True
            
        except Exception as e:
            print(f"[VICTORY] Klasse '{class_name}': Test mit Objekt-Typ '{obj_type}' fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_geh_collision_detection_NEW(self, class_name, test_obj, req):
        """ALTE VERSION - wird nicht mehr verwendet. Testet ob geh() korrekt Hindernisse erkennt (nur wenn expects_set_level=true).
        
        Erstellt ein Pseudo-Level mit Hindernissen und prüft, ob das Objekt:
        1. set_level() Methode hat und aufrufen kann
        2. Korrekt Hindernisse erkennt und Position nicht ändert
        """
        # Check if set_level method exists
        if not hasattr(test_obj, 'set_level') or not callable(getattr(test_obj, 'set_level')):
            print(f"[VICTORY] Klasse '{class_name}': 'set_level()' Methode fehlt (erwartet für Kollisionserkennung).")
            return False
        
        try:
            # Create a pseudo-level with obstacles
            # Layout: 3x3 grid with obstacle in front of character
            #   0 1 2
            # 0 . . .
            # 1 . C H  (Character at 1,1 facing right, Hindernis at 2,1)
            # 2 . . .
            
            # Import Hindernis class
            try:
                from klassen.hindernis import Hindernis
            except ImportError:
                try:
                    from hindernis import Hindernis
                except ImportError:
                    print(f"[VICTORY] Klasse '{class_name}': Konnte Hindernis-Klasse nicht importieren für Kollisionstest.")
                    return False
            
            # Create obstacle
            obstacle = Hindernis(2, 1, "Baum")
            
            # Temporarily add obstacle to spielfeld objects for gib_objekt_bei() to find
            original_objekte = self.objekte[:]
            self.objekte.append(obstacle)
            
            # Set character to position 1,1 facing right (towards obstacle)
            try:
                if hasattr(test_obj, 'x'):
                    test_obj.x = 1
                elif hasattr(test_obj, 'set_x'):
                    test_obj.set_x(1)
                    
                if hasattr(test_obj, 'y'):
                    test_obj.y = 1
                elif hasattr(test_obj, 'set_y'):
                    test_obj.set_y(1)
                    
                if hasattr(test_obj, 'richtung'):
                    test_obj.richtung = 'right'
                elif hasattr(test_obj, 'set_richtung'):
                    test_obj.set_richtung('right')
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': Konnte Test-Position nicht setzen: {e}")
                return False
            
            # Call set_level with the actual spielfeld (which has gib_objekt_bei method)
            # or with a list of objects (for older implementations)
            try:
                # Try passing the spielfeld first (for implementations expecting level.gib_objekt_bei())
                test_obj.set_level(self)
            except Exception as e:
                # If that fails, try passing a list of objects (for older implementations)
                try:
                    test_obj.set_level([obstacle])
                except Exception as e2:
                    self.objekte = original_objekte
                    print(f"[VICTORY] Klasse '{class_name}': set_level() wirft Fehler: {e}")
                    return False
            
            # Get position before geh()
            try:
                before_x = self._get_attr_value(test_obj, 'x', class_name)
                before_y = self._get_attr_value(test_obj, 'y', class_name)
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': Konnte Position vor geh() nicht ermitteln: {e}")
                return False
            
            # Call geh() - should NOT move because obstacle blocks
            try:
                test_obj.geh()
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': geh() wirft Fehler bei Kollision: {e}")
                return False
            
            # Get position after geh()
            try:
                after_x = self._get_attr_value(test_obj, 'x', class_name)
                after_y = self._get_attr_value(test_obj, 'y', class_name)
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': Konnte Position nach geh() nicht ermitteln: {e}")
                return False
            
            # Verify position did NOT change (obstacle should block)
            if before_x != after_x or before_y != after_y:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': geh() erkennt Hindernis nicht. Position änderte sich von ({before_x},{before_y}) zu ({after_x},{after_y}), sollte aber gleich bleiben.")
                return False
            
            # Test 2: Movement in free direction should work
            # Turn character to face up (free space)
            try:
                if hasattr(test_obj, 'richtung'):
                    test_obj.richtung = 'up'
                elif hasattr(test_obj, 'set_richtung'):
                    test_obj.set_richtung('up')
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': Konnte Richtung nicht auf 'up' setzen: {e}")
                return False
            
            # Get position before free movement
            try:
                before_x = self._get_attr_value(test_obj, 'x', class_name)
                before_y = self._get_attr_value(test_obj, 'y', class_name)
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': Konnte Position vor freier Bewegung nicht ermitteln: {e}")
                return False
            
            # Call geh() - should move up (no obstacle)
            try:
                test_obj.geh()
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': geh() wirft Fehler bei freier Bewegung: {e}")
                return False
            
            # Get position after free movement
            try:
                after_x = self._get_attr_value(test_obj, 'x', class_name)
                after_y = self._get_attr_value(test_obj, 'y', class_name)
            except Exception as e:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': Konnte Position nach freier Bewegung nicht ermitteln: {e}")
                return False
            
            # Verify position DID change (should move up)
            expected_y = before_y - 1
            if after_x != before_x or after_y != expected_y:
                self.objekte = original_objekte
                print(f"[VICTORY] Klasse '{class_name}': geh() bewegt sich nicht korrekt im freien Raum. Position: ({before_x},{before_y}) -> ({after_x},{after_y}), erwartet: ({before_x},{expected_y})")
                return False
            
            # Restore original objects
            self.objekte = original_objekte
            return True
            
        except Exception as e:
            # Restore original objects in case of exception
            if 'original_objekte' in locals():
                self.objekte = original_objekte
            print(f"[VICTORY] Klasse '{class_name}': Kollisionstest fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_movement_methods(self, class_name, test_obj, req):
        """Testet Bewegungsmethoden funktional."""
        methods = req.get('methods', [])
        expects_set_level = req.get('expects_set_level', False)
        
        # If expects_set_level is true, call set_level BEFORE any tests
        if expects_set_level:
            if not hasattr(test_obj, 'set_level') or not callable(getattr(test_obj, 'set_level')):
                print(f"[VICTORY] Klasse '{class_name}': 'set_level()' Methode fehlt (erwartet für Kollisionserkennung).")
                return False
            try:
                test_obj.set_level(self)
            except Exception as e:
                print(f"[VICTORY] Klasse '{class_name}': set_level() wirft Fehler: {e}")
                return False
        
        # Test geh() method
        if 'geh' in methods:
            # If expects_set_level=true, skip basic movement test and only do realistic collision test
            if expects_set_level:
                if not self._test_geh_realistic_collision(class_name, test_obj, req):
                    return False
            else:
                # Test 1: Basic movement (only for implementations WITHOUT collision detection)
                try:
                    initial_x = self._get_attr_value(test_obj, 'x', class_name)
                    initial_y = self._get_attr_value(test_obj, 'y', class_name)
                    richtung = self._get_attr_value(test_obj, 'richtung', class_name)
                except Exception as e:
                    print(f"[VICTORY] Klasse '{class_name}': Konnte Anfangsposition nicht ermitteln: {e}")
                    return False
                
                # Call geh()
                try:
                    test_obj.geh()
                except Exception as e:
                    print(f"[VICTORY] Klasse '{class_name}': Methode 'geh()' wirft Fehler: {e}")
                    return False
                
                # Check new position
                try:
                    new_x = self._get_attr_value(test_obj, 'x', class_name)
                    new_y = self._get_attr_value(test_obj, 'y', class_name)
                    
                    # Verify movement based on direction
                    expected_x, expected_y = initial_x, initial_y
                    if richtung == 'up':
                        expected_y -= 1
                    elif richtung == 'down':
                        expected_y += 1
                    elif richtung == 'left':
                        expected_x -= 1
                    elif richtung == 'right':
                        expected_x += 1
                    
                    if new_x != expected_x or new_y != expected_y:
                        print(f"[VICTORY] Klasse '{class_name}': geh() bewegt nicht korrekt. Richtung: {richtung}, Alt: ({initial_x},{initial_y}), Neu: ({new_x},{new_y}), Erwartet: ({expected_x},{expected_y})")
                        return False
                        
                except Exception as e:
                    print(f"[VICTORY] Klasse '{class_name}': Konnte neue Position nach geh() nicht ermitteln: {e}")
                    return False
        
        # Test links() and rechts() methods
        if 'links' in methods:
            try:
                initial_richt = self._get_attr_value(test_obj, 'richtung', class_name)
                test_obj.links()
                new_richt = self._get_attr_value(test_obj, 'richtung', class_name)
                
                # Verify rotation
                rotation_map = {'up': 'left', 'left': 'down', 'down': 'right', 'right': 'up'}
                expected_richt = rotation_map.get(initial_richt)
                if new_richt != expected_richt:
                    print(f"[VICTORY] Klasse '{class_name}': links() dreht nicht korrekt. Alt: {initial_richt}, Neu: {new_richt}, Erwartet: {expected_richt}")
                    return False
            except Exception as e:
                print(f"[VICTORY] Klasse '{class_name}': links() Test fehlgeschlagen: {e}")
                return False
        
        if 'rechts' in methods:
            try:
                initial_richt = self._get_attr_value(test_obj, 'richtung', class_name)
                test_obj.rechts()
                new_richt = self._get_attr_value(test_obj, 'richtung', class_name)
                
                # Verify rotation
                rotation_map = {'up': 'right', 'right': 'down', 'down': 'left', 'left': 'up'}
                expected_richt = rotation_map.get(initial_richt)
                if new_richt != expected_richt:
                    print(f"[VICTORY] Klasse '{class_name}': rechts() dreht nicht korrekt. Alt: {initial_richt}, Neu: {new_richt}, Erwartet: {expected_richt}")
                    return False
            except Exception as e:
                print(f"[VICTORY] Klasse '{class_name}': rechts() Test fehlgeschlagen: {e}")
                return False
        
        return True
    
    def _test_setter_getter_methods(self, class_name, test_obj, req):
        """Testet Setter/Getter Methoden funktional.
        
        Only tests attributes that have BOTH getter AND setter in methods list.
        """
        private_attrs = req.get('attributes_private', {})
        methods = req.get('methods', [])
        
        for attr, is_private in private_attrs.items():
            getter_name = f'get_{attr}'
            setter_name = f'set_{attr}'
            
            # Only test if BOTH getter AND setter are in methods list
            has_getter = getter_name in methods
            has_setter = setter_name in methods
            
            if has_getter and has_setter:
                try:
                    # Get original value
                    original = getattr(test_obj, getter_name)()
                    
                    # Choose test value based on attribute type
                    if attr == 'richtung':
                        # Richtung must be valid direction string
                        test_value = "left" if original != "left" else "right"
                    elif attr == 'weiblich':
                        # Boolean attribute
                        test_value = not original
                    elif isinstance(original, str):
                        test_value = "TEST_VALUE"
                    elif isinstance(original, bool):
                        test_value = not original
                    elif isinstance(original, int):
                        test_value = 999
                    else:
                        test_value = original  # Skip test if type unknown
                    
                    # Set test value
                    getattr(test_obj, setter_name)(test_value)
                    
                    # Get new value
                    new_value = getattr(test_obj, getter_name)()
                    
                    # Restore original
                    getattr(test_obj, setter_name)(original)
                    
                    # Verify
                    if new_value != test_value:
                        print(f"[VICTORY] Klasse '{class_name}': {setter_name}()/{getter_name}() funktionieren nicht korrekt zusammen.")
                        return False
                        
                except Exception as e:
                    print(f"[VICTORY] Klasse '{class_name}': {setter_name}()/{getter_name}() Test fehlgeschlagen: {e}")
                    return False
        
        return True
    
    def _get_attr_value(self, obj, attr, class_name):
        """Holt Attributwert (öffentlich, privat oder via Getter)."""
        # Try direct access
        try:
            return getattr(obj, attr)
        except AttributeError:
            pass
        
        # Try getter
        getter_name = f'get_{attr}'
        if hasattr(obj, getter_name):
            try:
                return getattr(obj, getter_name)()
            except Exception:
                pass
        
        # Try name mangling
        mangled_name = f"_{class_name}__{attr}"
        if hasattr(obj, mangled_name):
            return getattr(obj, mangled_name)
        
        raise AttributeError(f"Attribut '{attr}' nicht gefunden")
    
    def _check_inheritance_new(self, class_name, test_obj, req):
        """Prüft Vererbungsbeziehungen mit isinstance() und MRO-Fallback."""
        inherits = req.get('inherits')
        if not inherits or inherits == 'None':
            return True
        
        parent_class_name = inherits
        
        try:
            import importlib
            import sys
            
            # Try to load parent class from klassen module
            module_name = parent_class_name.lower()
            parent_class = None
            
            # Try klassen.{module_name}
            if f'klassen.{module_name}' in sys.modules:
                mod = sys.modules[f'klassen.{module_name}']
                if hasattr(mod, parent_class_name):
                    parent_class = getattr(mod, parent_class_name)
            
            # Try direct import if not found
            if parent_class is None:
                try:
                    mod = importlib.import_module(f'klassen.{module_name}')
                    if hasattr(mod, parent_class_name):
                        parent_class = getattr(mod, parent_class_name)
                except Exception:
                    pass
            
            # Method 1: isinstance() check (works if same class object)
            if parent_class is not None:
                if isinstance(test_obj, parent_class):
                    return True
            
            # Method 2: Check MRO (Method Resolution Order) for class name
            # This works even if parent class was imported differently
            obj_class = test_obj.__class__
            mro = obj_class.__mro__  # All parent classes
            
            # Check if any parent class has the expected name
            for base_class in mro:
                if base_class.__name__ == parent_class_name:
                    return True
            
            # If we get here, inheritance not found
            print(f"[VICTORY] Klasse '{class_name}': Erbt nicht von '{parent_class_name}'.")
            return False
            
        except Exception as e:
            print(f"[VICTORY] Klasse '{class_name}': Vererbungsprüfung fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_rebuild_mode(self):
        """Prüft rebuild_mode Bedingungen."""
        if not self.template_objects:
            print("[VICTORY] Rebuild-Mode: Keine Template-Objekte definiert.")
            return False
        
        for tpl in self.template_objects:
            try:
                x, y = tpl.get('x'), tpl.get('y')
                expected_typ = tpl.get('typ')
                
                def get_obj_attr(obj, attr_name):
                    try:
                        return getattr(obj, attr_name)
                    except AttributeError:
                        getter_name = f'get_{attr_name}'
                        if hasattr(obj, getter_name):
                            getter = getattr(obj, getter_name)
                            if callable(getter):
                                return getter()
                    return None
                
                found = False
                for obj in self.objekte:
                    obj_x = get_obj_attr(obj, 'x')
                    obj_y = get_obj_attr(obj, 'y')
                    
                    if obj_x == x and obj_y == y:
                        obj_typ = getattr(obj, 'typ', None) or obj.__class__.__name__
                        if obj_typ == expected_typ:
                            found = True
                            
                            # Check optional attributes like richtung
                            if 'richtung' in tpl:
                                expected_richt = tpl.get('richtung')
                                actual_richt = get_obj_attr(obj, 'richtung')
                                if actual_richt != expected_richt:
                                    print(f"[VICTORY] Rebuild-Mode: Objekt bei ({x},{y}) hat falsche Richtung. Ist: {actual_richt}, Soll: {expected_richt}")
                                    return False
                            break
                
                if not found:
                    print(f"[VICTORY] Rebuild-Mode: Objekt '{expected_typ}' fehlt bei Position ({x},{y}).")
                    return False
            except Exception as e:
                print(f"[VICTORY] Rebuild-Mode: Fehler beim Prüfen von Template: {e}")
                return False
        
        return True
    
    def objekt_hinzufuegen(self, objekt):
        """
        Fügt ein von Schülern erzeugtes Objekt zum Spielfeld hinzu.
        Wird im rebuild_mode verwendet, um Objekte zu platzieren.
        
        Args:
            objekt: Das hinzuzufügende Objekt (muss x, y, typ Attribute haben)
        """
        try:
            # Überprüfe ob Objekt die notwendigen Attribute hat (direkt oder über Getter)
            def has_attribute_or_getter(obj, attr_name):
                if hasattr(obj, attr_name):
                    return True
                getter_name = f'get_{attr_name}'
                if hasattr(obj, getter_name) and callable(getattr(obj, getter_name)):
                    return True
                return False
            
            if not has_attribute_or_getter(objekt, 'x') or not has_attribute_or_getter(objekt, 'y'):
                print("[FEHLER] Objekt muss x und y Attribute (oder get_x/get_y Getter) haben")
                return False
            
            # Hole x, y Werte
            def get_attribute_value(obj, attr_name):
                try:
                    return getattr(obj, attr_name)
                except AttributeError:
                    getter_name = f'get_{attr_name}'
                    if hasattr(obj, getter_name):
                        return getattr(obj, getter_name)()
                return None
            
            # Im rebuild_mode mit class_requirements: Wenn es ein Held ist, wrappe in MetaHeld
            final_obj = objekt
            typ_str = str(getattr(objekt, 'typ', '')) or objekt.__class__.__name__
            
            if self.rebuild_mode and typ_str == 'Held':
                # Prüfe ob class_requirements für Held aktiv ist
                req = self.class_requirements.get("Held", {})
                student_mode_for_held = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
                
                if student_mode_for_held:
                    # Erstelle MetaHeld wrapper um Schüler-Objekt
                    try:
                        from .held import MetaHeld
                        x = get_attribute_value(objekt, 'x')
                        y = get_attribute_value(objekt, 'y')
                        richt = get_attribute_value(objekt, 'richtung') or 'down'
                        weiblich = get_attribute_value(objekt, 'weiblich') or False
                        
                        final_obj = MetaHeld(self.framework, objekt, x, y, richt, weiblich=weiblich)
                    except Exception as e:
                        print(f"[FEHLER] Held konnte nicht erstellt werden: {e}")
                        final_obj = objekt
            
            # Füge Objekt zur Liste hinzu
            self.objekte.append(final_obj)
            
            # Im rebuild_mode: Prüfe ob dieses Objekt ein Template ersetzt
            if self.rebuild_mode:
                x = get_attribute_value(objekt, 'x')
                y = get_attribute_value(objekt, 'y')
                typ = getattr(objekt, 'typ', None) or objekt.__class__.__name__
                
                # Suche passendes Template und markiere es als erfüllt
                for i, tpl in enumerate(self.template_objects):
                    if tpl.get('x') == x and tpl.get('y') == y:
                        # Template gefunden - markiere als erfüllt (wird nicht mehr gerendert)
                        tpl['_fulfilled'] = True
                        break
            
            # Setze Framework-Referenz falls möglich
            try:
                setattr(final_obj, 'framework', self.framework)
            except Exception:
                pass
            
            # Wenn es ein Held ist, setze self.held
            if typ_str == 'Held':
                self.held = final_obj
            
            return True
        except Exception as e:
            print(f"[FEHLER] Konnte Objekt nicht hinzufügen: {e}")
            return False
