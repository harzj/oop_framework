
# Korrekte Implementierung mit privaten Attributen
class Zettel:
    def __init__(self, x, y):
        self.__typ = "Zettel"
        self.__x = x
        self.__y = y
        self.__spruch = "Sesam öffne dich"

    def ist_passierbar(self):
        return True
    
    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def get_spruch(self):
        return self.__spruch
    
    def set_spruch(self, spruch):
        self.__spruch = spruch
