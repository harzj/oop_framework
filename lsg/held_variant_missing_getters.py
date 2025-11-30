
# Falsch: Private Attribute aber keine Getter
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.__x = x
        self.__y = y
        self.__richtung = richtung
        self.__weiblich = weiblich
        self.name = "Test Held"
        self.__typ = "Held"
    
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
    
    # Keine Getter! - WRONG!
    # Keine Setter!
