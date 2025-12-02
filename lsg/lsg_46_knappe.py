"""
Musterlösung für Level 46: Knappe Klasse

Diese Klasse implementiert einen Knappen mit:
- Privaten Attributen für Position (x, y) und Richtung
- Öffentlichen Attributen für name und typ
- Getter-Methoden für alle privaten Attribute
- Bewegungs- und Richtungsmethoden
- WICHTIG: Kein 'weiblich' Attribut (Knappen haben kein Geschlecht)
"""

class Knappe:
    def __init__(self, x, y, richtung):
        """
        Initialisiert einen Knappen.
        
        Args:
            x: X-Koordinate (wird privat gespeichert)
            y: Y-Koordinate (wird privat gespeichert)
            richtung: Blickrichtung ("up", "down", "left", "right") (wird privat gespeichert)
        """
        self.__x = x
        self.__y = y
        self.__richtung = richtung
        self.name = "Namenloser Knappe"  # Öffentlich
        self.typ = "Knappe"               # Öffentlich (wichtig für Rendering!)

    def set_richtung(self, neue_richtung):
        """Setzt die Blickrichtung"""
        if neue_richtung in ["up", "down", "left", "right"]:
            self.__richtung = neue_richtung

    def get_x(self):
        """Gibt die X-Koordinate zurück"""
        return self.__x
    
    def get_y(self):
        """Gibt die Y-Koordinate zurück"""
        return self.__y
    
    def get_richtung(self):
        """Gibt die Blickrichtung zurück"""
        return self.__richtung
    
    def get_typ(self):
        """Gibt den Typ zurück"""
        return self.typ
    
    def geh(self):
        """Bewegt den Knappen einen Schritt in Blickrichtung"""
        if self.__richtung == "up":
            self.__y -= 1
        elif self.__richtung == "down":
            self.__y += 1
        elif self.__richtung == "left":
            self.__x -= 1
        elif self.__richtung == "right":
            self.__x += 1
    
    def links(self):
        """Dreht den Knappen nach links (gegen Uhrzeigersinn)"""
        if self.__richtung == "up":
            self.__richtung = "left"
        elif self.__richtung == "down":
            self.__richtung = "right"
        elif self.__richtung == "left":
            self.__richtung = "down"
        elif self.__richtung == "right":
            self.__richtung = "up"
    
    def rechts(self):
        """Dreht den Knappen nach rechts (im Uhrzeigersinn)"""
        if self.__richtung == "up":
            self.__richtung = "right"
        elif self.__richtung == "down":
            self.__richtung = "left"
        elif self.__richtung == "left":
            self.__richtung = "up"
        elif self.__richtung == "right":
            self.__richtung = "down"
