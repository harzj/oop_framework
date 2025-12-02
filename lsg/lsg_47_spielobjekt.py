# Musterlösung Level 47: Spielobjekt (abstrakte Basisklasse) mit privaten Attributen

class Spielobjekt:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.__typ = None
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def get_typ(self):
        return self.__typ
    
    def ist_passierbar(self):
        return False
