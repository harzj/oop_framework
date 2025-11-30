
# Test: Nur x,y vorhanden (sollte gerendert werden, aber Level nicht abgeschlossen)
class Zettel():
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def get_x(self):
        return self.__x
    
    def get_y(self):
        return self.__y
