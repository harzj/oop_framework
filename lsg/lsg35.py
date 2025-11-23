from framework.grundlage import level
level.lade(35, weiblich=False)
from framework.grundlage import *

# Ab hier darfst du programmieren:

# Lösung für Level 35: Held Klasse
class Held:
    """Student implementation of Held class for level35."""
    
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Namenloser Held"
        self.typ = "Held"

# Dieser Befehl muss immer am Ende stehen
framework.starten()
