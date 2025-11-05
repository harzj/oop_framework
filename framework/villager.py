# framework/villager.py
import pygame
from .objekt import Objekt


class Villager(Objekt):
    """Ein einfacher Dorfbewohner / Dorfbewohnerin.

    Minimalimplementierung: wählt Sprite basierend auf dem weiblich-Flag
    und bietet eine kleine Attributanzeige. Verwendet das Basisklasse-Verhalten
    für Bewegung und Zeichnen.
    """

    def __init__(self, framework, x=0, y=0, richtung="down",
                 sprite_pfad: str = None, name: str = "Nils",
                 steuerung_aktiv: bool = False, weiblich: bool = False):
        if weiblich:
            typ = "Dorfbewohnerin"
            sprite_pfad = sprite_pfad or "sprites/villager2.png"
        else:
            typ = "Dorfbewohner"
            sprite_pfad = sprite_pfad or "sprites/villager.png"

        super().__init__(typ=typ, x=x, y=y, richtung=richtung,
                         sprite_pfad=sprite_pfad, name=name)
        self.framework = framework
        self.steuerung_aktiv = steuerung_aktiv
        self.weiblich = weiblich
        self.ist_held = False

    def attribute_als_text(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "richtung": self.richtung,
            "weiblich": self.weiblich,
        }

