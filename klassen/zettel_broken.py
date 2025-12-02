"""
Test zettel_49.py with BROKEN set_spruch() - should fail victory
"""
from spielobjekt import Spielobjekt

class Zettel(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._Spielobjekt__typ = "Zettel"
        self.__spruch = ""
    
    def get_spruch(self):
        return self.__spruch
    
    def set_spruch(self, text):
        # BROKEN: Doesn't actually set the value
        pass  # Does nothing!
