
# Fehlerhafte Implementierung: Öffentliche Attribute (soll fehlschlagen)
class Zettel():
    def __init__(self, x, y):
        self.typ = "Zettel"  # Sollte privat sein!
        self.x = x           # Sollte privat sein!
        self.y = y           # Sollte privat sein!
        self.spruch = "Sesam öffne dich"  # Sollte privat sein!

    def ist_passierbar(self):
        return True
    
    def get_typ(self):
        return self.typ
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_spruch(self):
        return self.spruch
    
    def set_spruch(self, spruch):
        self.spruch = spruch
