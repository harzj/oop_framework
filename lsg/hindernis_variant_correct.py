
# Korrekte Implementierung: Alle Attribute privat mit Gettern
class Hindernis():
    def __init__(self, x, y, art):
        self.__typ = art  # möglich sind Baum, Berg, Busch
        self.__x = x
        self.__y = y

    def ist_passierbar(self):
        return False
    
    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def set_position(self, x, y):
        self.__x = x
        self.__y = y
