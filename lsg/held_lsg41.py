
# Korrekte Lösung für Level 41: Private Attribute + Getter
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.__x = x
        self.__y = y
        self.__richtung = richtung
        self.__weiblich = weiblich
        self.name = "Namenloser Held"
        self.__typ = "Held"

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
