
# FAIL: Öffentliche Attribute statt private (sollte fehlschlagen)
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.x = x  # Sollte __x sein
        self.y = y  # Sollte __y sein
        self.richtung = richtung  # Sollte __richtung sein
        self.weiblich = weiblich  # Sollte __weiblich sein
        self.name = "Test Held"
        self.typ = "Held"  # Sollte __typ sein
    
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
        if self.richtung == "up":
            self.richtung = "left"
        elif self.richtung == "down":
            self.richtung = "right"
        elif self.richtung == "left":
            self.richtung = "down"
        elif self.richtung == "right":
            self.richtung = "up"
    
    def rechts(self):
        if self.richtung == "up":
            self.richtung = "right"
        elif self.richtung == "down":
            self.richtung = "left"
        elif self.richtung == "left":
            self.richtung = "up"
        elif self.richtung == "right":
            self.richtung = "down"
