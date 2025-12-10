from charakter import Charakter
from inventar import Inventar

class Knappe(Charakter):
    def __init__(self, x, y, richtung):
        super().__init__(x, y, richtung)
        self.name = "Namenloser Knappe"
        self.typ = "Knappe"  # Überschreibt typ von Charakter
        # Knappe hat ein leeres Inventar
        self.rucksack = Inventar()




