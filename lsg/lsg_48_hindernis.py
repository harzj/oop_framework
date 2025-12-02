# Musterlösung Level 48: Hindernis erbt von Spielobjekt

from lsg.lsg_48_spielobjekt import Spielobjekt

class Hindernis(Spielobjekt):
    def __init__(self, x, y, art):
        super().__init__(x, y)
        # Set typ to art (Baum, Berg, Busch)
        self._Spielobjekt__typ = art
    
    def get_typ(self):
        return self._Spielobjekt__typ
    
    def get_x(self):
        return self._Spielobjekt__x
    
    def get_y(self):
        return self._Spielobjekt__y
    
    def ist_passierbar(self):
        return False
