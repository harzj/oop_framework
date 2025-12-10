# Musterlösung Level 56: Inventar-Klasse
from framework.grundlage import level
level.lade(56, weiblich=True)
from framework.grundlage import *
# Ab hier darfst du programmieren:
# Level 56: Test für Inventar-Klasse

# Dieser Befehl muss immer am Ende stehen
framework.starten()
    
    def anzahl_items(self):
        return len(self.items) 
    
    def gib_item_nummer(self, nummer):
        try:
            return self.items[nummer]
        except IndexError:
            return None
        
    def gib_kapazitaet(self):
        return self.kapazitaet
    
    def gib_gold(self):
        return self.gold
    
    def gold_sammeln(self, menge):
        self.gold += menge

    def ist_voll(self):
        return len(self.items) >= self.kapazitaet
