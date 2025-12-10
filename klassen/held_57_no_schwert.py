# FEHLER: Held ohne Schwert im Inventar
from charakter import Charakter
from inventar import Inventar
from gegenstand import Gegenstand

class Held(Charakter):
    def __init__(self, x, y, richtung, weiblich):
        super().__init__(x, y, richtung)
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
        # FEHLER: Inventar ist leer, kein Schwert!
        self.rucksack = Inventar()
        
    def get_weiblich(self):
        return self.weiblich
