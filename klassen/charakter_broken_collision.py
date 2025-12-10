from spielobjekt import Spielobjekt

class Charakter(Spielobjekt):
    """Charakter OHNE korrekte Kollisionserkennung - für Fehlertest"""
    def __init__(self, x, y, richtung):
        super().__init__(x, y)
        self.richtung = richtung
        self.name = "Charakter ohne Kollision"
        self.typ = "Charakter"
        self.level_objekte = []
    
    def set_level(self, objekte):
        """Speichert Referenz zu Level-Objekten"""
        self.level_objekte = objekte
    
    def set_level(self, level):
        """Speichert Referenz zu Level-Objekten"""
        self.level_objekte = level
    
    def geh(self):
        """Bewegt sich OHNE Kollisionserkennung - FEHLER!"""
        # Bewegt sich einfach blind, ohne Hindernisse zu prüfen
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
        return self.name
    
    def set_richtung(self, value):
        if value in ["up", "down", "left", "right"]:
            self.richtung = value
