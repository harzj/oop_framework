
# Fehlerhafte Implementierung: Fehlende Getter (soll fehlschlagen)
class Zettel():
    def __init__(self, x, y):
        self.__typ = "Zettel"
        self.__x = x
        self.__y = y
        self.__spruch = "Sesam öffne dich"

    def ist_passierbar(self):
        return True
    
    # get_typ fehlt absichtlich!
    # get_x fehlt absichtlich!
    # get_y fehlt absichtlich!
    # get_spruch fehlt absichtlich!
    
    def set_spruch(self, spruch):
        self.__spruch = spruch
