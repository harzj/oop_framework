# framework/tuer.py
from .objekt import Objekt
from .utils import lade_sprite

class Tuer(Objekt):
    """Eine verschlossene Tür.
    Kann entweder per Code (Spruch) geöffnet werden oder per farbigem Schlüssel.
    Wenn color gesetzt ist, erwartet die Tür einen Schlüssel dieser Farbe (z.B. 'green','golden').
    """
    def __init__(self, x, y, code=None, color=None, sprite_pfad=None):
        # Wenn color gesetzt, nutze das farbige locked_door Sprite, sonst Standard
        if sprite_pfad is None:
            if color:
                sprite_pfad = f"sprites/locked_door_{color}.png"
            else:
                sprite_pfad = "sprites/tuer.png"
        super().__init__("Tür", x, y, "down", sprite_pfad)
        self._richtiger_code = code
        self.key_color = color
        self.offen = False

    def code_eingeben(self, code):
        """Öffnet die Tür, wenn der Code stimmt."""
        if str(code) == str(self._richtiger_code):
            if self.offen:
                print("[Tür] War bereits offen")
                return True
            #print("[Tür] Richtiger Code – Tür öffnet sich.")
            self.offen = True
            self.bild = lade_sprite("sprites/tuer_offen.png")
            """
            if self.framework:
                self.framework.spielfeld.entferne_objekt(self)
            return True
            """
            self.bild = lade_sprite("sprites/tuer_offen.png")
            return True
        else:
            if code != None:
                print("[Tür] Falscher Spruch!")
            return False
        
    def spruch_anwenden(self,code):
        self.code_eingeben(code)
    def schluessel_einsetzen(self, schluessel):
        """Versuche die Tür mit einem Schlüssel-Objekt zu öffnen.
        schluessel kann ein Objekt mit .color / .key_color Attribut sein.
        """
        if schluessel is None:
            return False
        color = getattr(schluessel, "color", None) or getattr(schluessel, "key_color", None)
        if color and self.key_color and color == self.key_color:
            self.offen = True
            # lade offenes Sprite falls vorhanden
            try:
                self.bild = lade_sprite("sprites/tuer_offen.png")
            except Exception:
                pass
            return True
        return False
        
    def ist_passierbar(self):
        return not self.offen
    
    def update(self):
        # Sprite abhängig vom Zustand der Tür wechseln
        if getattr(self, "offen", False):
            self.bild = lade_sprite("sprites/tuer_offen.png")
        else:
            # falls farbige Tür, stelle sicher, dass das correct locked sprite geladen ist
            if getattr(self, "key_color", None):
                try:
                    self.bild = lade_sprite(f"sprites/locked_door_{self.key_color}.png")
                except Exception:
                    pass

        # das Sprite neu laden (wenn du das schon irgendwo zentral machst, diesen Teil ggf. dort einfügen)
        try:
            self._bild_surface = self._lade_sprite(self._bild)
        except Exception:
            pass


