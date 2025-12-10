# framework/framework.py
import pygame
import tkinter as tk
from tkinter import filedialog
from .spielfeld import Spielfeld

class Framework:
    def __init__(self, levelnummer=1, feldgroesse=64, auto_erzeuge_objekte=True, w = False, splash=False):
        print("(c) 2025 Johannes Harz\nFachkonferenz Informatik\nCusanus Gymnasium St. Wendel")
        pygame.init()
        self.feldgroesse = feldgroesse
        self._tasten = {}
        self._running = True
        self._sieg = False
        self._hinweis = None        # zeigt Text bei ungültiger Aktion
        self._aktion_blockiert = False  # verhindert Queue-Updates aus Schülercode
        self._aus_tastatur = False
        self.weiblich = w
        self.info_scroll = 0  # Scroll-Offset für Infotext
        # transient projectiles (arrows) created by ranged attackers
        self._projectiles = []




                # Dummy-Fenster (für convert_alpha) + später richtige Größe
        # --- Fensterposition dynamisch setzen (rechte Hälfte, oberes Drittel) ---
        import os
        import tkinter as tk

        # Bildschirmgröße über Tkinter ermitteln
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()

        # Fenstergröße (Dummy für Splash + Initialisierung)
        win_w, win_h = 800, 600

        # Position: rechte Hälfte, oberes Drittel
        x = screen_w - win_w - 50              # 50 px Abstand vom rechten Rand
        y = int(screen_h / 3 - win_h / 3)      # oberes Drittel zentriert
        if y < 0:
            y = 0

        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

        # Erstes Dummy-Fenster für Splash etc.
        self.screen = pygame.display.set_mode((win_w, win_h))

        
        # --- Splash-Screen (1 Sekunde, mit Aspect-Ratio) ---
        if splash:
            try:
                splash = pygame.image.load("sprites/splash.png").convert_alpha()
                img_w, img_h = splash.get_size()
                win_w, win_h = self.screen.get_size()

                # Maßstab berechnen (maximale Breite oder Höhe ausnutzen)
                scale = min(win_w / img_w, win_h / img_h)
                new_size = (int(img_w * scale), int(img_h * scale))
                splash_scaled = pygame.transform.smoothscale(splash, new_size)

                # Zentriert zeichnen
                x = (win_w - new_size[0]) // 2
                y = (win_h - new_size[1]) // 2
                self.screen.fill((0, 0, 0))
                self.screen.blit(splash_scaled, (x, y))
                pygame.display.flip()
                pygame.time.wait(1000)
            except Exception as e:
                print("[Splash] konnte nicht angezeigt werden:", e)
            # --- Ende Splash-Screen ---


        
        self.levelfile = f"level/level{levelnummer}.json"
        self.spielfeld = Spielfeld(self.levelfile, self, feldgroesse, auto_erzeuge_objekte)
        breite = self.spielfeld.level.breite * feldgroesse + 280
        hoehe  = self.spielfeld.level.hoehe  * feldgroesse
        self.screen = pygame.display.set_mode((breite, hoehe))
        pygame.display.set_caption("OOP-Framework")

        self.font = pygame.font.SysFont("consolas", 18)
        self.big  = pygame.font.SysFont("consolas", 32, bold=True)

        # Standard-Tasten
        self.taste_registrieren(pygame.K_ESCAPE, self.beenden)
        self.taste_registrieren(pygame.K_o, self.level_oeffnen)

        # sofort einmal zeichnen
        self._render_frame()
        pygame.time.wait(500)

    # --- Tastatur ---
    def taste_registrieren(self, key, fn): self._tasten[key] = fn
    
    def objekt_hinzufuegen(self, obj):
        """Fügt ein Objekt dem Spielfeld hinzu und verknüpft es mit dem Framework."""
        # Decide whether the caller is student code (schueler / klassen / other)
        try:
            import sys as _sys
            frm = _sys._getframe(1)
            caller_mod = frm.f_globals.get('__name__', '')
        except Exception:
            caller_mod = ''

        is_student_caller = False
        try:
            if isinstance(caller_mod, str):
                if caller_mod == 'schueler' or caller_mod.startswith('klassen.'):
                    is_student_caller = True
                # treat any non-framework caller as student code for this API
                elif not (caller_mod == 'framework' or caller_mod.startswith('framework.')):
                    is_student_caller = True
        except Exception:
            is_student_caller = False

        # If the call originates from student code, accept the passed object as-is
        # (this allows students to instantiate framework classes themselves and
        # add them). Otherwise, default behaviour applies.
        try:
            obj.framework = self
        except Exception:
            pass

        # Use spielfeld.objekt_hinzufuegen for proper handling (especially in rebuild mode)
        try:
            if hasattr(self.spielfeld, 'objekt_hinzufuegen'):
                self.spielfeld.objekt_hinzufuegen(obj)
            else:
                # Fallback: direct append
                self.spielfeld.objekte.append(obj)
        except Exception:
            # fallback: try to ensure list exists
            try:
                if not hasattr(self.spielfeld, 'objekte'):
                    self.spielfeld.objekte = []
                self.spielfeld.objekte.append(obj)
            except Exception:
                pass

        # If a Held was added, ensure controls are active
        try:
            if getattr(obj, 'typ', None) == 'Held' or obj.__class__.__name__ == 'Held':
                try:
                    # If the object exposes an aktiviere_steuerung method, call it
                    if hasattr(obj, 'aktiviere_steuerung') and callable(getattr(obj, 'aktiviere_steuerung')):
                        try:
                            obj.aktiviere_steuerung()
                        except Exception:
                            pass
                except Exception:
                    pass

        except Exception:
            pass

        try:
            self._render_frame()
        except Exception:
            pass
        
    def gib_objekt_an(self, x, y):
        """Gibt das Objekt an Position (x, y) zurück oder None."""
        return self.spielfeld.objekt_an(x, y)



    # --- Render-Hilfen ---
    def _zeichne_info(self):
        y = 8 - self.info_scroll  # Scroll-Offset berücksichtigen

        panel_x = self.spielfeld.level.breite * self.feldgroesse + 8
        #y = 8
        # Ensure the Held is always shown first with basic attributes
        try:
            sp = getattr(self, 'spielfeld', None)
        except Exception:
            sp = None

        if sp:
            held = getattr(sp, 'held', None)
            if held:
                try:
                    # If this is a MetaHeld wrapping a student object, only show
                    # attributes that the student actually provided (hasattr).
                    stud = getattr(held, '_student', None)
                except Exception:
                    stud = None

                if stud is not None:
                    try:
                        # name only if student provided it
                        if hasattr(stud, 'name'):
                            name = getattr(stud, 'name')
                            hdr = self.font.render(f"Name={name}", True, (255,255,255))
                            self.screen.blit(hdr, (panel_x, y)); y += 20
                    except Exception:
                        pass
                    try:
                        # show only attributes present on the student object (directly or via getter)
                        dm = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                        
                        # Helper to get value directly or via getter
                        def get_student_attr(obj, attr_name):
                            """Try direct access first, then getter method"""
                            try:
                                return getattr(obj, attr_name)
                            except AttributeError:
                                getter_name = f'get_{attr_name}'
                                if hasattr(obj, getter_name):
                                    try:
                                        getter = getattr(obj, getter_name)
                                        if callable(getter):
                                            return getter()
                                    except Exception:
                                        pass
                                raise
                        
                        # Try to get and display x
                        try:
                            x_val = get_student_attr(stud, 'x')
                            x_txt = self.font.render(f"x={x_val}", True, (200,200,200))
                            self.screen.blit(x_txt, (panel_x, y)); y += 20
                        except AttributeError:
                            pass
                        
                        # Try to get and display y
                        try:
                            y_val = get_student_attr(stud, 'y')
                            y_txt = self.font.render(f"y={y_val}", True, (200,200,200))
                            self.screen.blit(y_txt, (panel_x, y)); y += 20
                        except AttributeError:
                            pass
                        
                        # Try to get and display richtung
                        try:
                            r = get_student_attr(stud, 'richtung')
                            rdisp = dm.get(str(r), str(r))
                            r_txt = self.font.render(f"richtung={rdisp}", True, (200,200,200))
                            self.screen.blit(r_txt, (panel_x, y)); y += 20
                        except AttributeError:
                            pass
                    except Exception:
                        pass
                    # After showing richtung, draw Held-Inventar (if any) below it
                    try:
                        inv = getattr(stud, 'inventar', None) or getattr(held, 'inventar', None)
                        if inv:
                            item_x = panel_x
                            item_y = y
                            icon_size = 16
                            spacing = icon_size + 4
                            lbl = self.font.render("Inventar:", True, (220,220,160))
                            self.screen.blit(lbl, (item_x, item_y))
                            item_y += 18
                            ix = 0
                            for it in list(inv):
                                try:
                                    color = getattr(it, 'farbe', None) or getattr(it, 'color', None) or getattr(it, 'key_color', None)
                                    surf = None
                                    try:
                                        if hasattr(it, 'bild') and getattr(it, 'bild', None) is not None:
                                            surf = it.bild
                                        else:
                                            import os, pygame as _pg
                                            cand = None
                                            if color:
                                                bases = [
                                                    os.getcwd(),
                                                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                                                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),
                                                ]
                                                for b in bases:
                                                    p = os.path.join(b, 'sprites', f'key_{color}.png')
                                                    if os.path.exists(p):
                                                        cand = p
                                                        break
                                            if cand:
                                                try:
                                                    surf = _pg.image.load(cand).convert_alpha()
                                                except Exception:
                                                    surf = None
                                    except Exception:
                                        surf = None

                                    if surf:
                                        try:
                                            surf_small = pygame.transform.smoothscale(surf, (icon_size, icon_size))
                                            self.screen.blit(surf_small, (item_x + ix * spacing, item_y))
                                        except Exception:
                                            pygame.draw.rect(self.screen, (200,200,0), (item_x + ix * spacing, item_y, icon_size, icon_size))
                                    else:
                                        if color:
                                            pygame.draw.rect(self.screen, (200,200,0), (item_x + ix * spacing, item_y, icon_size, icon_size))
                                        else:
                                            nm = getattr(it, 'name', str(it))[:10]
                                            s = self.font.render(nm, True, (200,200,200))
                                            self.screen.blit(s, (item_x + ix * spacing, item_y))

                                    ix += 1
                                    if ix >= 5:
                                        ix = 0
                                        item_y += icon_size + 6
                                except Exception:
                                    continue
                            y = item_y + icon_size + 6
                    except Exception:
                        pass
                    y += 4
                # separator after Held (visual separation)
                try:
                    pygame.draw.line(self.screen, (120,120,120), (panel_x, y+6), (self.screen.get_width()-8, y+6), 1)
                    y += 10
                except Exception:
                    pass

                # Only draw the default-held block when there is no student object
                # (when we showed student-provided attributes above we must not
                # repeat the generic Held display -- this previously caused the
                # hero to appear twice in the inspector).
                if stud is None:
                    try:
                        # use requested default name if not set
                        name = getattr(held, 'name', None) or 'namenloser held'
                        hdr = self.font.render(f"Name={name}", True, (255,255,255))
                        self.screen.blit(hdr, (panel_x, y)); y += 20
                    except Exception:
                        pass
                    try:
                        # one value per line (like Monster inspector)
                        x = getattr(held, 'x', 0)
                        yv = getattr(held, 'y', 0)
                        richt = getattr(held, 'richtung', '?')
                        # map directions for display only
                        dm = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                        rdisp = dm.get(str(richt), str(richt))
                        x_txt = self.font.render(f"x={x}", True, (200,200,200))
                        self.screen.blit(x_txt, (panel_x, y)); y += 20
                        y_txt = self.font.render(f"y={yv}", True, (200,200,200))
                        self.screen.blit(y_txt, (panel_x, y)); y += 20
                        r_txt = self.font.render(f"richtung={rdisp}", True, (200,200,200))
                        self.screen.blit(r_txt, (panel_x, y)); y += 20
                    except Exception:
                        pass
                    # After showing richtung, draw Held-Inventar (if any) below it
                    try:
                        inv = getattr(held, 'rucksack', None) or getattr(held, 'inventar', None)
                        if inv:
                            item_x = panel_x
                            item_y = y
                            icon_size = 16
                            spacing = icon_size + 4
                            lbl = self.font.render("Inventar:", True, (220,220,160))
                            self.screen.blit(lbl, (item_x, item_y))
                            item_y += 18
                            ix = 0
                            # Support both old Inventar format (iterable) and new format (items list)
                            items_to_render = list(inv) if hasattr(inv, '__iter__') and not hasattr(inv, 'items') else getattr(inv, 'items', [])
                            for it in items_to_render:
                                try:
                                    color = getattr(it, 'farbe', None) or getattr(it, 'color', None) or getattr(it, 'key_color', None)
                                    art = getattr(it, 'art', None)
                                    surf = None
                                    try:
                                        if hasattr(it, 'bild') and getattr(it, 'bild', None) is not None:
                                            surf = it.bild
                                        else:
                                            import os, pygame as _pg
                                            cand = None
                                            
                                            # Try art-based sprite mapping first (for Gegenstand items)
                                            if art:
                                                sprite_map = {
                                                    'Schwert': 'sprites/schwert.png',
                                                    'Schluessel': 'sprites/key_green.png',
                                                }
                                                sprite_path = sprite_map.get(art)
                                                if sprite_path:
                                                    bases = [
                                                        os.getcwd(),
                                                        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                                                    ]
                                                    for b in bases:
                                                        p = os.path.join(b, sprite_path)
                                                        if os.path.exists(p):
                                                            cand = p
                                                            break
                                            
                                            # Fall back to color-based key sprites
                                            if not cand and color:
                                                bases = [
                                                    os.getcwd(),
                                                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                                                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),
                                                ]
                                                for b in bases:
                                                    p = os.path.join(b, 'sprites', f'key_{color}.png')
                                                    if os.path.exists(p):
                                                        cand = p
                                                        break
                                            
                                            if cand:
                                                try:
                                                    surf = _pg.image.load(cand).convert_alpha()
                                                except Exception:
                                                    surf = None
                                    except Exception:
                                        surf = None

                                    if surf:
                                        try:
                                            surf_small = pygame.transform.smoothscale(surf, (icon_size, icon_size))
                                            self.screen.blit(surf_small, (item_x + ix * spacing, item_y))
                                        except Exception:
                                            pygame.draw.rect(self.screen, (200,200,0), (item_x + ix * spacing, item_y, icon_size, icon_size))
                                    else:
                                        if color:
                                            pygame.draw.rect(self.screen, (200,200,0), (item_x + ix * spacing, item_y, icon_size, icon_size))
                                        else:
                                            nm = art if art else getattr(it, 'name', str(it))[:10]
                                            s = self.font.render(nm[:3], True, (200,200,200))
                                            self.screen.blit(s, (item_x + ix * spacing, item_y))

                                    ix += 1
                                    if ix >= 5:
                                        ix = 0
                                        item_y += icon_size + 6
                                except Exception:
                                    continue
                            y = item_y + icon_size + 6
                    except Exception:
                        pass
                    y += 4

        # Show Knappe next, then Monsters, then remaining objects. Use separators
        # between these groups and avoid large vertical gaps (separators replace heavy spacing).
        try:
            # small helper to draw a horizontal separator
            def draw_sep(ypos):
                try:
                    pygame.draw.line(self.screen, (100,100,100), (panel_x, ypos+6), (self.screen.get_width()-8, ypos+6), 1)
                except Exception:
                    pass

            # Draw Knappe (if present) as a distinct block after Held
            kn = getattr(sp, 'knappe', None)
            if kn is not None:
                try:
                    # header
                    name = getattr(kn, 'name', None) or 'namenloser knappe'
                    hdr = self.font.render(f"Name={name}", True, (255,255,255))
                    self.screen.blit(hdr, (panel_x, y)); y += 20
                except Exception:
                    pass
                try:
                    x = getattr(kn, 'x', 0)
                    yv = getattr(kn, 'y', 0)
                    richt = getattr(kn, 'richtung', '?')
                    dm = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                    rdisp = dm.get(str(richt), str(richt))
                    x_txt = self.font.render(f"x={x}", True, (200,200,200))
                    self.screen.blit(x_txt, (panel_x, y)); y += 20
                    y_txt = self.font.render(f"y={yv}", True, (200,200,200))
                    self.screen.blit(y_txt, (panel_x, y)); y += 20
                    r_txt = self.font.render(f"richtung={rdisp}", True, (200,200,200))
                    self.screen.blit(r_txt, (panel_x, y)); y += 20
                except Exception:
                    pass
                
                # Render Knappe's inventory if present (rucksack attribute)
                try:
                    inv = getattr(kn, 'rucksack', None) or getattr(kn, 'inventar', None)
                    if inv and hasattr(inv, 'items'):
                        item_x = panel_x
                        item_y = y
                        icon_size = 16
                        spacing = icon_size + 4
                        lbl = self.font.render("Inventar:", True, (220,220,160))
                        self.screen.blit(lbl, (item_x, item_y))
                        item_y += 18
                        ix = 0
                        items_list = getattr(inv, 'items', [])
                        for it in items_list:
                            try:
                                # Try to load sprite for item based on art attribute
                                art = getattr(it, 'art', None)
                                surf = None
                                if art:
                                    import os
                                    sprite_map = {
                                        'Schwert': 'sprites/schwert.png',
                                        'Schluessel': 'sprites/key_green.png',
                                    }
                                    sprite_path = sprite_map.get(art)
                                    if sprite_path:
                                        bases = [
                                            os.getcwd(),
                                            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                                        ]
                                        for b in bases:
                                            p = os.path.join(b, sprite_path)
                                            if os.path.exists(p):
                                                try:
                                                    surf = pygame.image.load(p).convert_alpha()
                                                    break
                                                except Exception:
                                                    pass
                                
                                if surf:
                                    try:
                                        surf_small = pygame.transform.smoothscale(surf, (icon_size, icon_size))
                                        self.screen.blit(surf_small, (item_x + ix * spacing, item_y))
                                    except Exception:
                                        pygame.draw.rect(self.screen, (200,200,0), (item_x + ix * spacing, item_y, icon_size, icon_size))
                                else:
                                    # Fallback: draw colored rectangle or text
                                    nm = art if art else str(it)[:10]
                                    s = self.font.render(nm[:3], True, (200,200,200))
                                    self.screen.blit(s, (item_x + ix * spacing, item_y))
                                
                                ix += 1
                                if ix >= 5:
                                    ix = 0
                                    item_y += icon_size + 6
                            except Exception:
                                continue
                        if items_list:
                            y = item_y + icon_size + 6
                except Exception:
                    pass
                
                # separator after knappe
                draw_sep(y); y += 10

            # Monsters: render each with a separator between
            monsters = [o for o in self.spielfeld.objekte if getattr(o, 'typ', None) == 'Monster']
            for m in monsters:
                try:
                    name = getattr(m, 'name', None) or 'Monster'
                    hdr = self.font.render(f"{name} (Monster)", True, (255,255,255))
                    self.screen.blit(hdr, (panel_x, y)); y += 20
                except Exception:
                    pass
                try:
                    items = m.attribute_als_text()
                    for k, v in items.items():
                        try:
                            val = v
                            if isinstance(k, str) and 'richt' in k.lower():
                                dm = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                                val = dm.get(str(v), str(v))
                            txt = f"{k}: {val}"
                            while self.font.size(txt)[0] > (self.screen.get_width() - panel_x - 20):
                                txt = txt[:-1]
                            txt = self.font.render(f"{k}: {val}", True, (240,240,240))
                            self.screen.blit(txt, (panel_x, y)); y += 20
                        except Exception:
                            continue
                except Exception as ex_attr:
                    try:
                        msg = f"Fehler in der Schülerklasse Monster: {ex_attr}"
                        err = self.font.render(msg, True, (255,100,100))
                        self.screen.blit(err, (panel_x, y)); y += 20
                    except Exception:
                        pass
                # separator between monsters
                draw_sep(y); y += 8

            # Finally render remaining objects (excluding Held, Knappe, Monsters, and items)
            # Items to exclude: Zettel, Herz, Tuer, Tor, Schluessel, Hindernis, etc.
            excluded_types = ['Monster', 'Zettel', 'Herz', 'Tuer', 'Tor', 'Schluessel', 'Baum', 'Berg', 'Busch', 'Hindernis', 'Spruch', '?']
            remaining = [o for o in self.spielfeld.objekte 
                        if o not in ([held] if held else []) 
                        and o is not kn 
                        and getattr(o,'typ',None) not in excluded_types]
            for o in remaining:
                try:
                    try:
                        items = o.attribute_als_text()
                    except Exception as ex_attr:
                        typ_name = getattr(o, 'typ', None) or o.__class__.__name__
                        try:
                            hdr_txt = f"{getattr(o, 'name', typ_name)} ({typ_name})"
                            hdr = self.font.render(hdr_txt, True, (255,255,255))
                            self.screen.blit(hdr, (panel_x, y)); y += 20
                        except Exception:
                            pass
                        required = ['x','y','richtung','typ','name']
                        missing = []
                        for a in required:
                            try:
                                if not hasattr(o, a):
                                    missing.append(a)
                            except Exception:
                                missing.append(a)
                        msg = None
                        if missing:
                            msg = f"Fehler in der Schülerklasse {typ_name}: Fehlende Attribute: {', '.join(missing)}"
                        else:
                            msg = f"Fehler beim Lesen der Schülerklasse {typ_name}: {ex_attr}"
                        try:
                            err = self.font.render(msg, True, (255,100,100))
                            self.screen.blit(err, (panel_x, y)); y += 20
                        except Exception:
                            pass
                        # small spacing after each problematic object
                        y += 6
                        continue

                    for k, v in items.items():
                        try:
                            val = v
                            if isinstance(k, str) and 'richt' in k.lower():
                                dm = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                                val = dm.get(str(v), str(v))
                            txt = f"{k}: {val}"
                            while self.font.size(txt)[0] > (self.screen.get_width() - panel_x - 20):
                                txt = txt[:-1]
                            txt = self.font.render(f"{k}: {val}", True, (240,240,240))
                            self.screen.blit(txt, (panel_x, y)); y += 20
                        except Exception:
                            continue
                    # small spacing after each object
                    y += 6
                except Exception:
                    try:
                        typ_name = getattr(o, 'typ', None) or o.__class__.__name__
                        msg = f"Fehler beim Anzeigen von {typ_name}"
                        err = self.font.render(msg, True, (255, 100, 100))
                        self.screen.blit(err, (panel_x, y)); y += 20
                    except Exception:
                        pass
                    y += 6
        except Exception:
            # if anything unexpected happens, fall back to previous generic loop
            try:
                for o in self.spielfeld.objekte:
                    try:
                        items = o.attribute_als_text()
                        for k, v in items.items():
                            txt = self.font.render(f"{k}: {v}", True, (240,240,240))
                            self.screen.blit(txt, (panel_x, y)); y += 20
                        y += 6
                    except Exception:
                        continue
            except Exception:
                pass
                y += 10
        """        
        if self._sieg:
            msg = self.font.render("Alle Herzen gesammelt!", True, (255, 230, 80))
            self.screen.blit(msg, (panel_x, y+10))"""

        # ... in framework/framework.py, in _zeichne_info() ...
        if self._hinweis:
            panel_x = self.spielfeld.level.breite * self.feldgroesse + 8
            max_w   = self.screen.get_width() - panel_x - 20
            line_h  = self.font.get_linesize()

            # einfache Wortumbruch-Logik
            words = self._hinweis.split()
            lines, cur = [], ""
            for w in words:
                test = (cur + " " + w).strip()
                if self.font.size(test)[0] <= max_w:
                    cur = test
                else:
                    if cur: lines.append(cur)
                    # falls einzelnes Wort länger als max_w ist -> harte Teilung
                    while self.font.size(w)[0] > max_w and len(w) > 1:
                        # finde maximale Teil-Länge
                        lo, hi = 1, len(w)
                        while lo < hi:
                            mid = (lo + hi) // 2 + 1
                            if self.font.size(w[:mid])[0] <= max_w: lo = mid
                            else: hi = mid - 1
                        lines.append(w[:lo])
                        w = w[lo:]
                    cur = w
            if cur: lines.append(cur)

            # oben im Panel zeichnen (immer sichtbar)
            y0 = y
            for i, line in enumerate(lines):
                msg = self.font.render(line, True, (255, 100, 100))
                self.screen.blit(msg, (panel_x, y0 + i * line_h))
        panel_w = self.screen.get_width() - panel_x - 8
        anzeige_h = self.screen.get_height() - 16
        pygame.draw.rect(self.screen, (80,80,80), (panel_x + panel_w - 10, 8, 6, anzeige_h))







    def _render_frame(self):
        self.screen.fill((0, 0, 0))

        # Nur lebende Objekte updaten
        for o in self.spielfeld.objekte:
            if not getattr(o, "tot", False):
                try:
                    o.update()
                except Exception as e:
                    pass
                    #print("[Update-Fehler]", e)

        # Jetzt alle zeichnen (auch tote!)
        self.spielfeld.zeichne(self.screen)
        self._zeichne_info()
        self._zeichne_sieg_overlay()

        pygame.display.flip()


    # --- Public API ---
    def sieg(self): self._sieg = True
    def beenden(self): self._running = False

    def level_oeffnen(self):
        """
        root = tk.Tk(); root.withdraw()
        pfad = filedialog.askopenfilename(filetypes=[("JSON Level","*.json")], title="Level öffnen")
        root.destroy()
        if pfad:
            self.spielfeld = Spielfeld(pfad, self, self.feldgroesse, True)
            breite = self.spielfeld.level.breite * self.feldgroesse + 280
            hoehe  = self.spielfeld.level.hoehe  * self.feldgroesse
            self.screen = pygame.display.set_mode((breite, hoehe))
            self._sieg = False
            self._render_frame()
            self._hinweis = None
            self._aktion_blockiert = False
        """
        
        self.spielfeld = Spielfeld(self.levelfile, self, self.feldgroesse, True)
        breite = self.spielfeld.level.breite * self.feldgroesse + 280
        hoehe  = self.spielfeld.level.hoehe  * self.feldgroesse
        self.screen = pygame.display.set_mode((breite, hoehe))
        self._sieg = False
        self._render_frame()
        self._hinweis = None
        self._aktion_blockiert = False

            
    def stoppe_programm(self, meldung="Ungültige Aktion"):
        """Bricht die Schüleraktions-Queue ab, aber Framework läuft weiter."""
        self._hinweis = meldung
        self._aktion_blockiert = True
        print(f"[Framework] {meldung}")  # optional für Debug
        
    def _zeichne_sieg_overlay(self):
        """Dunkelt den Spielfeldbereich ab und zeigt 'Level geschafft'."""
        if not self._sieg or self._aktion_blockiert:
            return  # keine Anzeige, wenn Sieg noch nicht aktiv oder blockiert wurde

        # Spielfeld-Bereich berechnen (ohne rechtes Panel)
        spielfeld_breite = self.spielfeld.level.breite * self.feldgroesse
        spielfeld_hoehe  = self.spielfeld.level.hoehe  * self.feldgroesse

        overlay = pygame.Surface((spielfeld_breite, spielfeld_hoehe), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # halbtransparentes Schwarz
        self.screen.blit(overlay, (0, 0))

        # Text mittig anzeigen
        text = self.big.render("Level geschafft!", True, (255, 230, 80))
        text_rect = text.get_rect(center=(spielfeld_breite // 2, spielfeld_hoehe // 2))
        self.screen.blit(text, text_rect)



    def starten(self):
        import os, sys, time
        clock = pygame.time.Clock()

        # Test-Modus: sofort nach Sieg/Timeout den Prozess beenden (damit ein externes Runner-Skript weiter macht)
        TEST_MODE = os.getenv("OOP_TEST", "") == "1"
        TEST_TIMEOUT_MS = int(os.getenv("OOP_TEST_TIMEOUT_MS", "8000"))

        start_time = time.time()

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    # --- neu: Enter (Return) nimmt alle Gegenstände auf der aktuellen Heldposition auf ---
                    try:
                        if event.key == pygame.K_RETURN:
                            try:
                                sp = getattr(self, "spielfeld", None)
                                held = getattr(sp, "held", None) if sp else None
                                # Prefer a more specific single-item pickup if available
                                if held:
                                    if hasattr(held, "nehm_auf_einfach"):
                                        try:
                                            held.nehm_auf_einfach()
                                        except Exception:
                                            pass
                                    elif hasattr(held, "nehm_auf_alle"):
                                        try:
                                            held.nehm_auf_alle()
                                        except Exception:
                                            pass
                                    elif hasattr(held, "nehme_auf_alle"):
                                        try:
                                            held.nehme_auf_alle()
                                        except Exception:
                                            pass
                            except Exception:
                                pass
                            # do not fall through to the registered handler for RETURN
                            # (avoid invoking accidental or duplicate actions such as using the key immediately)
                            # handled pickup explicitly; don't print debug to avoid noisy output
                            pass
                            continue
                    except Exception:
                        pass

                    # bestehende Tasten-Registrierung aufrufen (wie bisher)
                    fn = self._tasten.get(event.key)
                    if fn:
                        try:
                            self._aus_tastatur = True
                            fn()
                        except Exception as e:
                            print("Fehler in Tastenaktion:", e)
                        finally:
                            self._aus_tastatur = False
                elif event.type == pygame.MOUSEWHEEL:
                    self.info_scroll += event.y * 20
                    if self.info_scroll < 0:
                        self.info_scroll = 0
            # Sieg erkennen (kombinierte Bedingungen)
            try:
                if not self._aktion_blockiert and getattr(self, 'spielfeld', None) and self.spielfeld.check_victory():
                    self.sieg()
            except Exception:
                # fallback to legacy hearts-only check
                if not self._aktion_blockiert and not self.spielfeld.gibt_noch_herzen():
                    self.sieg()

            # Wenn im Testmodus: beende Prozess bei Sieg oder bei Timeout
            if TEST_MODE:
                # Erfolg: sofort exit(0)
                if self._sieg and not self._aktion_blockiert:
                    print("[TEST] Level erfolgreich beendet.")
                    pygame.quit()
                    sys.exit(0)

                # Timeout
                elapsed_ms = int((time.time() - start_time) * 1000)
                if elapsed_ms > TEST_TIMEOUT_MS:
                    print(f"[TEST] Timeout ({TEST_TIMEOUT_MS}ms): Noch Herzen vorhanden oder blockiert.")
                    pygame.quit()
                    sys.exit(2)

            # --- Render: Objekt-Inspektor (rechte Seite) erweitern um Inventaranzeige ---
            try:
                # existierender inspector-render-code befindet sich irgendwo in _render_frame oder hier;
                # füge das Inventar-Rendering direkt an der Stelle ein, an der held/knappe/monster angezeigt werden.
                # defensive search for inspector surface / font
                screen = getattr(self, "_screen", None) or pygame.display.get_surface()
                if screen:
                    font = pygame.font.SysFont(None, 20)
                    x0 = screen.get_width() - 200  # rechter Bereich
                    y0 = 20
                    line_h = 20

                    sp = getattr(self, "spielfeld", None)
                    if sp:
                        # Reihenfolge: Held, Knappe, dann Monster(s)
                        entities = []
                        if getattr(sp, "held", None):
                            entities.append(sp.held)
                        if getattr(sp, "knappe", None):
                            entities.append(sp.knappe)
                        # append monsters
                        for o in sp.objekte:
                            try:
                                typ = getattr(o, "typ", "") or getattr(o, "name", "")
                                if typ and "monster" in str(typ).lower():
                                    entities.append(o)
                            except Exception:
                                continue

                        # Zeichne Basisinfos + Inventar
                        for ent in entities:
                            try:
                                # header: Name (Typ)
                                name = getattr(ent, "name", getattr(ent, "typ", ent.__class__.__name__))
                                hdr = font.render(f"{name} ({getattr(ent,'typ', '')})", True, (255,255,255))
                                screen.blit(hdr, (x0, y0))
                                y0 += line_h
                                # position + richtung (one per line, direction displayed as N/O/W/S)
                                try:
                                    ex = getattr(ent, 'x', 0)
                                    ey = getattr(ent, 'y', 0)
                                    er = getattr(ent, 'richtung', '?')
                                    dm = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                                    rdisp = dm.get(str(er), str(er))
                                    sx = font.render(f"x={ex}", True, (200,200,200))
                                    screen.blit(sx, (x0, y0)); y0 += line_h
                                    sy = font.render(f"y={ey}", True, (200,200,200))
                                    screen.blit(sy, (x0, y0)); y0 += line_h
                                    sr = font.render(f"richtung={rdisp}", True, (200,200,200))
                                    screen.blit(sr, (x0, y0)); y0 += line_h
                                except Exception:
                                    try:
                                        xyt = font.render(f"x={getattr(ent,'x',0)} y={getattr(ent,'y',0)} dir={getattr(ent,'richtung','?')}", True, (200,200,200))
                                        screen.blit(xyt, (x0, y0)); y0 += line_h
                                    except Exception:
                                        y0 += line_h

                                # Spells / gesammelte Sprueche: falls vorhanden als Text (bestehendes Verhalten)
                                spells = getattr(ent, "spruch", None) or getattr(ent, "zauberspruch", None) or getattr(ent, "_spruch", None)
                                if spells:
                                    srf = font.render(f"Spruch: {spells}", True, (180,220,180))
                                    screen.blit(srf, (x0, y0))
                                    y0 += line_h

                                # Inventar: falls vorhanden, zeichne kleine Icons für Schlüssel
                                inv = getattr(ent, "inventar", None)
                                if inv is not None:
                                    item_x = x0
                                    item_y = y0
                                    # compute area available for icons (right panel width minus small margin)
                                    max_area = max(100, screen.get_width() - x0 - 20)
                                    # target: show up to 5 icons in a row; compute icon size accordingly
                                    # reserve ~4px spacing between icons
                                    per_icon_space = max_area // 5
                                    icon_size = max(12, min(32, per_icon_space - 4))
                                    spacing = icon_size + 4
                                    # draw small label
                                    lbl = font.render("Inventar:", True, (220,220,160))
                                    screen.blit(lbl, (item_x, item_y))
                                    item_y += line_h
                                    # draw icons in rows, show all collected keys (including duplicates)
                                    ix = 0
                                    for it in list(inv):
                                        try:
                                            color = getattr(it, "farbe", None) or getattr(it, "color", None) or getattr(it, "key_color", None)
                                            # If color missing, try to guess from the item name (best-effort)
                                            if not color:
                                                try:
                                                    nm = str(getattr(it, 'name', '')).lower()
                                                    if 'gold' in nm:
                                                        color = 'golden'
                                                    elif 'green' in nm or 'gruen' in nm or 'grün' in nm:
                                                        color = 'green'
                                                    elif 'blue' in nm or 'blau' in nm:
                                                        color = 'blue'
                                                    elif 'red' in nm or 'rot' in nm:
                                                        color = 'red'
                                                    elif 'violet' in nm or 'violett' in nm or 'purple' in nm:
                                                        color = 'violet'
                                                except Exception:
                                                    color = None
                                            surf = None
                                            try:
                                                if hasattr(it, "bild") and getattr(it, "bild", None) is not None:
                                                    surf = it.bild
                                                else:
                                                    import os, pygame as _pg
                                                    cand = None
                                                    if color:
                                                        # try several likely base paths so sprite loading
                                                        # works regardless of current working dir (Thonny etc.)
                                                        bases = [
                                                            os.getcwd(),
                                                            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                                                            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),
                                                        ]
                                                        for b in bases:
                                                            p = os.path.join(b, 'sprites', f'key_{color}.png')
                                                            if os.path.exists(p):
                                                                cand = p
                                                                break
                                                    if cand:
                                                        try:
                                                            surf = _pg.image.load(cand).convert_alpha()
                                                        except Exception:
                                                            surf = None
                                            except Exception:
                                                surf = None

                                            if surf:
                                                try:
                                                    surf_small = pygame.transform.smoothscale(surf, (icon_size, icon_size))
                                                    screen.blit(surf_small, (item_x + ix * spacing, item_y))
                                                except Exception:
                                                    pygame.draw.rect(screen, (200,200,0), (item_x + ix * spacing, item_y, icon_size, icon_size))
                                            else:
                                                # fallback colored rect for keys or text for generic items
                                                if color:
                                                    pygame.draw.rect(screen, (200,200,0), (item_x + ix * spacing, item_y, icon_size, icon_size))
                                                else:
                                                    nm = getattr(it, 'name', str(it))[:10]
                                                    s = font.render(nm, True, (200,200,200))
                                                    screen.blit(s, (item_x + ix * spacing, item_y))

                                            ix += 1
                                            if ix >= 5:
                                                ix = 0
                                                item_y += icon_size + 6
                                        except Exception:
                                            continue
                                    # advance y0 after inventory rendering
                                    y0 = item_y + icon_size + 6
                            except Exception:
                                continue
            except Exception:
                pass

            self._render_frame()
            clock.tick(60)
        # Main loop exited: ensure SDL/pygame is cleanly shut down so IDEs (Thonny)
        # regain control and the window closes. Do not raise SystemExit here.
        try:
            pygame.quit()
        except Exception:
            pass

