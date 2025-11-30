
# Falsch: Private Attribute aber fehlende Getter
class Hindernis():
    def __init__(self, x, y, art):
        self.__typ = art  # möglich sind Baum, Berg, Busch
        self.__x = x
        self.__y = y

    def ist_passierbar(self):
        return False
    
    # get_typ fehlt!
    # get_x fehlt!
    # get_y fehlt!
    
    def set_position(self, x, y):
        self.__x = x
        self.__y = y
