from spielobjekt import Spielobjekt

class Charakter(Spielobjekt):
    def __init__(self, x, y, richtung):
        super().__init__(x, y)
        self.richtung = richtung
        self.name = "Charakter mit Kollision"
        self.typ = "Charakter"
        self.level_objekte = []
    
    def set_level(self, objekte):
        """Speichert Referenz zu Level-Objekten für Kollisionserkennung"""
        self.level_objekte = objekte
    
    def geh(self):
        """Bewegt sich in Richtung, wenn kein Hindernis blockiert"""
        # Berechne Zielposition
        ziel_x = self.x
        ziel_y = self.y
        
        if self.richtung == "up":
            ziel_y -= 1
        elif self.richtung == "down":
            ziel_y += 1
        elif self.richtung == "left":
            ziel_x -= 1
        elif self.richtung == "right":
            ziel_x += 1
        
        # Prüfe Kollision
        kollision = False
        for obj in self.level_objekte:
            obj_x = obj.get_x() if hasattr(obj, 'get_x') else obj.x
            obj_y = obj.get_y() if hasattr(obj, 'get_y') else obj.y
            
            if obj_x == ziel_x and obj_y == ziel_y:
                # Prüfe ob passierbar
                if hasattr(obj, 'ist_passierbar'):
                    if not obj.ist_passierbar():
                        kollision = True
                        break
        
        # Nur bewegen wenn keine Kollision
        if not kollision:
            self.x = ziel_x
            self.y = ziel_y
    
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
    
    def get_richtung(self):
        return self.richtung
    
    def get_name(self):
        return self.name
    
    def set_richtung(self, value):
        if value in ["up", "down", "left", "right"]:
            self.richtung = value
