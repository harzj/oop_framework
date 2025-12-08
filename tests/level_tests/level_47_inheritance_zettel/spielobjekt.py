
# Spielobjekt mit privaten Attributen (Level 47)
class Spielobjekt:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.__typ = "Spielobjekt"
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def get_typ(self):
        return self.__typ
