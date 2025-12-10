
# Falsch: Alle Attribute öffentlich (kein __ Präfix)
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"

    def set_richtung(self, neue_richtung):
        if neue_richtung in ["up", "down", "left", "right"]:
            self.richtung = neue_richtung

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_richtung(self):
        return self.richtung
    
    def get_weiblich(self):
        return self.weiblich
    
    def get_typ(self):
        return self.typ
    
    def geh(self):
        if self.richtung == "up":
            self.y -= 1
        elif self.richtung == "down":
            self.y += 1
        elif self.richtung == "left":
            self.x -= 1
        elif self.richtung == "right":
            self.x += 1
    
    def links(self):
        if self.richtung == "up":
            self.richtung = "left"
        elif self.richtung == "down":
            self.richtung = "right"
        elif self.richtung == "left":
            self.richtung = "down"
        elif self.richtung == "right":
            self.richtung = "up"
    
    def rechts(self):
        if self.richtung == "up":
            self.richtung = "right"
        elif self.richtung == "down":
            self.richtung = "left"
        elif self.richtung == "left":
            self.richtung = "up"
        elif self.richtung == "right":
            self.richtung = "down"


