from framework.grundlage import level
level.lade(36,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Test Held"
        self.typ = "Held"

    def geh(self):
        if self.richtung == "up":
            self.y -= 1
        elif self.richtung == "down":
            self.y += 1
        elif self.richtung == "left":
            self.x -= 1
        elif self.richtung == "right":
            self.x += 1
        
    def links(self):
        richtungen = ["up", "left", "down", "right"]
        idx = richtungen.index(self.richtung)
        self.richtung = richtungen[(idx + 1) % 4]

    def rechts(self):
        richtungen = ["up", "right", "down", "left"]
        idx = richtungen.index(self.richtung)
        self.richtung = richtungen[(idx + 1) % 4]


held.geh()
held.geh()
held.links()
held.geh()

# Dieser Befehl muss immer am Ende stehen
framework.starten()
