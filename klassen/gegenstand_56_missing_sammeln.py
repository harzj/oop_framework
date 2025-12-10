# FEHLER: Gegenstand ohne 'sammeln' Methode
class Gegenstand:
    def __init__(self, art: str):
        self.art = art
        self.typ = "Gegenstand"
        self.im_inventar = False

    # FEHLER: sammeln() Methode fehlt!
