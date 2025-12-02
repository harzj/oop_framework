
# Korrekte Lösung für Level 40: Private Attribute
class Held:
    def __init__(self, x, y, richtung, weiblich):
        self.__x = x
        self.__y = y
        self.__richtung = richtung
        self.__weiblich = weiblich
        self.name = "Namenloser Held"
        self.__typ = "Held"
