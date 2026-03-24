from framework.grundlage import level
level.lade(35,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
class Held:
    def __init__(self,x,y,richtung,weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Bernd"
        self.typ = "Held"

# Dieser Befehl muss immer am Ende stehen
framework.starten()

