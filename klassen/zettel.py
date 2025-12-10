
# Korrekte Implementierung mit privaten Attributen
from spielobjekt import *

class Zettel(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)  
        self._Spielobjekt__typ = "Zettel"
        self.__spruch = "Sesam öffne dich"

    def get_spruch(self):
        return self.__spruch
    
    def set_spruch(self, spruch):
        self.__spruch = spruch
