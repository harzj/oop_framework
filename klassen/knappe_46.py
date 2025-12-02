# Falsch: Alle Attribute öffentlich (kein __ Präfix)
class Knappe:
    def __init__(self, x, y, richtung):
        self.__x = x
        self.__y = y
        self.__richtung = richtung
        self.name = "Namenloser Knappe"
        self.typ = "Knappe"

    def set_richtung(self, neue_richtung):
        if neue_richtung in ["up", "down", "left", "right"]:
            self.__richtung = neue_richtung

    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def get_richtung(self):
        return self.__richtung
    
    def get_typ(self):
        return self.typ
    
    def geh(self):
        if self.__richtung == "up":
            self.__y -= 1
        elif self.__richtung == "down":
            self.__y += 1
        elif self.__richtung == "left":
            self.__x -= 1
        elif self.__richtung == "right":
            self.__x += 1
    
    def links(self):
        if self.__richtung == "up":
            self.__richtung = "left"
        elif self.__richtung == "down":
            self.__richtung = "right"
        elif self.__richtung == "left":
            self.__richtung = "down"
        elif self.__richtung == "right":
            self.__richtung = "up"
    
    def rechts(self):
        if self.__richtung == "up":
            self.__richtung = "right"
        elif self.__richtung == "down":
            self.__richtung = "left"
        elif self.__richtung == "left":
            self.__richtung = "up"
        elif self.__richtung == "right":
            self.__richtung = "down"


