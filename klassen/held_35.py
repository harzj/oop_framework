# Held-Klasse für Level 35-37 (ohne Charakter-Vererbung)
class Held:
    """Student implementation of Held class for basic levels."""
    
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"
