
# Musterlösung Level 48: Hindernis erbt von Spielobjekt
from spielobjekt import *

class Hindernis(Spielobjekt):
    def __init__(self, x, y, art):
        super().__init__(x, y)
        self._Spielobjekt__typ = art
    

