
# Zettel ohne Vererbung von Spielobjekt (sollte fehlschlagen)
class Zettel:
    def __init__(self, x, y):
        self.typ = "Zettel"
        self.x = x
        self.y = y
        self.spruch = "Sesam öffne dich"

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
    
    def ist_passierbar(self):
        return True
