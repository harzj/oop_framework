# Beispiel: Held-Klasse mit set_level() Unterstützung
#
# Diese Klasse demonstriert die neue "Level setzen" Funktionalität.
# Der Held kann das Spielfeld abfragen, um intelligente Bewegungen zu machen.

class Held:
    def __init__(self, x, y, richtung, weiblich):
        """Konstruktor - level wird auf None gesetzt"""
        self.level = None  # Wird vom Framework nach Spawn gesetzt
        self.x = x
        self.y = y
        self.richtung = richtung
        self.weiblich = weiblich
        self.name = "Intelligenter Held"
        self.typ = "Held"
    
    def set_level(self, spielfeld):
        """
        Wird vom Framework automatisch nach dem Spawn aufgerufen.
        
        Args:
            spielfeld: Das Spielfeld-Objekt (framework.spielfeld.Spielfeld)
        """
        self.level = spielfeld
        print(f"[Held] Level-Referenz gesetzt: {spielfeld.grid_w}x{spielfeld.grid_h}")
    
    def geh(self):
        """
        Bewegung mit Kollisionserkennung.
        Prüft vor der Bewegung, ob das Zielfeld frei ist.
        """
        if self.level is None:
            # Kein Level gesetzt - einfache Bewegung ohne Prüfung
            if self.richtung == "up":
                self.y -= 1
            elif self.richtung == "down":
                self.y += 1
            elif self.richtung == "left":
                self.x -= 1
            elif self.richtung == "right":
                self.x += 1
            return
        
        # Berechne Zielposition
        ziel_x, ziel_y = self.x, self.y
        if self.richtung == "up":
            ziel_y -= 1
        elif self.richtung == "down":
            ziel_y += 1
        elif self.richtung == "left":
            ziel_x -= 1
        elif self.richtung == "right":
            ziel_x += 1
        
        # Prüfe Spielfeld-Grenzen
        if ziel_x < 0 or ziel_x >= self.level.grid_w:
            print(f"[Held] Bewegung blockiert - außerhalb x-Grenze")
            return
        if ziel_y < 0 or ziel_y >= self.level.grid_h:
            print(f"[Held] Bewegung blockiert - außerhalb y-Grenze")
            return
        
        # Prüfe ob Feld passierbar ist
        try:
            if self.level.ist_feld_frei(ziel_x, ziel_y):
                self.x = ziel_x
                self.y = ziel_y
                print(f"[Held] Bewegt zu ({self.x}, {self.y})")
            else:
                print(f"[Held] Bewegung blockiert - Feld ({ziel_x}, {ziel_y}) nicht frei")
        except Exception as e:
            # Fallback: Bewege trotzdem (für Kompatibilität)
            self.x = ziel_x
            self.y = ziel_y
    
    def links(self):
        """Dreht nach links"""
        richtungen = ["up", "left", "down", "right"]
        try:
            idx = richtungen.index(self.richtung)
            self.richtung = richtungen[(idx + 1) % 4]
        except ValueError:
            self.richtung = "down"
    
    def rechts(self):
        """Dreht nach rechts"""
        richtungen = ["up", "right", "down", "left"]
        try:
            idx = richtungen.index(self.richtung)
            self.richtung = richtungen[(idx + 1) % 4]
        except ValueError:
            self.richtung = "down"
    
    def was_ist_vorn(self):
        """
        Gibt zurück, welches Objekt vor dem Helden ist.
        Nutzt die Level-Referenz um Objekte abzufragen.
        """
        if self.level is None:
            return None
        
        # Berechne Position vor dem Helden
        vorn_x, vorn_y = self.x, self.y
        if self.richtung == "up":
            vorn_y -= 1
        elif self.richtung == "down":
            vorn_y += 1
        elif self.richtung == "left":
            vorn_x -= 1
        elif self.richtung == "right":
            vorn_x += 1
        
        # Suche Objekt an dieser Position
        try:
            for obj in self.level.objekte:
                if hasattr(obj, 'x') and hasattr(obj, 'y'):
                    if obj.x == vorn_x and obj.y == vorn_y:
                        return obj.typ if hasattr(obj, 'typ') else obj.__class__.__name__
        except Exception:
            pass
        
        return None
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_richtung(self):
        return self.richtung
    
    def get_name(self):
        return self.name
    
    def get_weiblich(self):
        return self.weiblich
    
    def get_typ(self):
        return self.typ
