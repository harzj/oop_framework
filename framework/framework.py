# framework/framework.py
import pygame
import tkinter as tk
from tkinter import filedialog
from .spielfeld import Spielfeld


def _load_version_banner():
    """Read version.json from the project root and return a banner string."""
    try:
        import json
        from pathlib import Path
        from datetime import date
        vfile = Path(__file__).resolve().parents[1] / 'version.json'
        v = json.loads(vfile.read_text(encoding='utf-8'))
        today = date.today().strftime('%d.%m.%Y')
        return (f"OOPventure Version {v['major']}.{v['minor']}.{v['patch']} "
                f"Build {v['build']} vom {today}")
    except Exception:
        pass
    try:
        # Fallback: _version.py bundled inside the distribution ZIP
        from pathlib import Path
        vf = Path(__file__).resolve().parent / '_version.py'
        ns = {}
        exec(vf.read_text(encoding='utf-8'), ns)  # noqa: S102
        return f"OOPventure Version {ns.get('__version__', '?')}"
    except Exception:
        return "OOPventure"


class Framework:
    def __init__(self, levelnummer=1, feldgroesse=64, auto_erzeuge_objekte=True, w = False, splash=False):
        print(_load_version_banner())
        print("(c) 2025 - 2026 Johannes Harz | Fachkonferenz Informatik | Cusanus Gymnasium St. Wendel")
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
        # Set of object ids that the student has obtained a reference to.
        # Used by _zeichne_info to decide which objects to display in the inspector.
        self._inspector_refs = set()
        # Maps object id → variable name used by the student (e.g. 'm', 'knappe')
        self._inspector_ref_names = {}
        # F1 help window state
        self._help_visible = False
        self._help_tab = 1   # 0=Generelle Hilfe, 1=Held, ...
        self._help_scroll = 0
        self._help_tab_rects = []
        self._help_prev_size = None   # screen size before resize for F1
        self._help_detach_rect = None  # clickable "own window" button rect
        # Inspector panel minimum width – grows automatically to fit text
        self._inspector_panel_width = 280




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
        pygame.display.set_caption("OOPventure")

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

    def _register_inspector_ref(self, obj, name=None):
        """Register obj so it appears in the right-panel inspector.
        Call this whenever student code obtains a reference to a Knappe, Monster, etc.
        name: optional variable name the student used (e.g. 'm', 'knappe').
        """
        try:
            if obj is not None:
                oid = id(obj)
                self._inspector_refs.add(oid)
                if name:
                    self._inspector_ref_names[oid] = name
        except Exception:
            pass

    def _ensure_inspector_panel(self):
        """Measure all inspector text before drawing; expand the window if any
        string would overflow the panel.  Called once per frame before render."""
        try:
            sp = getattr(self, 'spielfeld', None)
            if sp is None:
                return
            refs = getattr(self, '_inspector_refs', set())
            ref_names = getattr(self, '_inspector_ref_names', {})

            texts = []
            # Held
            held = getattr(sp, 'held', None)
            if held:
                stud = getattr(held, '_student', None)
                obj  = stud if stud is not None else held
                texts.append(f"Name: {getattr(obj, 'name', None) or 'namenloser held'}")

            # Knappe
            kn = getattr(sp, 'knappe', None)
            if kn and id(kn) in refs:
                texts.append(f"Objektname: {ref_names.get(id(kn), getattr(kn, 'typ', 'Knappe'))}")
                texts.append(f"Name: {getattr(kn, 'name', None) or 'namenloser knappe'}")

            # Monster / Bogenschuetze
            for o in getattr(sp, 'objekte', []):
                if getattr(o, 'typ', None) in ('Monster', 'Bogenschuetze') and id(o) in refs:
                    texts.append(f"Objektname: {ref_names.get(id(o), getattr(o, 'typ', 'Monster'))}")
                    texts.append(f"Name: {getattr(o, 'name', None) or 'Monster'}")

            if not texts:
                return

            # 8 = left gap inside panel, 18 = scrollbar + right margin
            max_text_px = max(self.font.size(t)[0] for t in texts)
            panel_x     = self.spielfeld.level.breite * self.feldgroesse + 8
            needed_w    = panel_x + max_text_px + 18
            if needed_w > self.screen.get_width():
                game_w  = self.spielfeld.level.breite * self.feldgroesse
                game_h  = self.spielfeld.level.hoehe  * self.feldgroesse
                new_panel_w = max(getattr(self, '_inspector_panel_width', 280),
                                  max_text_px + 30)   # 30 = margins + breathing room
                self._inspector_panel_width = new_panel_w
                self.screen = pygame.display.set_mode((game_w + new_panel_w, game_h))
        except Exception:
            pass

    # --- Hilfe-Fenster (F1) ---

    def _get_held_methoden(self):
        return [
            ("geh()",              "delay (opt.): Pause in ms",                              "Bewegt den Helden einen Schritt in die Richtung, in die er blickt."),
            ("links()",            "delay (opt.): Pause in ms",                              "Dreht den Helden um 90° nach links (gegen den Uhrzeigersinn)."),
            ("rechts()",           "delay (opt.): Pause in ms",                              "Dreht den Helden um 90° nach rechts (im Uhrzeigersinn)."),
            ("zurueck()",          "delay (opt.): Pause in ms",                              "Bewegt den Helden einen Schritt rückwärts (ohne Drehung)."),
            ("nimm_herz()",          "delay (opt.): Pause in ms",                              "Hebt den Gegenstand auf der aktuellen Position auf."  ),  # früher nehme_auf()
            ("attack()",           "delay (opt.): Pause in ms",                              "Greift das Objekt direkt vor dem Helden an."),
            ("was_ist_vorn()",     "–",                                                      "Gibt den Typ des Objekts vor dem Helden als Text zurück."),
            ("was_ist_links()",    "–",                                                      "Gibt den Typ des Objekts links vom Helden als Text zurück."),
            ("was_ist_rechts()",   "–",                                                      "Gibt den Typ des Objekts rechts vom Helden als Text zurück."),
            ("gib_objekt_vor_dir()","–",                                                    "Gibt die Referenz auf das Objekt direkt vor dem Helden zurück."),
            ("gib_knappe()",       "–",                                                      "Gibt die Referenz auf den Knappe zurück (falls vorhanden)."),
            ("ist_auf_herz()",     "–",                                                      "Gibt True zurück, wenn der Held auf einem Herz steht."),
            ("herzen_vor_mir()",   "–",                                                      "Gibt die Anzahl der Herzen in direkter Sichtlinie zurück. Hindernisse blockieren die Sicht."),
            ("lese_spruch()",      "delay (opt.): Pause in ms",                              "Liest und merkt sich den Spruch auf einem Zettel, wenn der Held auf diesem steht."),
            ("sage_spruch()",      "code (opt.): Spruchtext,  delay (opt.): Pause in ms",   "Sagt den gemerkten Spruch (falls vorhanden), um eine Tür damit zu öffnen."),
            ("bediene_tor()",      "delay (opt.): Pause in ms",                              "Betätigt das Tor, das direkt vor dem Helden steht."),
        ]

    def _get_knappe_methoden(self):
        return [
            ("geh()",               "delay (opt.): Pause in ms",                             "Bewegt den Knappe einen Schritt in die Richtung, in die er blickt."),
            ("links()",             "delay (opt.): Pause in ms",                             "Dreht den Knappe um 90° nach links."),
            ("rechts()",            "delay (opt.): Pause in ms",                             "Dreht den Knappe um 90° nach rechts."),
            ("zurueck()",           "delay (opt.): Pause in ms",                             "Bewegt den Knappe einen Schritt rückwärts (ohne Drehung)."),
            ("nimm_herz()",           "delay (opt.): Pause in ms",                             "Hebt einen Gegenstand auf der aktuellen Position auf."  ),  # früher nehme_auf()
            ("attack()",            "delay (opt.): Pause in ms",                             "Greift das Objekt direkt vor dem Knappe an."),
            ("was_ist_vorn()",      "–",                                                     "Gibt den Typ des Objekts vor dem Knappe als Text zurück."),
            ("was_ist_links()",     "–",                                                     "Gibt den Typ des Objekts links vom Knappe als Text zurück."),
            ("was_ist_rechts()",    "–",                                                     "Gibt den Typ des Objekts rechts vom Knappe als Text zurück."),
            ("gib_objekt_vor_dir()","–",                                                     "Gibt die Referenz auf das Objekt direkt vor dem Knappe zurück."),
            ("lese_spruch()",       "delay (opt.): Pause in ms",                             "Liest und merkt sich den Spruch auf einem Zettel, wenn der Knappe auf diesem steht."),
            ("sage_spruch()",       "code (opt.): Spruchtext,  delay (opt.): Pause in ms",  "Sagt den gemerkten Spruch (falls vorhanden), um eine Tür damit zu öffnen."),
            ("bediene_tor()",       "delay (opt.): Pause in ms",                             "Betätigt das Tor direkt vor dem Knappe."),
        ]

    def _get_monster_methoden(self):
        return [
            ("geh()",              "–",                                                    "Bewegt das Monster einen Schritt vorwärts."),
            ("links()",            "–",                                                    "Dreht das Monster um 90° nach links."),
            ("rechts()",           "–",                                                    "Dreht das Monster um 90° nach rechts."),
            ("zurueck()",          "–",                                                    "Bewegt das Monster einen Schritt rückwärts (ohne Drehung)."),
            ("angriff()",          "opfer (opt.): Zielobjekt,  delay (opt.): Pause in ms","Führt einen Angriff auf das Zielobjekt aus."),
            ("was_ist_vorn()",     "–",                                                    "Gibt den Typ des Objekts vor dem Monster als Text zurück."),
            ("gib_objekt_vor_dir()","–",                                                  "Gibt die Referenz auf das Objekt direkt vor dem Monster zurück."),
        ]

    def _get_zettel_methoden(self):
        return [
            ("gib_spruch()",      "–",                     "Gibt den Spruch auf dem Zettel als String zurück."),
            ("spruch_ausgeben()", "–",                     "Gibt den Spruch des Zettels auf der Konsole aus."),
        ]

    def _get_tuer_methoden(self):
        return [
            ("ist_passierbar()",   "–",                     "Gibt True zurück, wenn die Tür geöffnet / passierbar ist."),
            ("spruch_anwenden()",  "s: str – der Spruch",   "Versucht, die Tür mit dem übergebenen Spruch zu öffnen."),
        ]

    def _get_tuer_farbig_methoden(self):
        return [
            ("ist_passierbar()",          "–",                          "Gibt True zurück, wenn die Tür geöffnet / passierbar ist."),
            ("schluessel_verwenden(k)",   "k: Schluessel",              "Öffnet die Tür, wenn die Farbe des Schlüssels mit der Türfarbe übereinstimmt."),
            ("get_farbe()",               "–",                          "Gibt die Farbe der Tür zurück: 'blue', 'golden', 'green', 'red', 'violet'."),
            ("get_offen()",               "–",                          "Gibt True zurück, wenn die Tür geöffnet ist."),
        ]

    def _get_schluessel_methoden(self):
        return [
            ("get_farbe()",         "–",              "Gibt die Farbe des Schlüssels zurück: 'blue', 'golden', 'green', 'red', 'violet'."),
            ("set_farbe(f)",        "f: str",         "Setzt die Farbe des Schlüssels auf die angegebene Farbe: 'blue', 'golden', 'green', 'red', 'violet'."),
            ("setze_position(x, y)", "x, y: int",     "Setzt den Schlüssel auf die angegebene Position (muss frei sein)."),
        ]

    def _get_impl_methoden(self, klasse, required_methods):
        """
        Für Implementierungs-Level (35–58): liefert Methodenliste für eine
        vom Schüler zu implementierende Klasse.
        Erste Zeile: Konstruktor, danach nur die geforderten Methoden.
        """
        # Lookup aller bekannten Methoden (stripped name → Tabelleneintrag)
        _all = {}
        for src in [
            self._get_held_methoden(),
            self._get_knappe_methoden(),
            self._get_monster_methoden(),
            self._get_zettel_methoden(),
            self._get_tuer_methoden(),
            self._get_tuer_farbig_methoden(),
            self._get_schluessel_methoden(),
        ]:
            for entry in src:
                key = entry[0].split('(')[0]
                if key not in _all:
                    _all[key] = entry

        # Ergänzung: Methoden, die typisch für Impl-Klassen gefordert werden
        _extra = {
            "get_x":            ("get_x()",              "–",                   "Gibt die x-Position des Objekts zurück."),
            "get_y":            ("get_y()",              "–",                   "Gibt die y-Position des Objekts zurück."),
            "get_typ":          ("get_typ()",            "–",                   "Gibt den Typ des Objekts als String zurück."),
            "get_richtung":     ("get_richtung()",       "–",                   "Gibt die aktuelle Blickrichtung zurück ('up','down','left','right')."),
            "set_richtung":     ("set_richtung(r)",      "r: str",              "Setzt die Blickrichtung ('up','down','left','right')."),
            "get_spruch":       ("get_spruch()",         "–",                   "Gibt den Spruch des Zettels als String zurück."),
            "set_spruch":       ("set_spruch(s)",        "s: str",              "Setzt den Spruch des Zettels auf den übergebenen Wert."),
            "get_weiblich":     ("get_weiblich()",       "–",                   "Gibt True zurück, wenn der Held weiblich ist."),
            "item_hinzufuegen": ("item_hinzufuegen(item)", "item: Gegenstand",  "Fügt einen Gegenstand dem Inventar hinzu."),
            "hat_item":         ("hat_item(item)",       "item: Gegenstand",    "Gibt True zurück, wenn der Gegenstand im Inventar ist."),
            "anzahl_items":     ("anzahl_items()",       "–",                   "Gibt die Anzahl der Items im Inventar zurück."),
            "gib_item_nummer":  ("gib_item_nummer(n)",  "n: int",              "Gibt das Item mit dem angegebenen Index zurück (0-basiert)."),
            "gold_sammeln":     ("gold_sammeln(menge)",  "menge: int",          "Fügt die angegebene Goldmenge zum Inventar hinzu."),
            "ist_voll":         ("ist_voll()",           "–",                   "Gibt True zurück, wenn das Inventar voll ist."),
            "sammeln":          ("sammeln(inventar)",    "inventar: Inventar",  "Legt den Gegenstand in das übergebene Inventar."),
        }
        for key, entry in _extra.items():
            if key not in _all:
                _all[key] = entry

        # Konstruktor-Zeile als erste Zeile
        konstr_row = ("__init__(self, ...)", "–", f"Konstruktor der Klasse {klasse}.")
        result = [konstr_row]
        for m in required_methods:
            if m in _all:
                result.append(_all[m])
            else:
                result.append((f"{m}()", "–", "Muss von dir implementiert werden."))
        return result

    def _get_konstruktoren(self):
        """Gibt eine Liste von (Klasse, Signatur, Beschreibung) für den Konstruktoren-Tab zurück."""
        return [
            ("Held",       "x, y: int,  r: str,  weiblich: bool",
             "from framework.held import Held\nr = 'up','down','left','right'  |  weiblich = True (Heldin) / False (Held)"),
            ("Knappe",     "x, y: int,  r: str",
             "from framework.knappe import Knappe\nr = 'up', 'down', 'left' oder 'right'"),
            ("Hindernis",  "art: str,  x, y: int",
             "from framework.hindernis import Hindernis\nart = 'Baum', 'Busch' oder 'Berg'"),
            ("Herz",       "x, y: int",
             "from framework.herz import Herz\nPlatziert ein Herz auf dem Spielfeld."),
            ("Schluessel", "x, y: int",
             "from framework.schluessel import Schluessel\nStandardfarbe: 'green'. Weitere Farben: 'blue', 'golden', 'red', 'violet'."),
            ("Tor",        "x, y: int,  offen: bool",
             "from framework.tor import Tor\noffen = True (Tor geöffnet) oder False (Tor geschlossen)"),
            ("Tuer",       "x, y: int,  farbe: str",
             "from framework.tuer import Tuer\nFarbige Tür: farbe = 'blue','golden','green','red','violet'"),
            ("Tuer",       "x, y: int",
             "from framework.tuer import Tuer\nTür ohne Farbe → wird mit Zauberspruch geöffnet"),
        ]

    def _render_konstruktoren_tab(self, surf, fonts, colors, x, y, w):
        """Zeichnet den Konstruktoren-Tab: 3-spaltige Tabelle (Klasse | Signatur | Hinweis)."""
        COL1 = 120
        COL2 = 260
        COL3 = w - COL1 - COL2 - 12
        PAD  = 4
        body = fonts['body']
        hdr  = fonts['header']
        lh   = body.get_linesize()

        # Header
        pygame.draw.rect(surf, colors['header_bg'], (x, y, w, lh + PAD * 2))
        surf.blit(hdr.render("Klasse",     True, colors['header_text']), (x + 4,               y + PAD))
        surf.blit(hdr.render("Parameter",  True, colors['header_text']), (x + COL1 + 4,        y + PAD))
        surf.blit(hdr.render("Hinweis",    True, colors['header_text']), (x + COL1 + COL2 + 4, y + PAD))
        y += lh + PAD * 2 + 2

        for i, (klasse, sig, hinweis) in enumerate(self._get_konstruktoren()):
            hinweis_parts = hinweis.split('\n')
            sig_lines     = self._wrap_text(body, sig,             COL2 - 8)
            hinweis_lines = []
            for part in hinweis_parts:
                hinweis_lines.extend(self._wrap_text(body, part, COL3 - 6))
            row_h = max(len(sig_lines), len(hinweis_lines)) * lh + PAD * 2

            pygame.draw.rect(surf, colors['row_even'] if i % 2 == 0 else colors['row_odd'],
                             (x, y, w, row_h))
            pygame.draw.line(surf, colors['sep'], (x + COL1,        y), (x + COL1,        y + row_h))
            pygame.draw.line(surf, colors['sep'], (x + COL1 + COL2, y), (x + COL1 + COL2, y + row_h))

            surf.blit(body.render(klasse, True, colors['col_method']), (x + 4, y + PAD))
            for li, sl in enumerate(sig_lines):
                surf.blit(body.render(sl, True, colors['col_param']),
                          (x + COL1 + 4, y + PAD + li * lh))
            for li, hl in enumerate(hinweis_lines):
                surf.blit(body.render(hl, True, colors['col_desc']),
                          (x + COL1 + COL2 + 4, y + PAD + li * lh))
            y += row_h

        return y + 8

    def _wrap_text(self, font, text, max_width):
        """Bricht text in Zeilen auf, die max_width px nicht überschreiten."""
        words = text.split(' ')
        lines, current = [], ''
        for word in words:
            test = (current + ' ' + word).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines if lines else ['']

    def _render_methoden_tabelle(self, surf, fonts, colors, x, y, w, methoden):
        """Zeichnet eine 3-spaltige Tabelle: Methode | Parameter | Beschreibung."""
        COL1 = 185
        COL2 = 210
        COL3 = w - COL1 - COL2 - 12
        PAD = 4
        body = fonts['body']
        hdr  = fonts['header']
        lh   = body.get_linesize()

        # Tabellenheader
        pygame.draw.rect(surf, colors['header_bg'], (x, y, w, lh + PAD * 2))
        surf.blit(hdr.render("Methode",      True, colors['header_text']), (x + 4,               y + PAD))
        surf.blit(hdr.render("Parameter",    True, colors['header_text']), (x + COL1 + 4,        y + PAD))
        surf.blit(hdr.render("Beschreibung", True, colors['header_text']), (x + COL1 + COL2 + 4, y + PAD))
        y += lh + PAD * 2 + 2

        for i, (method, params, desc) in enumerate(methoden):
            desc_lines   = self._wrap_text(body, desc,   COL3 - 6)
            params_lines = self._wrap_text(body, params, COL2 - 8)
            row_h = max(len(desc_lines), len(params_lines)) * lh + PAD * 2

            pygame.draw.rect(surf, colors['row_even'] if i % 2 == 0 else colors['row_odd'], (x, y, w, row_h))
            pygame.draw.line(surf, colors['sep'], (x + COL1,        y), (x + COL1,        y + row_h))
            pygame.draw.line(surf, colors['sep'], (x + COL1 + COL2, y), (x + COL1 + COL2, y + row_h))

            surf.blit(body.render(method, True, colors['col_method']), (x + 4, y + PAD))
            for li, pl in enumerate(params_lines):
                surf.blit(body.render(pl, True, colors['col_param']),  (x + COL1 + 4,        y + PAD + li * lh))
            for li, dl in enumerate(desc_lines):
                surf.blit(body.render(dl, True, colors['col_desc']),   (x + COL1 + COL2 + 4, y + PAD + li * lh))
            y += row_h

        return y

    def _render_hilfe_allgemein(self, surf, fonts, colors, x, y, w, sp):
        """Rendert den 'Generelle Hilfe'-Tab aus den Leveldaten."""
        bf  = fonts['hint_body']
        tf  = fonts['hint_title']
        lh  = bf.get_linesize() + 2
        tlh = tf.get_linesize() + 4

        def blit_bullet(text, color, indent=8):
            nonlocal y
            for ln in self._wrap_text(bf, f"  \u2022 {text}", w - indent - 20):
                surf.blit(bf.render(ln, True, color), (x + indent, y)); y += lh

        def section(title):
            nonlocal y
            pygame.draw.line(surf, colors['sep'], (x, y), (x + w, y)); y += 8
            surf.blit(tf.render(title, True, colors['header_text']), (x, y)); y += tlh

        if sp is None:
            surf.blit(bf.render("Kein Level geladen.", True, colors['col_desc']), (x, y))
            return y + lh

        victory  = getattr(sp, 'victory_settings', {}) or {}
        settings = getattr(sp, 'settings', {}) or {}
        hints    = settings.get('hints', {}) or {}
        classes_present = bool(victory.get('classes_present', False))
        rebuild         = bool(victory.get('rebuild_mode', False))

        # ── Phase ──────────────────────────────────────────────────────────
        phase_custom = hints.get('phase', '').strip() if isinstance(hints.get('phase'), str) else ''
        if phase_custom:
            phase_text  = phase_custom
            phase_color = (255, 200, 100)
        else:
            phase_text  = "Phase 2: Eigene Klassen schreiben" if classes_present else "Phase 1: Helden programmieren"
            phase_color = (255, 200, 100) if classes_present else (120, 200, 255)
        surf.blit(tf.render(f"Phase:  {phase_text}", True, phase_color), (x, y)); y += tlh

        # ── Siegbedingungen ────────────────────────────────────────────────
        section("Siegbedingungen:")

        goals_drawn = 0

        # 1. Herzen sammeln (default True when key absent, matching check_victory logic)
        collect_hearts = True if 'collect_hearts' not in victory else bool(victory.get('collect_hearts'))
        if collect_hearts:
            herzen = [o for o in getattr(sp, 'objekte', [])
                      if getattr(o, 'typ', '') == 'Herz' and not getattr(o, 'tot', False)]
            anzahl = len(herzen)
            if anzahl > 1:
                blit_bullet(f"Sammle alle {anzahl} Herzen auf dem Spielfeld ein.", colors['col_desc'])
            else:
                blit_bullet("Sammle alle Herzen auf dem Spielfeld ein.", colors['col_desc'])
            goals_drawn += 1

        # 2. Position erreichen
        mt = victory.get('move_to')
        if mt and isinstance(mt, dict) and mt.get('enabled'):
            tx, ty = mt.get('x', '?'), mt.get('y', '?')
            blit_bullet(f"Bewege den Helden zum Zielfeld an Position ({tx}, {ty}).", colors['col_desc'])
            goals_drawn += 1

        # 3. Rebuild-Modus
        if rebuild:
            blit_bullet("Baue das Spielfeld so nach, wie es in der Vorlage vorgegeben ist.", colors['col_desc'])
            goals_drawn += 1

        # 4. Klassen implementieren (Phase 2)
        if classes_present:
            req = settings.get('class_requirements', {}) or {}
            if req:
                for cls_name, cls_info in req.items():
                    if not isinstance(cls_info, dict):
                        blit_bullet(f"Schreibe die Klasse '{cls_name}'.", colors['col_desc'])
                        continue
                    parts = [f"Implementiere die Klasse '{cls_name}'"]
                    inherits = cls_info.get('inherits')
                    if inherits and inherits not in ('None', 'none', None):
                        parts.append(f"die von '{inherits}' erbt")
                    methods = cls_info.get('methods', [])
                    attrs   = cls_info.get('attributes', [])
                    details = []
                    if attrs:
                        details.append(f"Attribute: {', '.join(attrs)}")
                    if methods:
                        details.append(f"Methoden: {', '.join(m + '()' for m in methods)}")
                    line = ' '.join(parts) + '.'
                    if details:
                        line += '  (' + '  |  '.join(details) + ')'
                    blit_bullet(line, colors['col_desc'])
                goals_drawn += 1
            else:
                blit_bullet("Implementiere die geforderten Klassen.", colors['col_desc'])
                goals_drawn += 1

        if goals_drawn == 0:
            blit_bullet("Erfülle die Siegbedingung des Levels.", colors['col_desc'])
        y += 4

        # ── Level-spezifische Hinweise aus JSON ────────────────────────────
        hints_text  = hints.get('text', []) or []
        hints_code  = hints.get('code', []) or []

        # ── Tipps ──────────────────────────────────────────────────────────
        section("Tipps:")
        if hints_text:
            for ht in hints_text:
                blit_bullet(ht, colors['hint_text'])
        elif not classes_present:
            blit_bullet("Bewege den Helden mit geh(), links() und rechts().", colors['hint_text'])
            if collect_hearts:
                blit_bullet("Gehe auf ein Herz-Feld und rufe nimm_herz() auf.", colors['hint_text'])
            if mt and isinstance(mt, dict) and mt.get('enabled'):
                blit_bullet("Du erreichst das Ziel, wenn der Held exakt auf dem markierten Feld steht.", colors['hint_text'])
        else:
            blit_bullet("Deine Klasse muss alle Pflichtattribute im __init__ setzen.", colors['hint_text'])
            blit_bullet("Vergiss nicht, super().__init__(...) im Konstruktor aufzurufen.", colors['hint_text'])
            blit_bullet("Nutze das Klassendiagramm im Arbeitsblatt als Vorlage.", colors['hint_text'])

        # ── Codebeispiel ────────────────────────────────────────────────────
        if hints_code:
            y += 6
            section("Codebeispiel:")
            code_bg = colors.get('code_bg', (22, 28, 48))
            padding = 8
            for code_line in hints_code:
                rw = w - padding * 2
                pygame.draw.rect(surf, code_bg, (x + padding, y, rw, lh + 2))
                surf.blit(bf.render(code_line, True, (160, 230, 160)), (x + padding + 4, y + 1))
                y += lh + 2
            y += 4

        return y

    # --- Hilfe-Fenstergröße verwalten ---
    # Level 0 hat 7×7 Tiles → Spielbreite 7*64 + 280 = 728, Höhe 7*64 = 448.
    # Das Hilfspanel braucht min. 880×580 plus etwas Rahmen.
    _HELP_MIN_W = 960   # min. Spielfensterbreite damit F1-Panel gut lesbar ist
    _HELP_MIN_H = 640   # min. Spielfensterhöhe

    def _ensure_help_window_size(self):
        """Vergrößert das Fenster temporär, wenn es kleiner als _HELP_MIN_* ist."""
        try:
            sw, sh = self.screen.get_size()
            if sw < self._HELP_MIN_W or sh < self._HELP_MIN_H:
                self._help_prev_size = (sw, sh)
                new_w = max(sw, self._HELP_MIN_W)
                new_h = max(sh, self._HELP_MIN_H)
                self.screen = pygame.display.set_mode((new_w, new_h))
        except Exception:
            pass

    def _restore_help_window_size(self):
        """Stellt die Fenstergröße vor dem F1-Öffnen wieder her."""
        try:
            prev = getattr(self, '_help_prev_size', None)
            if prev:
                self.screen = pygame.display.set_mode(prev)
                self._help_prev_size = None
        except Exception:
            pass

    def _open_help_in_own_window(self):
        """Öffnet die Hilfe in einem eigenständigen Tkinter-Fenster."""
        import threading

        def _build_text():
            lines = []
            sp = getattr(self, 'spielfeld', None)
            settings = getattr(sp, 'settings', {}) or {}
            hints = settings.get('hints', {}) or {}
            hints_text = hints.get('text', []) or []
            hints_code = hints.get('code', []) or []
            methoden_filter = hints.get('methoden')
            allowed = set(methoden_filter) if methoden_filter else None

            if hints_text:
                lines.append("── Tipps ──────────────────────────────")
                for t in hints_text:
                    lines.append(f"  • {t}")
                lines.append("")

            if hints_code:
                lines.append("── Beispielcode ────────────────────────")
                for c in hints_code:
                    lines.append(f"    {c}")
                lines.append("")

            def fmt_methoden(methoden):
                for method, params, desc in methoden:
                    if allowed and method.rstrip('()') not in allowed and method not in allowed:
                        continue
                    lines.append(f"  {method}")
                    if params and params != "–":
                        lines.append(f"      Parameter: {params}")
                    lines.append(f"      {desc}")

            try:
                _lnr = int(''.join(filter(str.isdigit, getattr(self, 'levelfile', '') or '')))
            except (ValueError, TypeError):
                _lnr = 0

            # Implementierungs-Modus für Level 35–58
            _impl_klassen_txt = {}
            if 35 <= _lnr <= 58:
                cr = (getattr(sp, 'settings', {}) or {}).get('class_requirements', {})
                if cr:
                    for _cls, _req in cr.items():
                        _impl_klassen_txt[_cls] = _req.get('methods', [])

            if _impl_klassen_txt:
                for cls_name, req_methods in _impl_klassen_txt.items():
                    lines.append(f"── {cls_name} – zu implementieren ──────────")
                    fmt_methoden(self._get_impl_methoden(cls_name, req_methods))
                    lines.append("")
            else:
                lines.append("── Held – Methoden ─────────────────────")
                fmt_methoden(self._get_held_methoden())
                lines.append("")

                has_knappe = False
                has_monster = False
                try:
                    tiles_flat = [c for row in sp.level.tiles for c in row]
                    has_knappe  = any(c.lower() == 'k' for c in tiles_flat if isinstance(c, str))
                    has_monster = any(c.lower() in ('x', 'y') for c in tiles_flat if isinstance(c, str))
                except Exception:
                    pass

                if has_knappe or getattr(sp, 'knappe', None) is not None:
                    lines.append("── Knappe – Methoden ───────────────────")
                    fmt_methoden(self._get_knappe_methoden())
                    lines.append("")

                if has_monster:
                    lines.append("── Monster – Methoden ──────────────────")
                    fmt_methoden(self._get_monster_methoden())
                    lines.append("")

                has_zettel_txt      = False
                has_tuer_spruch_txt = False
                has_tuer_farbig_txt = False
                has_schluessel_txt  = False
                try:
                    _ZETTEL_TYPEN = ('Zettel', 'Code', 'Spruch')
                    has_zettel_txt = any(
                        getattr(o, 'typ', '') in _ZETTEL_TYPEN
                        or type(o).__name__ in ('Code', 'Zettel')
                        for o in getattr(sp, 'objekte', []))
                    for _o in getattr(sp, 'objekte', []):
                        if getattr(_o, 'typ', '') == 'Tuer':
                            if getattr(_o, 'farbe', None) is not None:
                                has_tuer_farbig_txt = True
                            else:
                                has_tuer_spruch_txt = True
                        if getattr(_o, 'typ', '') == 'Schluessel':
                            has_schluessel_txt = True
                except Exception:
                    pass

                if has_zettel_txt:
                    lines.append("── Zettel – Methoden ───────────────────")
                    fmt_methoden(self._get_zettel_methoden())
                    lines.append("")

                if has_tuer_spruch_txt:
                    lines.append("── Tür – Methoden ──────────────────────")
                    fmt_methoden(self._get_tuer_methoden())
                    lines.append("")

                if has_tuer_farbig_txt:
                    lines.append("── Tür (farbig) – Methoden ─────────────")
                    fmt_methoden(self._get_tuer_farbig_methoden())
                    lines.append("")

                if has_schluessel_txt:
                    lines.append("── Schlüssel – Methoden ────────────────")
                    fmt_methoden(self._get_schluessel_methoden())
                    lines.append("")

                if bool(hints.get('konstruktoren_tab', False)) or (32 <= _lnr <= 34):
                    lines.append("── Konstruktoren ────────────────────────")
                    for klasse, sig, hinweis in self._get_konstruktoren():
                        lines.append(f"  {klasse}({sig})")
                        for part in hinweis.split('\n'):
                            lines.append(f"      {part}")
                    lines.append("")

            return "\n".join(lines)

        def _run():
            import tkinter as _tk
            from tkinter import scrolledtext as _st
            root = _tk.Tk()
            root.title("OOPventure – Hilfe")
            root.geometry("720x540")
            root.configure(bg="#12141e")

            txt = _st.ScrolledText(root, wrap=_tk.WORD, font=("Consolas", 12),
                                   bg="#12141e", fg="#d8dced",
                                   insertbackground="white", relief="flat",
                                   padx=10, pady=8)
            txt.pack(fill="both", expand=True)
            txt.insert("end", _build_text())
            txt.configure(state="disabled")
            root.mainloop()

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def _render_tastatur_uebersicht(self, surf, fonts, colors, x, y, w):
        """Rendert eine Tastaturübersicht anstelle der Methoden-Tabelle (für Level 0)."""
        KEYS = [
            # (Taste, Beschreibung)
            ("↑",          "Vorwärts gehen (in Blickrichtung)"),
            ("↓",          "Umdrehen (180°)"),
            ("←",          "90° nach links drehen"),
            ("→",          "90° nach rechts drehen"),
            ("Enter",      "Gegenstand / Herz aufnehmen"),
            ("Leertaste",  "Angreifen"),
            ("C",          "Zettel lesen (Spruch / Code anzeigen)"),
            ("V",          "Spruch / Code eingeben oder anwenden"),
            ("F",          "Tor oder Tür bedienen"),
            ("F1",         "Dieses Hilfefenster öffnen / schließen"),
            ("ESC",        "Spiel beenden"),
        ]
        PAD = 4
        COL1 = 110
        body   = fonts['body']
        header = fonts['header']
        lh     = body.get_linesize()

        # Tabellenheader
        pygame.draw.rect(surf, colors['header_bg'], (x, y, w, lh + PAD * 2))
        surf.blit(header.render("Taste",        True, colors['header_text']), (x + 4,        y + PAD))
        surf.blit(header.render("Aktion",       True, colors['header_text']), (x + COL1 + 4, y + PAD))
        y += lh + PAD * 2 + 2

        for i, (key, desc) in enumerate(KEYS):
            row_h = lh + PAD * 2
            pygame.draw.rect(surf, colors['row_even'] if i % 2 == 0 else colors['row_odd'], (x, y, w, row_h))
            pygame.draw.line(surf, colors['sep'], (x + COL1, y), (x + COL1, y + row_h))
            surf.blit(body.render(key,  True, colors['col_method']), (x + 4,        y + PAD))
            surf.blit(body.render(desc, True, colors['col_desc']),   (x + COL1 + 4, y + PAD))
            y += row_h

        return y + 8

    def _zeichne_hilfe(self):
        """F1-Hilfsfenster: zeigt verfügbare Befehle mit Tab-Navigation."""
        try:
            screen = self.screen
            sw, sh = screen.get_size()

            sp = getattr(self, 'spielfeld', None)
            level_hints = (getattr(sp, 'settings', {}) or {}).get('hints', {}) or {}
            no_monster_tab       = bool(level_hints.get('no_monster_tab', False))
            no_zettel_tab        = bool(level_hints.get('no_zettel_tab',  False))
            no_tuer_tab          = bool(level_hints.get('no_tuer_tab',    False))
            held_keyboard_mode   = bool(level_hints.get('held_keyboard_overview', False))
            default_tab          = level_hints.get('default_tab', None)  # None = use stored tab

            has_knappe  = False
            has_monster = False
            if sp:
                try:
                    tiles_flat = [c for row in sp.level.tiles for c in row]
                    has_knappe  = any(c.lower() == 'k'           for c in tiles_flat if isinstance(c, str))
                    has_monster = any(c.lower() in ('x', 'y')    for c in tiles_flat if isinstance(c, str))
                except Exception:
                    pass
                if not has_knappe and getattr(sp, 'knappe', None) is not None:
                    has_knappe = True
                if not has_monster:
                    has_monster = any(getattr(o, 'typ', '') in ('Monster', 'Bogenschuetze')
                                      for o in getattr(sp, 'objekte', []))

            # Level-Nummer (wird für Impl-Modus und Konstruktoren benötigt)
            try:
                _level_nr = int(''.join(filter(str.isdigit, getattr(self, 'levelfile', '') or '')))
            except (ValueError, TypeError):
                _level_nr = 0

            # Implementierungs-Modus für Level 35–58: Tabs aus class_requirements
            _impl_mode = 35 <= _level_nr <= 58
            _impl_klassen = {}  # class_name → required_methods list
            if _impl_mode:
                cr = (getattr(sp, 'settings', {}) or {}).get('class_requirements', {})
                if cr:
                    for _cls, _req in cr.items():
                        _impl_klassen[_cls] = _req.get('methods', [])

            if _impl_mode and _impl_klassen:
                tabs = ["Generelle Hilfe"] + list(_impl_klassen.keys())
            else:
                has_zettel      = False
                has_tuer_spruch = False
                has_tuer_farbig = False
                has_schluessel  = False
                if sp:
                    try:
                        _ZETTEL_TYPEN = ('Zettel', 'Code', 'Spruch')
                        has_zettel = any(
                            getattr(o, 'typ', '') in _ZETTEL_TYPEN
                            or type(o).__name__ in ('Code', 'Zettel')
                            for o in getattr(sp, 'objekte', []))
                        for _o in getattr(sp, 'objekte', []):
                            if getattr(_o, 'typ', '') == 'Tuer':
                                if getattr(_o, 'farbe', None) is not None:
                                    has_tuer_farbig = True
                                else:
                                    has_tuer_spruch = True
                            if getattr(_o, 'typ', '') == 'Schluessel':
                                has_schluessel = True
                    except Exception:
                        pass

                if no_monster_tab:
                    has_monster = False
                if no_zettel_tab:
                    has_zettel = False
                if no_tuer_tab:
                    has_tuer_spruch = False
                    has_tuer_farbig = False
                    has_schluessel  = False

                self._help_tuer_farbig = has_tuer_farbig
                has_tuer = has_tuer_spruch or has_tuer_farbig

                tabs = ["Generelle Hilfe", "Held"]
                if has_knappe:     tabs.append("Knappe")
                if has_monster:    tabs.append("Monster")
                if has_zettel:     tabs.append("Zettel")
                if has_tuer:       tabs.append("Tür")
                if has_schluessel: tabs.append("Schlüssel")

                show_konstruktoren = (
                    bool(level_hints.get('konstruktoren_tab', False))
                    or (32 <= _level_nr <= 34)
                )
                if show_konstruktoren:
                    tabs.append("Konstruktoren")

            # default_tab from hints: only apply once when the window is first opened
            _stored_tab = getattr(self, '_help_tab', None)
            if default_tab is not None and getattr(self, '_help_just_opened', False):
                tab = max(0, min(default_tab, len(tabs) - 1))
                self._help_just_opened = False
            else:
                tab = max(0, min(_stored_tab if _stored_tab is not None else 1, len(tabs) - 1))
            self._help_tab = tab

            W  = min(sw - 40, 880)
            H  = min(sh - 40, 580)
            px = (sw - W) // 2
            py = (sh - H) // 2

            C = {
                'bg':           (18,  20,  35),
                'border':       (70,  95, 160),
                'tab_active':   (45,  65, 125),
                'tab_inactive': (22,  26,  50),
                'tab_text_on':  (220, 232, 255),
                'tab_text_off': (130, 145, 185),
                'header_bg':    (32,  38,  65),
                'header_text':  (195, 210, 245),
                'row_even':     (28,  30,  50),
                'row_odd':      (20,  22,  42),
                'col_method':   (110, 195, 255),
                'col_param':    (170, 215, 150),
                'col_desc':     (215, 215, 205),
                'sep':          (55,  62, 100),
                'hint_text':    (195, 215, 200),
                'code_bg':      (22,  28,  48),
            }
            fonts = {
                'tab':        pygame.font.SysFont("consolas", 15, bold=True),
                'header':     pygame.font.SysFont("consolas", 14, bold=True),
                'body':       pygame.font.SysFont("consolas", 13),
                'hint_title': pygame.font.SysFont("consolas", 15, bold=True),
                'hint_body':  pygame.font.SysFont("consolas", 14),
            }

            # Dimm-Overlay
            ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            screen.blit(ov, (0, 0))

            # Panel
            pygame.draw.rect(screen, C['bg'],     (px, py, W, H))
            pygame.draw.rect(screen, C['border'], (px, py, W, H), 2)

            # Titelzeile
            TITLE_H = 30
            pygame.draw.rect(screen, C['border'], (px, py, W, TITLE_H))
            screen.blit(fonts['tab'].render(
                "Hilfe  (F1 schließen  |  \u2190 \u2192 Tabs  |  Mausklick auf Tab)",
                True, (240, 245, 255)), (px + 10, py + 7))

            # "Eigenes Fenster"-Button (⧉) ganz rechts in der Titelzeile
            _btn_w, _btn_h = 28, 22
            _btn_x = px + W - _btn_w - 4
            _btn_y = py + (TITLE_H - _btn_h) // 2
            _btn_rect = pygame.Rect(_btn_x, _btn_y, _btn_w, _btn_h)
            self._help_detach_rect = _btn_rect
            pygame.draw.rect(screen, (55, 75, 140), _btn_rect, border_radius=3)
            pygame.draw.rect(screen, (120, 150, 220), _btn_rect, 1, border_radius=3)
            _btn_lbl = fonts['tab'].render("\u29c9", True, (220, 235, 255))
            screen.blit(_btn_lbl, (_btn_x + (_btn_w - _btn_lbl.get_width()) // 2,
                                   _btn_y + (_btn_h - _btn_lbl.get_height()) // 2))

            # Tabs
            TAB_H = 28
            tab_y = py + TITLE_H
            tab_w = min(160, W // len(tabs))
            self._help_tab_rects = []
            for i, name in enumerate(tabs):
                tx   = px + i * tab_w
                active = (i == tab)
                pygame.draw.rect(screen, C['tab_active'] if active else C['tab_inactive'], (tx, tab_y, tab_w, TAB_H))
                pygame.draw.rect(screen, C['border'], (tx, tab_y, tab_w, TAB_H), 1)
                label = fonts['tab'].render(name, True, C['tab_text_on'] if active else C['tab_text_off'])
                screen.blit(label, (tx + (tab_w - label.get_width()) // 2, tab_y + 5))
                self._help_tab_rects.append(pygame.Rect(tx, tab_y, tab_w, TAB_H))

            # Content-Bereich
            CY0  = tab_y + TAB_H + 6
            CX   = px + 10
            CW   = W - 20
            CH   = H - TITLE_H - TAB_H - 12
            scroll = max(0, getattr(self, '_help_scroll', 0))

            # Auf temporäre Surface rendern (ermöglicht Scrollen)
            render_h = max(CH, 2400)
            rs = pygame.Surface((CW, render_h))
            rs.fill(C['bg'])
            ry = 6
            # Methoden-Filter aus Level-Hints lesen
            methoden_filter = level_hints.get('methoden')  # None = zeige alle

            def _filter_methoden(methoden):
                if not methoden_filter:
                    return methoden
                allowed = set(methoden_filter)
                return [m for m in methoden if m[0].rstrip('()') in allowed or m[0] in allowed]

            if tab == 0:
                ry = self._render_hilfe_allgemein(rs, fonts, C, 0, ry, CW, sp)
            elif _impl_mode and tabs[tab] in _impl_klassen:
                ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW,
                    self._get_impl_methoden(tabs[tab], _impl_klassen[tabs[tab]]))
            elif tabs[tab] == "Held":
                if held_keyboard_mode:
                    ry = self._render_tastatur_uebersicht(rs, fonts, C, 0, ry, CW)
                else:
                    ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, _filter_methoden(self._get_held_methoden()))
            elif tabs[tab] == "Knappe":
                ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, _filter_methoden(self._get_knappe_methoden()))
            elif tabs[tab] == "Monster":
                ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, self._get_monster_methoden())
            elif tabs[tab] == "Zettel":
                ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, self._get_zettel_methoden())
            elif tabs[tab] == "Tür":
                if getattr(self, '_help_tuer_farbig', False):
                    ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, self._get_tuer_farbig_methoden())
                else:
                    ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, self._get_tuer_methoden())
            elif tabs[tab] == "Schlüssel":
                ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, self._get_schluessel_methoden())
            elif tabs[tab] == "Konstruktoren":
                ry = self._render_konstruktoren_tab(rs, fonts, C, 0, ry, CW)
            else:
                ry = self._render_methoden_tabelle(rs, fonts, C, 0, ry, CW, self._get_monster_methoden())

            max_scroll = max(0, ry + 10 - CH)
            scroll = min(scroll, max_scroll)
            self._help_scroll = scroll
            screen.blit(rs, (CX, CY0), (0, scroll, CW, CH))

            # Scrollbalken
            if max_scroll > 0:
                total_h = ry + 10
                bx = px + W - 11
                indicator_h = max(20, int(CH * CH / total_h))
                indicator_y = CY0 + int((CH - indicator_h) * scroll / max_scroll)
                pygame.draw.rect(screen, C['sep'],    (bx, CY0, 7, CH))
                pygame.draw.rect(screen, C['border'], (bx, indicator_y, 7, indicator_h))

        except Exception as e:
            try:
                self.screen.blit(self.font.render(f"Hilfe-Fehler: {e}", True, (255, 100, 100)), (40, 40))
            except Exception:
                pass

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
                    # Register the student Held object in inspector refs
                    try:
                        self._inspector_refs.add(id(held))
                        self._inspector_refs.add(id(stud))
                    except Exception:
                        pass
                    try:
                        # "Objektname: held" header
                        hdr = self.font.render("Objektname: held", True, (180, 180, 255))
                        self.screen.blit(hdr, (panel_x, y)); y += 20
                    except Exception:
                        pass
                    try:
                        # name only if student provided it
                        if hasattr(stud, 'name'):
                            name = getattr(stud, 'name')
                            hdr = self.font.render(f"Name: {name}", True, (255,255,255))
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
                            x_txt = self.font.render(f"x: {x_val}", True, (200,200,200))
                            self.screen.blit(x_txt, (panel_x, y)); y += 20
                        except AttributeError:
                            pass
                        
                        # Try to get and display y
                        try:
                            y_val = get_student_attr(stud, 'y')
                            y_txt = self.font.render(f"y: {y_val}", True, (200,200,200))
                            self.screen.blit(y_txt, (panel_x, y)); y += 20
                        except AttributeError:
                            pass
                        
                        # Try to get and display richtung
                        try:
                            r = get_student_attr(stud, 'richtung')
                            rdisp = dm.get(str(r), str(r))
                            r_txt = self.font.render(f"richtung: {rdisp}", True, (200,200,200))
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
                # Only draw the default-held block when there is no student object
                # (when we showed student-provided attributes above we must not
                # repeat the generic Held display -- this previously caused the
                # hero to appear twice in the inspector).
                if stud is None:
                    # Register held in inspector_refs (Phase 1 / non-MetaHeld case)
                    try:
                        self._inspector_refs.add(id(held))
                    except Exception:
                        pass
                    try:
                        # "Objektname: held" header
                        hdr = self.font.render("Objektname: held", True, (180, 180, 255))
                        self.screen.blit(hdr, (panel_x, y)); y += 20
                    except Exception:
                        pass
                    try:
                        # use requested default name if not set
                        name = getattr(held, 'name', None) or 'namenloser held'
                        hdr = self.font.render(f"Name: {name}", True, (255,255,255))
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
                        x_txt = self.font.render(f"x: {x}", True, (200,200,200))
                        self.screen.blit(x_txt, (panel_x, y)); y += 20
                        y_txt = self.font.render(f"y: {yv}", True, (200,200,200))
                        self.screen.blit(y_txt, (panel_x, y)); y += 20
                        r_txt = self.font.render(f"richtung: {rdisp}", True, (200,200,200))
                        self.screen.blit(r_txt, (panel_x, y)); y += 20
                    except Exception:
                        pass
                    # After showing richtung, draw Held-Inventar (if any) below it
                    try:
                        inv = getattr(held, 'rucksack', None) or getattr(held, 'inventar', None)
                        if inv:
                            item_x = panel_x
                            item_y = y
                            icon_size = 24
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

            # Is Phase 2 (classes_present_mode) active?
            try:
                classes_present = bool(getattr(sp, 'classes_present_mode', False))
            except Exception:
                classes_present = False

            # Separator after Held (drawn here so it always appears after all Held content)
            draw_sep(y); y += 12

            # Draw Knappe (if present) as a distinct block after Held.
            # In classes_present_mode only shown after the student obtained a reference.
            kn = getattr(sp, 'knappe', None)
            show_knappe = (kn is not None) and (id(kn) in getattr(self, '_inspector_refs', set()))
            if show_knappe:
                try:
                    # "Objektname: <varname>" header
                    kn_varname = getattr(self, '_inspector_ref_names', {}).get(id(kn), getattr(kn, 'typ', 'Knappe'))
                    hdr = self.font.render(f"Objektname: {kn_varname}", True, (180, 255, 180))
                    self.screen.blit(hdr, (panel_x, y)); y += 20
                except Exception:
                    pass
                try:
                    name = getattr(kn, 'name', None) or 'namenloser knappe'
                    hdr = self.font.render(f"Name: {name}", True, (255,255,255))
                    self.screen.blit(hdr, (panel_x, y)); y += 20
                except Exception:
                    pass
                try:
                    x = getattr(kn, 'x', 0)
                    yv = getattr(kn, 'y', 0)
                    richt = getattr(kn, 'richtung', '?')
                    dm = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                    rdisp = dm.get(str(richt), str(richt))
                    x_txt = self.font.render(f"x: {x}", True, (200,200,200))
                    self.screen.blit(x_txt, (panel_x, y)); y += 20
                    y_txt = self.font.render(f"y: {yv}", True, (200,200,200))
                    self.screen.blit(y_txt, (panel_x, y)); y += 20
                    r_txt = self.font.render(f"richtung: {rdisp}", True, (200,200,200))
                    self.screen.blit(r_txt, (panel_x, y)); y += 20
                except Exception:
                    pass
                
                # Render Knappe's inventory if present (rucksack attribute)
                try:
                    inv = getattr(kn, 'rucksack', None) or getattr(kn, 'inventar', None)
                    if inv and hasattr(inv, 'items'):
                        item_x = panel_x
                        item_y = y
                        icon_size = 24
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
                draw_sep(y); y += 12

            # Monsters: render each with a separator between.
            # Only shown when the student has a reference (sichtbar=True at spawn,
            # or obtained via gib_knappe() / gib_objekt_vor_dir()).
            monsters = [o for o in self.spielfeld.objekte if getattr(o, 'typ', None) in ('Monster', 'Bogenschuetze')]
            for m in monsters:
                if id(m) not in getattr(self, '_inspector_refs', set()):
                    continue
                try:
                    # "Objektname: <varname>" header
                    m_varname = getattr(self, '_inspector_ref_names', {}).get(id(m), getattr(m, 'typ', 'Monster'))
                    hdr = self.font.render(f"Objektname: {m_varname}", True, (255, 180, 180))
                    self.screen.blit(hdr, (panel_x, y)); y += 20
                except Exception:
                    pass
                try:
                    name = getattr(m, 'name', None) or 'Monster'
                    hdr = self.font.render(f"Name: {name}", True, (255,255,255))
                    self.screen.blit(hdr, (panel_x, y)); y += 20
                except Exception:
                    pass
                try:
                    dm_map = {'up': 'N', 'down': 'S', 'left': 'W', 'right': 'O', 'N': 'N', 'S': 'S', 'W': 'W', 'O': 'O'}
                    mx = getattr(m, 'x', '?')
                    my = getattr(m, 'y', '?')
                    mr = dm_map.get(str(getattr(m, 'richtung', '?')), str(getattr(m, 'richtung', '?')))
                    self.screen.blit(self.font.render(f"x: {mx}", True, (200,200,200)), (panel_x, y)); y += 20
                    self.screen.blit(self.font.render(f"y: {my}", True, (200,200,200)), (panel_x, y)); y += 20
                    self.screen.blit(self.font.render(f"richtung: {mr}", True, (200,200,200)), (panel_x, y)); y += 20
                except Exception:
                    pass
                # separator between monsters
                draw_sep(y); y += 12

            # Finally render remaining objects (excluding Held, Knappe, Monsters, and items)
            # Items to exclude: Zettel, Herz, Tuer, Tor, Schluessel, Hindernis, etc.
            excluded_types = ['Monster', 'Bogenschuetze', 'Zettel', 'Herz', 'Tuer', 'Tor', 'Schluessel', 'Baum', 'Berg', 'Busch', 'Hindernis', 'Spruch', '?']
            remaining = [o for o in self.spielfeld.objekte 
                        if o not in ([held] if held else []) 
                        and o is not kn 
                        and getattr(o,'typ',None) not in excluded_types]
            for o in remaining:
                # In classes_present_mode only show if student has a reference
                if classes_present and id(o) not in getattr(self, '_inspector_refs', set()):
                    continue
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
        self._ensure_inspector_panel()
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
        if getattr(self, '_help_visible', False):
            self._zeichne_hilfe()

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
                    # F1: Hilfsfenster ein-/ausblenden
                    if event.key == pygame.K_F1:
                        if not getattr(self, '_help_visible', False):
                            self._help_visible = True
                            self._help_scroll = 0
                            self._help_just_opened = True
                            self._ensure_help_window_size()
                        else:
                            self._help_visible = False
                            self._restore_help_window_size()
                        continue
                    # Navigation im Hilfsfenster (falls sichtbar)
                    if getattr(self, '_help_visible', False):
                        _tab     = getattr(self, '_help_tab', 1)
                        _n_tabs  = max(1, len(getattr(self, '_help_tab_rects', [None, None])))
                        if event.key == pygame.K_LEFT:
                            self._help_tab   = max(0, _tab - 1)
                            self._help_scroll = 0
                        elif event.key == pygame.K_RIGHT:
                            self._help_tab   = min(_n_tabs - 1, _tab + 1)
                            self._help_scroll = 0
                        elif event.key == pygame.K_ESCAPE:
                            self._help_visible = False
                            self._restore_help_window_size()
                        continue
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
                    if getattr(self, '_help_visible', False):
                        self._help_scroll = max(0, getattr(self, '_help_scroll', 0) - event.y * 20)
                    else:
                        self.info_scroll += event.y * 20
                        if self.info_scroll < 0:
                            self.info_scroll = 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if getattr(self, '_help_visible', False) and event.button == 1:
                        mx, my = event.pos
                        # Detach-Button: Hilfe in eigenem Fenster öffnen
                        _detach = getattr(self, '_help_detach_rect', None)
                        if _detach and _detach.collidepoint(mx, my):
                            self._open_help_in_own_window()
                            continue
                        for i, rect in enumerate(getattr(self, '_help_tab_rects', [])):
                            if rect.collidepoint(mx, my):
                                self._help_tab    = i
                                self._help_scroll = 0
                                break
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

