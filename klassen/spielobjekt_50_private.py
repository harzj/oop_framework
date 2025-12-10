
# Spielobjekt mit privaten Attributen (sollte bei Level 50 fehlschlagen)
class Spielobjekt:
    def __init__(self, x, y):
        self.__typ = "Spielobjekt"
        self.__x = x
        self.__y = y

    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def ist_passierbar(self):
        return False
