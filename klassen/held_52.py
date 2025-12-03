from charakter import Charakter

class Held(Charakter):
    def __init__(self, x, y, richtung, weiblich):
        super().__init__(x, y, richtung)
        self.weiblich = weiblich  # Öffentlich ab Level 50!
        self.name = "Namenloser Held"
        self.typ = "Held"  # Auch öffentlich!
        
    def get_weiblich(self):
        return self.weiblich