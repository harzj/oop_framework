class Inventar:
    def __init__(self):
        self.items = []
        self.kapazitaet = 16
        self.gold = 0

    def item_hinzufuegen(self,item):
        if len(self.items) < self.kapazitaet:
            self.items.append(item)
            return True
        return False
    
    def hat_item(self,item):
        return item in self.items
    
    def anzahl_items(self):
        return len(self.items) 
    
    def gib_item_nummer(self,nummer):
        try:
            return self.items[nummer]
        except IndexError:
            return None
        
    def gib_kapazitaet(self):
        return self.kapazitaet
    
    def gib_gold(self):
        return self.gold
    
    def gold_sammeln(self,menge):
        self.gold += menge

    def ist_voll(self):
        return len(self.items) >= self.kapazitaet