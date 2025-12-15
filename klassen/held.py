# Musterlösung Level 57: Held mit Inventar
from charakter import Charakter
from inventar import Inventar
from gegenstand import Gegenstand

class Held(Charakter):
    def __init__(self, x, y, richtung, weiblich):
        super().__init__(x, y, richtung)
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
        # Komposition: Held hat ein Inventar
        self.rucksack = Inventar()
        # Held startet mit einem Schwert
        schwert = Gegenstand("Schwert")
        self.rucksack.item_hinzufuegen(schwert)
        
    def get_weiblich(self):
        return self.weiblich
