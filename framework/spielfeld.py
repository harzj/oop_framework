# framework/spielfeld.py
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
        if auto_erzeuge_objekte:
            self._spawn_aus_level()
            
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
                
                # Check if student mode is enabled for Hindernis
                if hindernis_requirements:
                    student_mode_enabled = bool(hindernis_requirements.get('load_from_schueler') or hindernis_requirements.get('load_from_klassen'))
                    if student_mode_enabled:
                        self._hindernis_class_valid = False  # Will be set to True if validation passes
                
                # Try to get student Hindernis class and validate it ONCE
                if student_mode_enabled:
                    try:
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
                                
                                # Check private attributes - separate check for x, y vs typ
                                private_attrs = hindernis_requirements.get('attributes_private', {})
                                for attr_name, required in private_attrs.items():
                                    if required:
                                        has_private = hasattr(test_inst, f"_{test_inst.__class__.__name__}__{attr_name}")
                                        has_public = hasattr(test_inst, attr_name) and not attr_name.startswith('_')
                                        
                                        if not has_private or has_public:
                                            print(f"Hindernis: Attribut '{attr_name}' muss privat sein")
                                            validation_ok = False
                                            break
                                        
                                        # Check getter
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
                    zettel_student_mode_enabled = bool(zettel_requirements.get('load_from_schueler') or zettel_requirements.get('load_from_klassen'))
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
                                
                                # Check private attributes
                                private_attrs = zettel_requirements.get('attributes_private', {})
                                for attr_name, required in private_attrs.items():
                                    if required:
                                        has_private = hasattr(test_inst, f"_{test_inst.__class__.__name__}__{attr_name}")
                                        has_public = hasattr(test_inst, attr_name) and not attr_name.startswith('_')
                                        
                                        if not has_private or has_public:
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
                    
                    # Add Level reference later via setze_level()
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
                cls = self._get_entity_class("Knappe", Knappe)
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
                        # Try: student wants Level as first arg
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
                    else:
                        # Final fallback: use framework Knappe with generated name
                        self.knappe = Knappe(self.framework, x, y, richt, name=self.generate_knappe_name())
                except Exception:
                    # If anything unexpected fails, ensure we still spawn a framework Knappe
                    try:
                        self.knappe = Knappe(self.framework, x, y, richt, name=self.generate_knappe_name())
                    except Exception:
                        self.knappe = None
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
                    # For other classes: if methods or attributes configured, assume student class
                    has_methods = bool(req.get('methods', []))
                    has_attrs = bool(req.get('attributes', []))
                    load_student_from_requirements = has_methods or has_attrs
                    # Other classes always load from klassen/<name>.py when configured
                    if load_student_from_requirements:
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
                                        # skip wildcard imports and any imports from our framework package
                                        modname = getattr(node, 'module', '') or ''
                                        if modname.startswith('framework'):
                                            continue
                                        # skip `from ... import *` which may pollute namespace
                                        if any(alias.name == '*' for alias in node.names):
                                            continue
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
                                # execute only the trimmed AST
                                code_obj = compile(new_mod, path, 'exec')
                                exec(code_obj, module.__dict__)
                                return module
                            except Exception:
                                return None

                        # If cand refers to a dotted package (like klassen.x), try normal import first
                        if '.' in cand:
                            try:
                                mod = importlib.import_module(cand)
                                self._student_module_cache[cand] = mod
                                if required_class_name is None or getattr(mod, required_class_name, None) is not None:
                                    return mod
                                # module loaded but doesn't define the required class -> try next candidate
                                continue
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

            repo_root = os.path.dirname(os.path.dirname(__file__))

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
                                                    # Double underscore name mangling
                                                    attr_name = attr_name[len('_' + class_node.name + '__'):]
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
                        
                        # Second pass: find getter methods
                        for item in class_node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith('get_'):
                                    attr_name = item.name[4:]  # Remove 'get_' prefix
                                    getters.add(attr_name)
                        
                        # An attribute is considered present if it's set in __init__ OR has a getter
                        available = found | getters
                        return set(required).issubset(available)
                    
                    # helper: check whether the class has required methods
                    def _class_has_required_methods(class_node, required_methods):
                        found_methods = set()
                        for item in class_node.body:
                            if isinstance(item, ast.FunctionDef):
                                found_methods.add(item.name)
                        return set(required_methods).issubset(found_methods)

                    for node in tree.body:
                        if isinstance(node, ast.ClassDef) and node.name == cls_name:
                            # For Held classes, use class_requirements if available
                            if cls_name == 'Held':
                                # Get required attributes and methods from class_requirements
                                req = self.class_requirements.get("Held", {})
                                required_attrs = req.get('attributes', [])
                                required_methods = req.get('methods', [])
                                
                                # If no class_requirements, use legacy minimal set for attributes
                                if not required_attrs:
                                    required_attrs = ['x', 'y', 'richtung', 'weiblich', 'typ']
                                
                                try:
                                    # Check attributes
                                    if required_attrs and not _class_has_required_attrs(node, required_attrs):
                                        return False
                                    
                                    # Check methods
                                    if required_methods and not _class_has_required_methods(node, required_methods):
                                        return False
                                    
                                    return True
                                except Exception:
                                    return False
                            # For Zettel classes, use class_requirements if available
                            elif cls_name == 'Zettel':
                                # Get required attributes and methods from class_requirements
                                req = self.class_requirements.get("Zettel", {})
                                required_attrs = req.get('attributes', [])
                                required_methods = req.get('methods', [])
                                
                                try:
                                    # Check attributes
                                    if required_attrs and not _class_has_required_attrs(node, required_attrs):
                                        return False
                                    
                                    # Check methods
                                    if required_methods and not _class_has_required_methods(node, required_methods):
                                        return False
                                    
                                    return True
                                except Exception:
                                    return False
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
            mapping = { 'p': 'Held', 'h': 'Herz', 'x': 'Monster', 'c': 'Code', 'd': 'Tuer', 's': 'Schluessel', 'v': 'Villager', 'k': 'Knappe', 'g': 'Tor', 'q': 'Questgeber', 't': 'Hindernis', 'm': 'Hindernis', 'b': 'Hindernis' }
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
            hindernis_requirements = self.class_requirements.get('Hindernis', {})
            student_mode_enabled = False
            
            if hindernis_requirements:
                student_mode_enabled = bool(hindernis_requirements.get('load_from_schueler') or hindernis_requirements.get('load_from_klassen'))
            
            if student_mode_enabled:
                # Check if class exists
                if not self._student_has_class('Hindernis'):
                    hide_obstacles = True
                # Check if validation passed (get_x, get_y present)
                elif not getattr(self, '_hindernis_class_valid', False):
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
                
                # Check getter exists
                getter_name = f'get_{attr_name}'
                if not (hasattr(student_obj, getter_name) and callable(getattr(student_obj, getter_name))):
                    return False
                
                # Check setter exists (optional for some attributes like typ and weiblich)
                setter_name = f'set_{attr_name}'
                if attr_name not in ['typ', 'weiblich']:
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

    def check_victory(self) -> bool:
        """Evaluate configured victory conditions.

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
                    hx = int(getattr(held, 'x', None))
                    hy = int(getattr(held, 'y', None))
                    if hx != tx or hy != ty:
                        return False
                    # also ensure framework not blocking student actions
                    if getattr(self.framework, '_aktion_blockiert', False):
                        return False
                except Exception:
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
                    # BUT only if the class requires student implementation
                    for cn in needed:
                        # Check if this class requires student implementation
                        req = self.class_requirements.get(cn, {})
                        requires_student = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
                        
                        if requires_student:
                            has_class = self._student_has_class(cn)
                            if not has_class:
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
                            mv_enabled = mv and isinstance(mv, dict) and mv.get('enabled')
                            if not mv_enabled:
                                expected_x = getattr(held, '_level_expected_x', None)
                                expected_y = getattr(held, '_level_expected_y', None)
                                expected_richtung = getattr(held, '_level_expected_richtung', None)
                                
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
                        
                        # Check if it's student mode for this class
                        student_mode = bool(req.get('load_from_schueler') or req.get('load_from_klassen'))
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
                            # Already validated during spawn
                            continue
                        elif class_name == 'Zettel':
                            # Check validation result from spawn
                            if not getattr(self, '_zettel_class_valid', True):
                                return False
                            continue
                        else:
                            # Check privacy for at least one object of this class
                            if objects_to_check:
                                # Check privacy requirements for the first object
                                if not self._check_privacy_requirements(class_name, objects_to_check[0]):
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
