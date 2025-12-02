# framework/held.py
import random
import pygame
from .objekt import Objekt

class Knappe(Objekt):
    def __init__(self, framework_or_x, x_or_y=0, y_or_richtung=0, richtung_or_sprite="down",
                 sprite_pfad="sprites/knappe.png", name=None,
                 steuerung_aktiv=False):
        """
        Flexible constructor supporting two signatures:
        
        Student signature (Level 341+):
            Knappe(x, y, richtung, ...)
            Example: Knappe(2, 2, "up")
        
        Framework signature (internal use):
            Knappe(framework, x, y, richtung, ...)
            Example: Knappe(fw, 2, 2, "up")
        
        Detection: If first arg is numeric, use student signature.
        """
        # Detect signature based on first parameter
        if isinstance(framework_or_x, (int, float)):
            # Student signature: Knappe(x, y, richtung, ...)
            x = int(framework_or_x)
            y = int(x_or_y)
            richtung = y_or_richtung if isinstance(y_or_richtung, str) else "down"
            framework = None
            # sprite_pfad might be passed via richtung_or_sprite if it's a string starting with "sprites/"
            if isinstance(richtung_or_sprite, str) and richtung_or_sprite.startswith("sprites/"):
                sprite_pfad = richtung_or_sprite
        else:
            # Framework signature: Knappe(framework, x, y, richtung, ...)
            framework = framework_or_x
            x = int(x_or_y)
            y = int(y_or_richtung) if isinstance(y_or_richtung, (int, float)) else 0
            richtung = richtung_or_sprite if isinstance(richtung_or_sprite, str) else "down"
        
        super().__init__(typ="Knappe", x=x, y=y, richtung=richtung,
                         sprite_pfad=sprite_pfad, name=name)
        self.framework = framework
        self.ist_held = True
        self.geheimer_code = None

        # If no explicit name was provided, try to generate one via the
        # Spielfeld helper so framework-created Knappes keep a random name.
        # Be robust: the 'framework' argument may be a Framework or a Spielfeld
        # (or be missing when instantiated by student code). If we can't find
        # the framework generator, pick a local random name as fallback.
        if name is None:
            got = None
            try:
                # If framework looks like a Framework with a spielfeld (only if framework exists)
                if framework is not None:
                    # spielfeld.generate_knappe_name preferred
                    sp = getattr(framework, 'spielfeld', None)
                    gen = None
                    if sp is not None:
                        gen = getattr(sp, 'generate_knappe_name', None)
                    # fallback: framework itself might expose generator
                    if gen is None:
                        gen = getattr(framework, 'generate_knappe_name', None)
                    if callable(gen):
                        got = gen()
                # if framework itself is a Spielfeld-like object
                if got is None and framework is not None and hasattr(framework, 'generate_knappe_name'):
                    gen = getattr(framework, 'generate_knappe_name')
                    if callable(gen):
                        got = gen()
            except Exception:
                got = None

            if got is None:
                # fallback: use integrated knappe name generator (rich name list)
                try:
                    self.name = self.generate_knappe_name()
                except Exception:
                    # very small fallback
                    try:
                        self.name = random.choice(["Nils", "Tobi", "Udo"])
                    except Exception:
                        self.name = "Nils"
            else:
                self.name = got

        if steuerung_aktiv and framework is not None:
            self.aktiviere_steuerung()




    def aktiviere_steuerung(self):
        if self.framework is None:
            return  # No framework available (student-created Knappe)
        self.framework.taste_registrieren(pygame.K_a,  lambda: self.links(0))
        self.framework.taste_registrieren(pygame.K_d, lambda: self.rechts(0))
        self.framework.taste_registrieren(pygame.K_w,    lambda: self.geh(0))
        self.framework.taste_registrieren(pygame.K_s,lambda: self.zurueck(0))
        """
        self.framework.taste_registrieren(pygame.K_SPACE, lambda: self.attack(0))
        self.framework.taste_registrieren(pygame.K_c, lambda: self.lese_code(0))
        self.framework.taste_registrieren(pygame.K_v, lambda: self.code_eingeben(0))
        self.framework.taste_registrieren(pygame.K_f, lambda: self.bediene_tor())


        """
    def lese_code(self,delay_ms=500):
        self.lese_spruch(delay_ms)
        
    def spruch_sagen(self, code=None, delay_ms=500):
        self.code_eingeben(code,delay_ms)

    def sage_spruch(self,code=None,delay_ms=500):
        self.spruch_sagen(code,delay_ms)
        
    def spruch_lesen(self, delay_ms=500):
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
            print(f"[Knappe] Spruch {self.geheimer_code} notiert.")
            if self.framework:
                self.framework.spielfeld.entferne_objekt(code_obj)
            return self.geheimer_code
        # Kein Spruch gefunden - ungültige Aktion
        if not getattr(self.framework, '_aus_tastatur', False):
            self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
        print("[Knappe] Kein Spruch hier.")
        self._render_and_delay(delay_ms)
        return None
    
    def bediene_tor(self,delay_ms=500):
        """Versucht, das Tor vor dem Helden zu öffnen oder zu schließen."""
        # Check if framework is blocked
        if getattr(self.framework, '_aktion_blockiert', False):
            return None
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
            print("[Knappe]: Kein Tor vor mir")
            return None
        self._render_and_delay(delay_ms)


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
            if tuer._eingeben(code):
                print("[Knappe] " + self.geheimer_code + "!")
            else:
                if self.geheimer_code == None:
                    print("[Knappe] Ich habe keinen Spruch...")
                    self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
                else:
                    self._ungueltige_aktion("Ungültige Aktion! Versuch es nochmal!")
        else:
            print("[Knappe] Keine Tür vor mir.")
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
        
    def transmute_richtung(self,r):
        if r=="down":
            return "S"
        elif r=="up":
            return "N"
        elif r=="left":
            return "W"
        else:
            return "O"

    @staticmethod
    def generate_knappe_name():
        import random
        names = [
            "Page Skywalker","Jon Snowflake","Sir Lancelame","Rick Rollins",
            "Ben of the Rings","Tony Stork","Bucky Stables","Frodolin Beutelfuss","Jamie Lameister","Gerold of Trivia",
            "Arthur Denton","Samwise the Slacker","Obi-Wan Knappobi","Barry Slow","Knight Fury","Grogulette",
            "Sir Bean of Gondor","Thorin Eichensohn","Legoless","Knappernick",
            "Knapptain Iglo","Ritterschorsch","Helm Mut","Sigi von Schwertlingen","Klaus der Kleingehauene","Egon Eisenfaust","Ben Knied","Rainer Zufallsson","Dietmar Degenhart","Uwe von Ungefähr","Hartmut Helmrich","Bodo Beinhart","Kai der Kurze","Knapphart Stahl","Tobi Taschenmesser","Fridolin Fehlschlag","Gernot Gnadenlos","Ralf Rüstungslos","Gustav Gürtelschwert","Kuno Knickbein"
        ]
        try:
            return random.choice(names).capitalize()
        except Exception:
            return "Knappe"