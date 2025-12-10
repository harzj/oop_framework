
# Hindernis ohne x-Attribut (sollte bei Level 50 fehlschlagen)
from spielobjekt import *

class Hindernis(Spielobjekt):
    def __init__(self, art, y):  # FEHLER: x fehlt als Parameter
        # super().__init__ wird absichtlich NICHT aufgerufen
        # self.x fehlt!
        self.y = y
        self.typ = art
    
    def ist_passierbar(self):
        return False
    
    def get_x(self):
        # Getter existiert, aber x-Attribut fehlt!
        return 0  # Fake-Wert
    
    def get_y(self):
        return self.y
    
    def get_typ(self):
        return self.typ
