"""
Test hindernis_48.py with BROKEN get_typ() - should fail victory
"""
from spielobjekt import Spielobjekt

class Hindernis(Spielobjekt):
    def __init__(self, x, y, art):
        super().__init__(x, y)
        self._Spielobjekt__typ = art
    
    def ist_passierbar(self):
        return False
    
    def get_typ(self):
        # BROKEN: Returns wrong value
        return "FALSCH"
