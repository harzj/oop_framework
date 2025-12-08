from spielobjekt import Spielobjekt

# FAIL: Öffentliche Attribute statt private
class Zettel(Spielobjekt):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.typ = "Zettel"  # FALSCH: sollte _Spielobjekt__typ sein
        self.spruch = "Sesam öffne dich"  # FALSCH: sollte __spruch sein
    
    def get_spruch(self):
        return self.spruch
    
    def set_spruch(self, spruch):
        self.spruch = spruch
