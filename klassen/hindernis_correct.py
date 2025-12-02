
# Korrekte Implementierung mit privaten Attributen
class Hindernis:
    def __init__(self, x, y, art):
        self.__typ = art  # möglich sind Baum, Berg, Busch
        self.__x = x
        self.__y = y
    
    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
