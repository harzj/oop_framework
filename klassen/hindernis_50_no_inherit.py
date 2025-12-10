
# Hindernis ohne Vererbung von Spielobjekt (sollte fehlschlagen)
class Hindernis:
    def __init__(self, x, y, art):
        self.typ = art
        self.x = x
        self.y = y
    
    def get_typ(self):
        return self.typ
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def ist_passierbar(self):
        return False
