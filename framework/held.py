# framework/held.py
import pygame
from .objekt import Objekt

class Held(Objekt):
    def __init__(self, framework_or_x, x_or_y=0, y_or_richtung=0, richtung_or_weiblich="down",
                 weiblich_or_sprite_positional=None, sprite_pfad="sprites/held.png", name="Namenloser Held",
                 steuerung_aktiv=True, weiblich=None):
        """
        Flexible constructor supporting two signatures:
        
        Student signature (Level 341+):
            Held(x, y, richtung, weiblich, ...)
            Example: Held(3, 4, "down", False)
        
        Framework signature (internal use):
            Held(framework, x, y, richtung, weiblich=False, ...)
            Example: Held(fw, 3, 4, "down", weiblich=False)
        
        Detection: If first arg is numeric, use student signature.
        """
        # Detect signature based on first parameter
        if isinstance(framework_or_x, (int, float)):
            # Student signature: Held(x, y, richtung, weiblich, ...)
            x = int(framework_or_x)
            y = int(x_or_y)
            richtung = y_or_richtung if isinstance(y_or_richtung, str) else "down"
            # weiblich can be 4th positional arg or keyword arg
            if isinstance(richtung_or_weiblich, bool):
                weiblich_val = richtung_or_weiblich
            elif weiblich_or_sprite_positional is not None and isinstance(weiblich_or_sprite_positional, bool):
                weiblich_val = weiblich_or_sprite_positional
            elif weiblich is not None:
                weiblich_val = bool(weiblich)
            else:
                weiblich_val = False
            framework = None
            # sprite_pfad might be passed via weiblich_or_sprite_positional if it's a string
            if isinstance(weiblich_or_sprite_positional, str):
                sprite_pfad = weiblich_or_sprite_positional
        else:
            # Framework signature: Held(framework, x, y, richtung, weiblich=False, ...)
            framework = framework_or_x
            x = int(x_or_y)
            y = int(y_or_richtung) if isinstance(y_or_richtung, (int, float)) else 0
            richtung = richtung_or_weiblich if isinstance(richtung_or_weiblich, str) else "down"
            # weiblich as keyword argument (framework usage)
            if weiblich is not None:
                weiblich_val = bool(weiblich)
            elif weiblich_or_sprite_positional is not None and isinstance(weiblich_or_sprite_positional, bool):
                weiblich_val = bool(weiblich_or_sprite_positional)
            else:
                weiblich_val = False
        
        # Apply weiblich sprite override
        if weiblich_val:
            sprite_pfad = "sprites/held2.png"
        
        super().__init__(typ="Held", x=x, y=y, richtung=richtung,
                         sprite_pfad=sprite_pfad, name=name)
        self.framework = framework
        self.ist_held = True
        self.geheimer_code = None
        self.weiblich = weiblich_val
        self.knappen = []
        # Initialize gold from settings if available (only if framework exists)
        try:
            if framework is not None:
                settings = getattr(framework.spielfeld, 'settings', {})
                held_settings = settings.get('Held', {})
                self.gold = held_settings.get('gold', 0)
            else:
                self.gold = 0
        except Exception:
            self.gold = 0
        # Initialize inventar immediately for tests that expect it
        try:
            from .inventar import Inventar
            self.inventar = Inventar()
        except Exception:
            self.inventar = None

        if steuerung_aktiv and framework is not None:
            self.aktiviere_steuerung()

    def setze_position(self,x,y):
        # Deaktiviere für die Schüler-Umgebung diese Methode
        # Für Entwickler: Ändern Sie False zu True, um diese Methode zu aktivieren
        if False:
            super().setze_position(x,y)
        else:
            print("[Held] Das darf ich nicht!")


    def aktiviere_steuerung(self):
        if self.framework is None:
            return  # No framework available (student-created Held)
        
        # Prüfe ob classes_present_mode aktiv ist
        sp = getattr(self.framework, 'spielfeld', None)
        classes_present = sp and getattr(sp, 'classes_present_mode', False)
        
        # Bewegung funktioniert immer über Framework
        self.framework.taste_registrieren(pygame.K_LEFT,  lambda: self.links(0))
        self.framework.taste_registrieren(pygame.K_RIGHT, lambda: self.rechts(0))
        self.framework.taste_registrieren(pygame.K_UP,    lambda: self.geh(0))
        self.framework.taste_registrieren(pygame.K_DOWN,  lambda: self.zurueck(0))
        
        if classes_present:
            # Im classes_present_mode: Rufe Schüler-Methoden auf, keine Framework-Logik
            # Schüler muss diese Methoden selbst implementieren
            # Bei MetaHeld: Greife direkt auf _student zu um Framework-Methoden zu umgehen
            
            def get_student_obj():
                """Hole das Schüler-Objekt (falls MetaHeld) oder self (falls direkt Schüler-Held)"""
                try:
                    return object.__getattribute__(self, '_student')
                except AttributeError:
                    return self
            
            def call_student_angriff():
                stud = get_student_obj()
                try:
                    stud.angriff()
                except AttributeError:
                    print("[Held] Methode angriff() nicht implementiert!")
                except Exception as e:
                    print(f"[Held] Fehler in angriff(): {e}")
            
            def call_student_nimm_herz():
                stud = get_student_obj()
                try:
                    stud.nimm_herz()
                except AttributeError:
                    print("[Held] Methode nimm_herz() nicht implementiert!")
                except Exception as e:
                    print(f"[Held] Fehler in nimm_herz(): {e}")
            
            def call_student_lese_spruch():
                stud = get_student_obj()
                # Versuche beide Varianten
                try:
                    stud.lese_spruch()
                except AttributeError:
                    try:
                        stud.spruch_lesen()
                    except AttributeError:
                        print("[Held] Methode lese_spruch() oder spruch_lesen() nicht implementiert!")
                    except Exception as e:
                        print(f"[Held] Fehler in spruch_lesen(): {e}")
                except Exception as e:
                    print(f"[Held] Fehler in lese_spruch(): {e}")
            
            def call_student_sage_spruch():
                stud = get_student_obj()
                # Versuche beide Varianten
                try:
                    stud.spruch_sagen()
                except AttributeError:
                    try:
                        stud.sage_spruch()
                    except AttributeError:
                        print("[Held] Methode spruch_sagen() oder sage_spruch() nicht implementiert!")
                    except Exception as e:
                        print(f"[Held] Fehler in sage_spruch(): {e}")
                except Exception as e:
                    print(f"[Held] Fehler in spruch_sagen(): {e}")
            
            def call_student_bediene_tor():
                stud = get_student_obj()
                try:
                    stud.bediene_tor()
                except AttributeError:
                    print("[Held] Methode bediene_tor() nicht implementiert!")
                except Exception as e:
                    print(f"[Held] Fehler in bediene_tor(): {e}")
            
            self.framework.taste_registrieren(pygame.K_SPACE, call_student_angriff)
            self.framework.taste_registrieren(pygame.K_RETURN, call_student_nimm_herz)
            self.framework.taste_registrieren(pygame.K_c, call_student_lese_spruch)
            self.framework.taste_registrieren(pygame.K_v, call_student_sage_spruch)
            self.framework.taste_registrieren(pygame.K_f, call_student_bediene_tor)
        else:
            # Normaler Modus: Framework-Logik
            self.framework.taste_registrieren(pygame.K_RETURN,lambda: self.nehme_auf(0))
            self.framework.taste_registrieren(pygame.K_SPACE, lambda: self.attack(0))
            self.framework.taste_registrieren(pygame.K_c, lambda: self.lese_code(0))
            self.framework.taste_registrieren(pygame.K_v, lambda: self.code_eingeben(delay_ms=0))
            self.framework.taste_registrieren(pygame.K_f, lambda: self.bediene_tor(0))
        
    def gib_knappe(self):
        if len(self.knappen)>0:
            return self.knappen[0]
        
    def add_knappe(self,k):
        self.knappen.append(k)
    
    def gold_gib(self):
        """Returns the held's current gold amount."""
        return int(getattr(self, 'gold', 0) or 0)
    
    def gold_setzen(self, amount):
        """Sets the held's gold amount."""
        self.gold = int(amount)
    
    def nehme_auf(self, delay_ms=500):
        """Pick up a single relevant object (heart, key, or code)."""
        if not self.framework or not hasattr(self.framework, 'spielfeld'):
            return False
        
        # Check if framework is blocked
        if getattr(self.framework, '_aktion_blockiert', False):
            return False
        
        sp = self.framework.spielfeld
        
        # Try to pick up heart
        try:
            herz = sp.finde_herz(self.x, self.y)
            if herz:
                sp.entferne_objekt(herz)
                self._herzen += 1
                # Reward gold if configured
                try:
                    from .config import HEART_GOLD
                    if hasattr(self, 'gold'):
                        try:
                            self.gold = int(getattr(self, 'gold', 0) or 0) + int(HEART_GOLD)
                        except Exception:
                            try:
                                self.gold = int(HEART_GOLD)
                            except Exception:
                                pass
                except Exception:
                    pass
                self._render_and_delay(delay_ms)
                return True
        except Exception:
            pass
        
        # Try to pick up code/zettel
        try:
            code = sp.finde_code(self.x, self.y)
            if code:
                if hasattr(code, 'gib_code'):
                    self.geheimer_code = code.gib_code()
                sp.entferne_objekt(code)
                self._render_and_delay(delay_ms)
                return True
        except Exception:
            pass
        
        # Try to pick up key
        try:
            # Ensure inventar exists
            if self.inventar is None:
                from .inventar import Inventar
                self.inventar = Inventar()
            
            # Find schluessel on this tile
            for obj in sp.objekte:
                if getattr(obj, 'x', None) == self.x and getattr(obj, 'y', None) == self.y:
                    if getattr(obj, 'typ', '').lower() == 'schluessel':
                        self.inventar.hinzufuegen(obj)
                        sp.entferne_objekt(obj)
                        self._render_and_delay(delay_ms)
                        return True
        except Exception:
            pass
        
        # Nichts zum Aufheben gefunden - ungültige Aktion
        if not getattr(self.framework, '_aus_tastatur', False):
            self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
        print("Hier liegt nichts.")
        self._render_and_delay(delay_ms)
        return False
    
    def nehm_auf_alle(self):
        """Pick up all objects on the current tile."""
        if not self.framework or not hasattr(self.framework, 'spielfeld'):
            return
        
        sp = self.framework.spielfeld
        
        # Ensure inventar exists
        if self.inventar is None:
            try:
                from .inventar import Inventar
                self.inventar = Inventar()
            except Exception:
                self.inventar = None
        
        # Find all objects on current tile
        objects_on_tile = [o for o in list(sp.objekte) 
                          if getattr(o, 'x', None) == self.x 
                          and getattr(o, 'y', None) == self.y 
                          and o is not self]
        
        for obj in objects_on_tile:
            try:
                # Heart
                if getattr(obj, 'typ', '').lower() == 'herz':
                    sp.entferne_objekt(obj)
                    continue
                
                # Code/Zettel
                if hasattr(obj, 'gib_code'):
                    self.geheimer_code = obj.gib_code()
                    sp.entferne_objekt(obj)
                    continue
                
                # Schluessel - add to inventar
                if getattr(obj, 'typ', '').lower() == 'schluessel' and self.inventar is not None:
                    self.inventar.hinzufuegen(obj)
                    sp.entferne_objekt(obj)
                    continue
                
                # Gegenstand - add to inventar
                if hasattr(obj, 'aufgenommen_von'):
                    obj.aufgenommen_von(self)
                    sp.objekte.remove(obj)
                    continue
            except Exception:
                pass
        
    def attack(self, delay_ms=500):
        if self.framework and getattr(self.framework, "_aktion_blockiert", False):
            return
        if self.tot or not self.framework:
            return

        import os, pygame
        from .utils import richtung_offset

        # aktuelle Blickrichtung merken
        alte_richtung = self.richtung
        basis = os.path.splitext(self.sprite_pfad)[0]

        # Animation: 3 Frames
        frames = [
            f"{basis}_att1.png",
            f"{basis}_att2.png",
            f"{basis}_att3.png",
        ]

        start = pygame.time.get_ticks()
        frame_delay = 100  # ms pro Frame
        for i, pfad in enumerate(frames):
            if os.path.exists(pfad):
                try:
                    self.bild = pygame.image.load(pfad).convert_alpha()
                    self._render_and_delay(frame_delay)
                except Exception as e:
                    print(f"[Held] Fehler beim Laden von {pfad}: {e}")

        # Nach Animation wieder ursprüngliches Richtungsbild laden
        self.richtung = alte_richtung
        self._update_sprite_richtung()

        # Angriff auf Monster prüfen (wie bisher)
        # Im classes_present_mode wird nur die Animation abgespielt, aber kein Monster getötet
        # Der Schüler muss die Kampflogik selbst implementieren
        sp = getattr(self.framework, 'spielfeld', None)
        classes_present = sp and getattr(sp, 'classes_present_mode', False)
        
        if not classes_present:
            dx, dy = richtung_offset(self.richtung)
            tx, ty = self.x + dx, self.y + dy
            monster = self.framework.spielfeld.finde_monster(tx, ty)
            if monster:
                # NICHT mehr entfernen:
                # self.framework.spielfeld.entferne_objekt(monster)

                monster.tot = True
                monster._update_sprite_richtung()
                try:
                    base_m = monster.sprite_pfad.split(".png")[0]
                    ko_m   = f"{base_m}_ko.png"
                    if os.path.exists(ko_m):
                        monster.bild = pygame.image.load(ko_m).convert_alpha()
                except Exception as e:
                    print("[Warnung] KO-Sprite Monster:", e)

                self._kills += 1


        # letzte Frame kurz sichtbar halten
        self._render_and_delay(delay_ms)
        
    def lese_code(self,delay_ms=500):
        self.lese_spruch(delay_ms)

        
    def lese_spruch(self,delay_ms=500):
        """Liest den Code vom Boden (falls dort ein Zettel liegt)."""
        if not self.framework:
            return None
        # Check if framework is blocked
        if getattr(self.framework, '_aktion_blockiert', False):
            return None
        code_obj = self.framework.spielfeld.finde_code(self.x, self.y)
        if code_obj:
            self.geheimer_code = code_obj.gib_code()
            print(f"[Held] Spruch {self.geheimer_code} notiert.")
            if self.framework:
                self.framework.spielfeld.entferne_objekt(code_obj)
            return self.geheimer_code
        # Kein Spruch gefunden - ungültige Aktion
        if not getattr(self.framework, '_aus_tastatur', False):
            self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
        print("[Held] Kein Spruch hier.")
        self._render_and_delay(delay_ms)
        return None
    
    def spruch_lesen(self,delay_ms=500):
        self.lese_spruch(delay_ms)
    
    def bediene_tor(self,delay_ms=500):
        """Versucht, das Tor vor dem Helden zu öffnen oder zu schließen."""
        # Check if framework is blocked
        if getattr(self.framework, '_aktion_blockiert', False):
            return
        tor = self.framework.spielfeld.finde_tor_vor(self)
        if tor:
            if tor.offen:
                tor.schliessen()
            else:
                tor.oeffnen()
        else:
            # Kein Tor gefunden - ungültige Aktion
            if not getattr(self.framework, '_aus_tastatur', False):
                self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
            print("[Held]: Kein Tor vor mir")
        self._render_and_delay(delay_ms)

    def spruch_sagen(self, code=None, delay_ms=500):
        self.code_eingeben(code,delay_ms)

    def sage_spruch(self,code=None,delay_ms=500):
        self.spruch_sagen(code,delay_ms)

    def code_eingeben(self, code=None,delay_ms=500):
        """Versucht, vor der Tür einen Code einzugeben."""
        if not self.framework:
            return
        if code is None and hasattr(self, "geheimer_code"):
            code = self.geheimer_code
        dx, dy = self.framework.spielfeld.level.texturen["w"].get_size()  # irrelevant
        dx, dy = 0, 0
        dx, dy = self.framework.spielfeld.level.texturen["w"].get_size()
        dx, dy = self.framework.spielfeld.level.texturen["w"].get_size()
        dx, dy = 0, 0
        # Korrekt:
        from .utils import richtung_offset
        dx, dy = richtung_offset(self.richtung)
        tx, ty = self.x + dx, self.y + dy
        tuer = self.framework.spielfeld.finde_tuer(tx, ty)
        if tuer:
            if tuer.code_eingeben(code):
                print("[Held] " + self.geheimer_code + "!")
            else:
                if self.geheimer_code == None:
                    print("[Held] Ich habe keinen Spruch...")
                    self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
                else:
                    self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
        else:
            print("[Held] Keine Tür vor mir.")
            self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
        self._render_and_delay(delay_ms)

    def attribute_als_text(self):
        if self.tot:
            return {
                "name": self.name, "x": self.x, "y": self.y,
                "ist_tot":"True"}
        if self.geheimer_code is None:
            return {
                "name": self.name, "x": self.x, "y": self.y,
                "richtung": self.transmute_richtung(self.richtung)
            }
        else:
            return {
                "name": self.name, "x": self.x, "y": self.y,
                "richtung": self.transmute_richtung(self.richtung), "Spruch":self.geheimer_code
            }
    """    
    def transmute_richtung(self,r):
        if r=="down":
            return "S"
        elif r=="up":
            return "N"
        elif r=="left":
            return "W"
        else:
            return "O"
    """


class MetaHeld(Held):
    """Wrapper that integrates student-provided Held instances with framework.
    
    Delegates method calls to the student object while maintaining framework
    responsibilities (controls, rendering, game state).
    """

    def __init__(self, framework, student_obj, x=0, y=0, richtung='down', weiblich=False):
        # Helper to get attribute value directly or via getter
        def get_attr_or_via_getter(obj, attr_name, default):
            """Get attribute value directly or via get_<attr> method"""
            try:
                return getattr(obj, attr_name)
            except AttributeError:
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
        
        # Use student's position values if they exist (directly or via getter), otherwise use level position
        student_x = get_attr_or_via_getter(student_obj, 'x', x)
        student_y = get_attr_or_via_getter(student_obj, 'y', y)
        student_richtung = get_attr_or_via_getter(student_obj, 'richtung', richtung)
        
        super().__init__(framework, student_x, student_y, student_richtung, steuerung_aktiv=False, weiblich=weiblich)
        object.__setattr__(self, '_student', student_obj)
        # Initialize allowed getters (will be set by spawning code if class_requirements exist)
        object.__setattr__(self, '_allowed_getters', None)
        
        # Monkey-patch student methods to trigger rendering after execution
        self._patch_student_methods()
        
        try:
            self.aktiviere_steuerung()
        except Exception:
            pass

    def _patch_student_methods(self):
        """Wrap student movement methods to trigger rendering after execution."""
        try:
            stud = object.__getattribute__(self, '_student')
            
            # List of methods to patch
            methods_to_patch = ['geh', 'links', 'rechts', 'zurueck']
            
            for method_name in methods_to_patch:
                if hasattr(stud, method_name):
                    original_method = getattr(stud, method_name)
                    if callable(original_method):
                        # Create wrapper function
                        def create_wrapper(orig_method, meta_self):
                            def wrapper(*args, **kwargs):
                                # Call original student method
                                result = orig_method(*args, **kwargs)
                                
                                # Sync position from student to meta
                                try:
                                    for a in ('x', 'y', 'richtung'):
                                        try:
                                            val = getattr(stud, a)
                                            object.__setattr__(meta_self, a, val)
                                        except AttributeError:
                                            getter_name = f'get_{a}'
                                            if hasattr(stud, getter_name):
                                                try:
                                                    getter = getattr(stud, getter_name)
                                                    if callable(getter):
                                                        val = getter()
                                                        object.__setattr__(meta_self, a, val)
                                                except Exception:
                                                    pass
                                except Exception:
                                    pass
                                
                                # Update sprite
                                try:
                                    if hasattr(meta_self, '_update_sprite_richtung'):
                                        meta_self._update_sprite_richtung()
                                except Exception:
                                    pass
                                
                                # Render immediately
                                try:
                                    meta_self._render_and_delay(0)
                                except Exception:
                                    pass
                                
                                return result
                            return wrapper
                        
                        # Replace method on MetaHeld (not on student) to override inherited method
                        setattr(self, method_name, create_wrapper(original_method, self))
        except Exception:
            pass

    def __getattribute__(self, name):
        """Intercept ALL attribute access to prioritize student object.
        
        Priority:
        1. Framework internal attributes (_student, framework methods, rendering, etc.)
        2. Student object attributes (public or via getter)
        3. MetaHeld/Held attributes as last resort (only for rendering internals)
        
        This ensures:
        - Student public attributes override framework defaults (e.g., student's name)
        - Student private attributes raise AttributeError (e.g., self.__x)
        - Framework can still access internal state for rendering
        """
        # Allow access to framework internals (rendering, sprite management, etc.)
        # This list includes all attributes needed for framework operation
        framework_internals = {
            '_student', '_patch_student_methods', 'aktiviere_steuerung',
            '_render_and_delay', '_update_sprite_richtung', 'framework',
            'typ', 'sprite', 'inventar', '__class__', '__dict__', '__init__',
            # Add rendering-related attributes that framework needs
            'image', 'rect', 'animationen', 'aktuelle_animation', 'animation_frame',
            '_show_error_sprite', '_dont_render', '_student_mode', '_level_expected_x',
            '_level_expected_y', '_level_expected_richtung', '_class_requirements',
            '_allowed_getters',  # Level-specific getter restrictions
            # Sprite-related attributes for directional rendering
            'sprite_pfad', 'bild', 'tot', '_herzen', '_kills', 'ist_held', 'geheimer_code',
            'weiblich', 'knappen', 'gold', '_privatmodus'
        }
        
        if name in framework_internals:
            return object.__getattribute__(self, name)
        
        # For all other attributes, try student first
        try:
            stud = object.__getattribute__(self, '_student')
        except AttributeError:
            # No student object yet (during __init__) - use framework
            return object.__getattribute__(self, name)
        
        # Try direct attribute access on student object
        try:
            return getattr(stud, name)
        except AttributeError:
            # Attribute is private or doesn't exist - try getter method
            getter_name = f'get_{name}'
            
            # Check if getter is allowed by level requirements
            allowed_getters = None
            try:
                allowed_getters = object.__getattribute__(self, '_allowed_getters')
            except AttributeError:
                # _allowed_getters not set - allow all getters
                pass
            
            if allowed_getters is not None and getter_name not in allowed_getters:
                # Getter exists but not allowed for this level
                raise AttributeError(f"'{type(stud).__name__}' object has no attribute '{name}'")
            
            if hasattr(stud, getter_name):
                try:
                    getter = getattr(stud, getter_name)
                    if callable(getter):
                        return getter()
                except Exception:
                    pass
            
            # No attribute and no getter - raise AttributeError
            raise AttributeError(f"'{type(stud).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """Set attributes on both wrapper and student object.
        If attribute is private, try to use setter method (set_<name>).
        """
        if name in ('x', 'y', 'richtung'):
            object.__setattr__(self, name, value)
            try:
                stud = object.__getattribute__(self, '_student')
                
                # Try direct attribute access first
                if hasattr(stud, name):
                    try:
                        setattr(stud, name, value)
                        return
                    except AttributeError:
                        pass
                
                # If direct access fails, try setter method
                setter_name = f'set_{name}'
                if hasattr(stud, setter_name):
                    try:
                        setter = getattr(stud, setter_name)
                        if callable(setter):
                            setter(value)
                            return
                    except Exception:
                        pass
            except Exception:
                pass
            return
        object.__setattr__(self, name, value)

    def aktiviere_steuerung(self):
        """Register controls that delegate to student methods when available."""
        try:
            stud = object.__getattribute__(self, '_student')
        except Exception:
            stud = None

        def call_student_movement(method_name, *args):
            """Movement methods only work if student implements them - no fallback."""
            def _inner():
                try:
                    if stud is not None and hasattr(stud, method_name) and callable(getattr(stud, method_name)):
                        fn = getattr(stud, method_name)
                        try:
                            fn(*args)
                        except TypeError:
                            try:
                                fn()
                            except Exception:
                                pass
                    else:
                        # No implementation - do nothing (student must implement method)
                        pass
                finally:
                    # Sync position/direction from student -> meta (try direct access, then getter)
                    try:
                        if stud is not None:
                            for a in ('x', 'y', 'richtung'):
                                # Try direct access first
                                try:
                                    val = getattr(stud, a)
                                    object.__setattr__(self, a, val)
                                except AttributeError:
                                    # Try getter method
                                    getter_name = f'get_{a}'
                                    if hasattr(stud, getter_name):
                                        try:
                                            getter = getattr(stud, getter_name)
                                            if callable(getter):
                                                val = getter()
                                                object.__setattr__(self, a, val)
                                        except Exception:
                                            pass
                    except Exception:
                        pass
                    # Update sprite to reflect new direction
                    try:
                        if hasattr(self, '_update_sprite_richtung'):
                            self._update_sprite_richtung()
                    except Exception:
                        pass
                    # Render immediately to make movement visible
                    try:
                        self._render_and_delay(0)
                    except Exception:
                        pass
            return _inner
        
        def call_student_pickup():
            """Enter: Try nimm_herz(), nimm_schluessel(), lese_spruch() in order."""
            def _inner():
                if stud is None:
                    return
                
                success = False
                
                # Try nimm_herz()
                if hasattr(stud, 'nimm_herz') and callable(getattr(stud, 'nimm_herz')):
                    try:
                        result = stud.nimm_herz()
                        if result is True:
                            success = True
                    except Exception:
                        pass
                
                # Try nimm_schluessel()
                if not success and hasattr(stud, 'nimm_schluessel') and callable(getattr(stud, 'nimm_schluessel')):
                    try:
                        result = stud.nimm_schluessel()
                        if result is True:
                            success = True
                    except Exception:
                        pass
                
                # Try lese_spruch()
                if not success and hasattr(stud, 'lese_spruch') and callable(getattr(stud, 'lese_spruch')):
                    try:
                        result = stud.lese_spruch()
                        if result is True:
                            success = True
                    except Exception:
                        pass
                
                # If nothing was picked up, print message
                if not success:
                    print("Hier liegt nichts")
            
            return _inner
        
        def call_student_use():
            """F: Try bediene_tor() and verwende_schluessel()."""
            def _inner():
                if stud is None:
                    return
                
                # Try bediene_tor()
                if hasattr(stud, 'bediene_tor') and callable(getattr(stud, 'bediene_tor')):
                    try:
                        result = stud.bediene_tor()
                        if result == 1:
                            return  # Success
                        elif result == 2:
                            print("Kein Tor vor mir")
                            return
                    except Exception:
                        pass
                
                # Try verwende_schluessel()
                if hasattr(stud, 'verwende_schluessel') and callable(getattr(stud, 'verwende_schluessel')):
                    try:
                        result = stud.verwende_schluessel()
                        if result == 1:
                            return  # Success
                        elif result == 2:
                            print("Keine Tür vor mir")
                        elif result == 3:
                            print("Falscher Spruch")
                        elif result == 4:
                            print("Nicht der richtige Schlüssel im Inventar")
                    except Exception:
                        pass
            
            return _inner

        try:
            # Movement keys - only work if student implements them
            self.framework.taste_registrieren(pygame.K_UP, call_student_movement('geh'))
            self.framework.taste_registrieren(pygame.K_LEFT, call_student_movement('links'))
            self.framework.taste_registrieren(pygame.K_RIGHT, call_student_movement('rechts'))
            self.framework.taste_registrieren(pygame.K_DOWN, call_student_movement('zurueck'))
            
            # Enter: Try pickup methods
            self.framework.taste_registrieren(pygame.K_RETURN, call_student_pickup())
            
            # F: Try use methods
            self.framework.taste_registrieren(pygame.K_f, call_student_use())
            
            # Space: Attack - ruft angriff() auf der Schülerklasse auf
            def call_student_angriff():
                if stud is None:
                    return
                try:
                    stud.angriff()
                except AttributeError:
                    print("[Held] Methode angriff() nicht implementiert!")
                except Exception as e:
                    print(f"[Held] Fehler in angriff(): {e}")
            
            self.framework.taste_registrieren(pygame.K_SPACE, call_student_angriff)
            
            # C: Try lese_spruch() or spruch_lesen()
            def call_student_lese_spruch():
                if stud is None:
                    return
                try:
                    stud.lese_spruch()
                except AttributeError:
                    try:
                        stud.spruch_lesen()
                    except AttributeError:
                        print("[Held] Methode lese_spruch() oder spruch_lesen() nicht implementiert!")
                    except Exception as e:
                        print(f"[Held] Fehler in spruch_lesen(): {e}")
                except Exception as e:
                    print(f"[Held] Fehler in lese_spruch(): {e}")
            
            self.framework.taste_registrieren(pygame.K_c, call_student_lese_spruch)
            
            # V: Try spruch_sagen() or sage_spruch()
            def call_student_sage_spruch():
                if stud is None:
                    return
                try:
                    stud.spruch_sagen()
                except AttributeError:
                    try:
                        stud.sage_spruch()
                    except AttributeError:
                        print("[Held] Methode spruch_sagen() oder sage_spruch() nicht implementiert!")
                    except Exception as e:
                        print(f"[Held] Fehler in sage_spruch(): {e}")
                except Exception as e:
                    print(f"[Held] Fehler in spruch_sagen(): {e}")
            
            self.framework.taste_registrieren(pygame.K_v, call_student_sage_spruch)
        except Exception:
            try:
                super().aktiviere_steuerung()
            except Exception:
                pass

    def attribute_als_text(self):
        """Show all attributes from the student object in the inspector.
        If attribute is private, try to use getter method (get_<name>).
        """
        try:
            stud = object.__getattribute__(self, '_student')
            result = {}
            
            # Always show critical attributes for debugging
            for attr in ['x', 'y', 'richtung', 'weiblich', 'name', 'level', 'typ']:
                value_found = False
                
                # Try direct attribute access first (works for public attributes)
                try:
                    val = getattr(stud, attr)
                    # Convert Level object reference to string
                    if attr == 'level' and val is not None:
                        result[attr] = '<Level>'
                    else:
                        result[attr] = str(val)
                    value_found = True
                except AttributeError:
                    # Attribute is private or doesn't exist, try getter
                    pass
                
                # If direct access failed, try getter method
                if not value_found:
                    getter_name = f'get_{attr}'
                    try:
                        getter = getattr(stud, getter_name)
                        if callable(getter):
                            val = getter()
                            # Convert Level object reference to string
                            if attr == 'level' and val is not None:
                                result[attr] = '<Level>'
                            else:
                                result[attr] = str(val)
                            value_found = True
                    except AttributeError:
                        # Getter doesn't exist
                        pass
                    except Exception as e:
                        # Getter exists but raised an error
                        result[attr] = f'<error: {e}>'
                        value_found = True
                
                # If neither worked, show error message (but not for optional attributes)
                if not value_found and attr not in ['level', 'name']:
                    result[attr] = f'Attribut {attr} privat und kein getter vorhanden'
            
            return result
        except Exception:
            return super().attribute_als_text()
