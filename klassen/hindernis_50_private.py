
# Hindernis mit eigenen privaten Attributen (sollte bei Level 50 fehlschlagen)
from spielobjekt import *

class Hindernis(Spielobjekt):
    def __init__(self, x, y, art):
        super().__init__(x, y)
        self.__typ = art  # Private attribute in Hindernis
        self.__x = x      # Override parent's public x with private
        self.__y = y      # Override parent's public y with private
    
    def get_typ(self):
        return self.__typ
    
    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
