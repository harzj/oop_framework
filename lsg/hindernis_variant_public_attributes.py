
# Falsch: Alle Attribute öffentlich (kein __ Präfix)
class Hindernis():
    def __init__(self, x, y, art):
        self.typ = art  # möglich sind Baum, Berg, Busch
        self.x = x
        self.y = y

    def ist_passierbar(self):
        return False
    
    def get_typ(self):
        return self.typ
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
