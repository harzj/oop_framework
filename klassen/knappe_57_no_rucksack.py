# FEHLER: Knappe ohne rucksack Attribut
from charakter import Charakter

class Knappe(Charakter):
    def __init__(self, x, y, richtung):
        super().__init__(x, y, richtung)
        self.name = "Namenloser Knappe"
        self.typ = "Knappe"
        # FEHLER: rucksack fehlt!
