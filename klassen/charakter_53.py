from spielobjekt import Spielobjekt

class Charakter(Spielobjekt):
    def __init__(self, x, y, richtung):
        super().__init__(x,y)
        self.richtung = richtung
        self.name = "Namenloser Charakter"
        self.typ = "Charakter"
    
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
    
    def get_richtung(self):
        return self.richtung
    
    def get_name(self):
        return self.name  # name ist öffentlich
    
    def set_richtung(self, value):
        if value in ["up", "down", "left", "right"]:
            self.richtung = value
