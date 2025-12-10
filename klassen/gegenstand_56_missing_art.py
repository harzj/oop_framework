# FEHLER: Gegenstand ohne 'art' Attribut
class Gegenstand:
    def __init__(self, art: str):
        # FEHLER: art wird nicht gespeichert!
        self.typ = "Gegenstand"
        self.im_inventar = False

    def sammeln(self):
        """Sammelt den Gegenstand ein."""
        self.im_inventar = True
