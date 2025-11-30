
# Variante: get_x und get_y vorhanden, aber get_typ fehlt
# Sollte als Fragezeichen gerendert werden
class Hindernis():
    def __init__(self, x, y, art):
        self.__typ = art  # möglich sind Baum, Berg, Busch
        self.__x = x
        self.__y = y

    def ist_passierbar(self):
        return False
    
    # get_typ fehlt absichtlich!
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
    
    def set_position(self, x, y):
        self.__x = x
        self.__y = y
