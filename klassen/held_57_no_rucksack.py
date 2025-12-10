# FEHLER: Held ohne rucksack Attribut
from charakter import Charakter

class Held(Charakter):
    def __init__(self, x, y, richtung, weiblich):
        super().__init__(x, y, richtung)
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
        # FEHLER: rucksack fehlt!
        
    def get_weiblich(self):
        return self.weiblich
