# FEHLER: Knappe mit Items im Inventar
from charakter import Charakter
from inventar import Inventar
from gegenstand import Gegenstand

class Knappe(Charakter):
    def __init__(self, x, y, richtung):
        super().__init__(x, y, richtung)
        self.name = "Namenloser Knappe"
        self.typ = "Knappe"
        # FEHLER: Inventar sollte leer sein, enthält aber Items!
        self.rucksack = Inventar()
        item = Gegenstand("Brot")
        self.rucksack.item_hinzufuegen(item)
