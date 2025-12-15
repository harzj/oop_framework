from spielobjekt import Spielobjekt

class Charakter(Spielobjekt):
    def __init__(self, x, y, richtung):
        super().__init__(x,y)
        self.richtung = richtung
        self.name = "Namenloser Charakter"
        self.typ = "Charakter"
        self.level = None
    
    def set_level(self,level):
        self.level = level
    
    def geh(self):
        if self.richtung == "up":
            ziel_y = self.y - 1
            ziel_x = self.x
        elif self.richtung == "down":
            ziel_y = self.y + 1
            ziel_x = self.x
        elif self.richtung == "left":
            ziel_x = self.x - 1
            ziel_y = self.y
        elif self.richtung == "right":
            ziel_x = self.x + 1
            ziel_y = self.y

        if not self.level.ist_innerhalb(ziel_x,ziel_y):
            return

        target = self.level.gib_objekt_bei(ziel_x, ziel_y)

        if target == None or target.ist_passierbar():
            self.x = ziel_x
            self.y = ziel_y
            
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
