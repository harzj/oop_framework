class Gegenstand:
    def __init__(self, art: str):
        self.art = art
        self.typ = "Gegenstand"
        self.im_inventar = False

    def sammeln(self):
        """Sammelt den Gegenstand ein."""
        self.im_inventar = True

    def ablegen(self):
        """Legt den Gegenstand ab."""
        self.im_inventar = False
