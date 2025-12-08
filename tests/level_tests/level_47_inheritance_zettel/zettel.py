from spielobjekt import Spielobjekt

class Zettel(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)
        # Setze typ über Name Mangling (private Attribute von Elternklasse)
        self._Spielobjekt__typ = "Zettel"
        self.__spruch = "Sesam öffne dich"
    
    def get_spruch(self):
        return self.__spruch
    
    def set_spruch(self, spruch):
        self.__spruch = spruch
