
# Korrekte Implementierung mit privaten Attributen
class Spielobjekt:
    def __init__(self, x, y):
        self.typ = "Spielobjekt"
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
