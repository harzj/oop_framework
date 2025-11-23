
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
    
    # Getter methods for private attributes
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def get_richtung(self):
        return self.__richtung
    
    def get_weiblich(self):
        return self.__weiblich
    
    def get_typ(self):
        return self.__typ
    
    # Setter methods for private attributes
    def set_x(self, value):
        self.__x = value
    
    def set_y(self, value):
        self.__y = value
    
    def set_richtung(self, value):
        self.__richtung = value