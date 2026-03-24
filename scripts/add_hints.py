"""
Fügt Hinweise (hints) und Methoden-Filter zu den Level-JSON-Dateien 0-58 hinzu.
Führt nur Änderungen durch, wenn noch kein 'hints'-Eintrag in 'settings' vorhanden ist.
"""
import json
from pathlib import Path

LEVEL_DIR = Path(__file__).parent.parent / "level"

# ---------------------------------------------------------------------------
# Methoden-Gruppen (Schlüssel = Methodenname im Held-Tab ohne "()")
# ---------------------------------------------------------------------------
M_BASIC       = ["geh", "links", "rechts", "zurueck"]
M_HERZ        = M_BASIC + ["ist_auf_herz", "nehme_auf", "verbleibende_herzen"]
M_HERZ_PLUS   = M_HERZ + ["herzen_vor_mir"]
M_SEHEN       = M_HERZ_PLUS + ["was_ist_vorn", "was_ist_links", "was_ist_rechts"]
M_OBJEKTE     = M_SEHEN + ["gib_objekt_vor_dir", "gib_knappe", "lese_spruch", "sage_spruch", "bediene_tor"]
M_ALLE        = None  # None = kein Filter, zeige alles

# ---------------------------------------------------------------------------
# Hints-Daten je Level
# format:  level_nr -> {"text": [...], "code": [...], "methoden": [...|None]}
# ---------------------------------------------------------------------------
HINTS = {
    # ── Level 0–8: Grundbewegungen ─────────────────────────────────────────
    0: {
        "text": [
            "Willkommen im OOP-Framework! Dieses Level zeigt dir den Aufbau der Spielwelt.",
            "Nutze geh(), links() und rechts(), um den Helden zu bewegen.",
        ],
        "code": [
            "held.geh()",
            "held.links()",
            "held.rechts()",
        ],
        "methoden": M_BASIC,
    },
    1: {
        "text": [
            "Bewege den Helden mit geh(), links() und rechts() ans Ziel.",
            "Mit zurueck() dreht sich der Held um 180°.",
        ],
        "code": [
            "held.geh()",
            "held.rechts()",
            "held.geh()",
        ],
        "methoden": M_BASIC,
    },
    2: {
        "text": [
            "Nutze eine for-Schleife, um mehrere Schritte effizient zu programmieren.",
        ],
        "code": [
            "for i in range(5):",
            "    held.geh()",
        ],
        "methoden": M_BASIC,
    },
    3: {
        "text": [
            "Auch der Knappe kann sich mit geh(), links() und rechts() bewegen.",
            "Steuere Held und Knappe abwechselnd.",
        ],
        "code": [
            "held.geh()",
            "knappe.rechts()",
            "knappe.geh()",
        ],
        "methoden": M_BASIC,
    },
    4: {
        "text": [
            "Bewege den Helden vorsichtig – Monster können gefährlich sein!",
            "Versuche, dem Monster auszuweichen.",
        ],
        "code": [
            "held.links()",
            "held.geh()",
        ],
        "methoden": M_BASIC,
    },
    5: {
        "text": [
            "Nutze for-Schleifen, um wiederholte Bewegungen zu vereinfachen.",
        ],
        "code": [
            "for i in range(3):",
            "    held.geh()",
            "held.links()",
            "held.geh()",
        ],
        "methoden": M_BASIC,
    },
    6: {
        "text": [
            "Held und Knappe können unabhängig voneinander gesteuert werden.",
        ],
        "code": [
            "for i in range(4):",
            "    held.geh()",
            "knappe.links()",
            "knappe.geh()",
        ],
        "methoden": M_BASIC,
    },
    7: {
        "text": [
            "Plane die Route des Helden sorgfältig, um alle Felder zu erreichen.",
        ],
        "code": [
            "held.geh()",
            "held.rechts()",
            "held.geh()",
        ],
        "methoden": M_BASIC,
    },
    8: {
        "text": [
            "Kombiniere Schleifen und Richtungsänderungen für komplexe Pfade.",
        ],
        "code": [
            "for i in range(3):",
            "    held.geh()",
            "    held.links()",
        ],
        "methoden": M_BASIC,
    },

    # ── Level 9–15: Herzen sammeln ─────────────────────────────────────────
    9: {
        "text": [
            "Nutze ist_auf_herz(), um zu prüfen, ob der Held auf einem Herz steht.",
            "Rufe nehme_auf() auf, wenn du auf einem Herz stehst, um es einzusammeln.",
        ],
        "code": [
            "held.geh()",
            "if held.ist_auf_herz():",
            "    held.nehme_auf()",
        ],
        "methoden": M_HERZ,
    },
    10: {
        "text": [
            "Auch der Knappe kann mit ist_auf_herz() und nehme_auf() Herzen sammeln.",
            "Steuere beide Charaktere, um alle Herzen einzusammeln.",
        ],
        "code": [
            "if held.ist_auf_herz():",
            "    held.nehme_auf()",
            "if knappe.ist_auf_herz():",
            "    knappe.nehme_auf()",
        ],
        "methoden": M_HERZ,
    },
    11: {
        "text": [
            "Nutze eine while-Schleife mit verbleibende_herzen(), um solange zu laufen, bis alle Herzen gesammelt sind.",
        ],
        "code": [
            "while held.verbleibende_herzen() > 0:",
            "    held.geh()",
            "    if held.ist_auf_herz():",
            "        held.nehme_auf()",
        ],
        "methoden": M_HERZ,
    },
    12: {
        "text": [
            "Dein Code aus Level 11 sollte auch dieses Level lösen – durch verbleibende_herzen() passt er sich automatisch an.",
        ],
        "code": [
            "while held.verbleibende_herzen() > 0:",
            "    held.geh()",
            "    if held.ist_auf_herz():",
            "        held.nehme_auf()",
        ],
        "methoden": M_HERZ,
    },
    13: {
        "text": [
            "Nutze verbleibende_herzen() als Schleifenbedingung für allgemeinen Code.",
            "herzen_vor_mir() gibt True zurück, wenn ein Herz direkt vor dem Helden liegt.",
        ],
        "code": [
            "while held.verbleibende_herzen() > 0:",
            "    if held.ist_auf_herz():",
            "        held.nehme_auf()",
            "    else:",
            "        held.geh()",
        ],
        "methoden": M_HERZ_PLUS,
    },
    14: {
        "text": [
            "Kombiniere verbleibende_herzen() und herzen_vor_mir() für einen flexiblen Herzsammler.",
        ],
        "code": [
            "while held.verbleibende_herzen() > 0:",
            "    if held.ist_auf_herz():",
            "        held.nehme_auf()",
            "    elif held.herzen_vor_mir():",
            "        held.geh()",
            "    else:",
            "        held.links()",
        ],
        "methoden": M_HERZ_PLUS,
    },
    15: {
        "text": [
            "Nutze alle bisher gelernten Methoden, um dieses Level zu lösen.",
        ],
        "code": [],
        "methoden": M_HERZ_PLUS,
    },

    # ── Level 16–19: Umgebung erkunden ────────────────────────────────────
    16: {
        "text": [
            "was_ist_vorn() gibt den Typ des Objekts vor dem Held als Text zurück.",
            "Mögliche Rückgabewerte: 'Baum', 'Wand', 'Herz', 'Tor', 'Tuer', 'Monster', 'None' (freier Weg).",
            "Nutze print(held.was_ist_vorn()), um Objekte in der Konsole zu erkunden.",
        ],
        "code": [
            "print(held.was_ist_vorn())",
            "print(knappe.was_ist_links())",
            "print(knappe.was_ist_rechts())",
        ],
        "methoden": M_SEHEN,
    },
    17: {
        "text": [
            "Prüfe mit was_ist_vorn(), ob ein Baum im Weg steht, und drehe dich dann links.",
            "Sammle alle Herzen ein, solange noch welche übrig sind.",
        ],
        "code": [
            "while held.verbleibende_herzen() > 0:",
            "    if held.was_ist_vorn() == 'Baum':",
            "        held.links()",
            "    else:",
            "        held.geh()",
            "        if held.ist_auf_herz():",
            "            held.nehme_auf()",
        ],
        "methoden": M_SEHEN,
    },
    18: {
        "text": [
            "Knobelaufgabe: Löse das Level nur mit was_ist_vorn() und Schleifen.",
            "Tipp: Prüfe alle vier Richtungen, bevor du dich bewegst.",
        ],
        "code": [],
        "methoden": M_SEHEN,
    },
    19: {
        "text": [
            "Knobelaufgabe: Kombiniere was_ist_vorn(), was_ist_links() und was_ist_rechts().",
        ],
        "code": [
            "if held.was_ist_links() == 'None':",
            "    held.links()",
            "elif held.was_ist_vorn() == 'None':",
            "    held.geh()",
            "else:",
            "    held.rechts()",
        ],
        "methoden": M_SEHEN,
    },

    # ── Level 20–25: Zugriff auf Objekte ──────────────────────────────────
    20: {
        "text": [
            "Objekte sind im Speicher, aber du brauchst eine Variable, um auf sie zuzugreifen.",
            "Nutze die vorhandenen Objekte zettel und tuer, um den Spruch zu lesen und anzuwenden.",
        ],
        "code": [
            "spruch = zettel.gib_spruch()",
            "tuer.spruch_anwenden(spruch)",
        ],
        "methoden": M_OBJEKTE,
    },
    21: {
        "text": [
            "Nutze gib_knappe() oder gib_objekt_bei(x, y), um Zugriff auf weitere Objekte zu erhalten.",
            "Tipp: level.gib_objekt_bei(x, y) liefert das Objekt an einer bestimmten Position.",
        ],
        "code": [
            "t = level.gib_objekt_bei(0, 3)",
            "z = level.gib_objekt_bei(2, 4)",
            "spruch = z.gib_spruch()",
            "t.spruch_anwenden(spruch)",
        ],
        "methoden": M_OBJEKTE,
    },
    22: {
        "text": [
            "Nutze gib_objekt_bei(x, y), um Zugriff auf beliebige Objekte im Level zu erhalten.",
        ],
        "code": [
            "obj = level.gib_objekt_bei(3, 2)",
            "print(obj)",
        ],
        "methoden": M_OBJEKTE,
    },
    23: {
        "text": [
            "gib_objekt_vor_dir() gibt dir Zugriff auf das Objekt direkt vor dem Helden.",
            "Tipp: Nutze es, um mit Toren und Zetteln zu interagieren.",
        ],
        "code": [
            "obj = held.gib_objekt_vor_dir()",
            "print(obj)",
        ],
        "methoden": M_OBJEKTE,
    },
    24: {
        "text": [
            "Nutze bediene_tor(), um das Tor vor dem Helden oder Knappe zu öffnen/schließen.",
        ],
        "code": [
            "held.bediene_tor()",
            "knappe.geh()",
        ],
        "methoden": M_OBJEKTE,
    },
    25: {
        "text": [
            "Kombiniere alle bisherigen Methoden, um das Level zu lösen.",
        ],
        "code": [],
        "methoden": M_OBJEKTE,
    },

    # ── Level 26: Datenkapselung – setze_richtung ─────────────────────────
    26: {
        "text": [
            "Du kannst die Richtung des Helden nicht einfach direkt setzen.",
            "Nutze stattdessen held.setze_richtung('N'), um den Helden nach Norden zu drehen.",
            "Gültige Richtungen: 'up' (Norden), 'down' (Süden), 'left' (Westen), 'right' (Osten).",
        ],
        "code": [
            "held.setze_richtung('up')",
            "held.geh()",
            "held.nehme_auf()",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 27–31: Getter und Setter, Schlüssel ─────────────────────────
    27: {
        "text": [
            "Farbige Schlüssel passen zu farbigen Schlössern (Türen).",
            "Nutze gib_objekt_bei(x, y) auf dem Level, um an den Schlüssel zu gelangen.",
            "Mit get_farbe() liest du die Farbe des Schlüssels aus.",
        ],
        "code": [
            "schluessel = level.gib_objekt_bei(3, 3)",
            "tuer = level.gib_objekt_bei(2, 1)",
            "tuer.verwende_schluessel(schluessel)",
        ],
        "methoden": M_ALLE,
    },
    28: {
        "text": [
            "Prüfe mit get_farbe(), welche Farbe der Schlüssel hat, und verwende dann den passenden Schlüssel.",
        ],
        "code": [
            "schluessel = level.gib_objekt_bei(3, 3)",
            "farbe = schluessel.get_farbe()",
            "print(farbe)",
        ],
        "methoden": M_ALLE,
    },
    29: {
        "text": [
            "Du brauchst die Farbe des Schlüssels, um die richtige Tür zu öffnen.",
            "Vergleiche die Farben mit get_farbe() vom Schlüssel und der Tür.",
        ],
        "code": [
            "s = level.gib_objekt_bei(3, 3)",
            "t = level.gib_objekt_bei(2, 1)",
            "if s.get_farbe() == t.get_farbe():",
            "    t.verwende_schluessel(s)",
        ],
        "methoden": M_ALLE,
    },
    30: {
        "text": [
            "Mit set_farbe(f) kannst du die Farbe eines Schlüssels ändern.",
            "Farben: 'blue', 'golden', 'green', 'red', 'violet'.",
        ],
        "code": [
            "schluessel = level.gib_objekt_bei(3, 3)",
            "schluessel.set_farbe('red')",
            "tuer = level.gib_objekt_bei(2, 1)",
            "tuer.verwende_schluessel(schluessel)",
        ],
        "methoden": M_ALLE,
    },
    31: {
        "text": [
            "Mit setze_position(x, y) kannst du einen Schlüssel an eine neue Stelle teleportieren.",
            "Tipp: Finde den richtigen Schlüssel und positioniere ihn so, dass du ihn aufnehmen kannst.",
        ],
        "code": [
            "schluessel = level.gib_objekt_bei(5, 2)",
            "schluessel.setze_position(1, 1)",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 32–34: Objekte erzeugen ─────────────────────────────────────
    32: {
        "text": [
            "Du kannst neue Objekte mit ihrem Konstruktor erzeugen und zum Level hinzufügen.",
            "Beispiel: tor1 = Tor(1, 2, True)  →  level.objekt_hinzufuegen(tor1)",
            "Stelle Hindernisse vor die Bogenschützen, um den Helden zu schützen.",
        ],
        "code": [
            "from framework.tor import Tor",
            "tor1 = Tor(1, 2, True)",
            "level.objekt_hinzufuegen(tor1)",
        ],
        "methoden": M_ALLE,
    },
    33: {
        "text": [
            "Erzeuge Monster-Objekte und füge sie dem Level hinzu, um das Level zu lösen.",
            "Schau dir das Klassendiagramm von Monster an: Monster(x, y, richtung).",
        ],
        "code": [
            "from framework.monster import Monster",
            "m = Monster(4, 2, 'up')",
            "level.objekt_hinzufuegen(m)",
        ],
        "methoden": M_ALLE,
    },
    34: {
        "text": [
            "Erzeuge einen passenden Schlüssel mit dem Konstruktor und füge ihn dem Level hinzu.",
            "Schluessel(x, y) erzeugt einen Schlüssel an der angegebenen Position.",
        ],
        "code": [
            "from framework.schluessel import Schluessel",
            "s = Schluessel(3, 3)",
            "level.objekt_hinzufuegen(s)",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 35–37: Klasse Held implementieren ───────────────────────────
    35: {
        "text": [
            "Implementiere die Klasse Held in schueler.py, damit der Held im Level erscheint.",
            "Der Konstruktor bekommt: xp, yp (Position), richtung (str), w (weiblich, bool).",
            "Setze alle Attribute (x, y, richtung, name, typ, weiblich) im __init__.",
        ],
        "code": [
            "# Analog: Klasse mit Attributen aus Parametern befüllen:",
            "class Konto:",
            "    def __init__(self, nummer, inhaber):",
            "        self.nr = nummer     # Parameter wird genutzt!",
            "        self.inh = inhaber",
            "        self.guthaben = 0    # fester Startwert",
        ],
        "methoden": M_ALLE,
    },
    36: {
        "text": [
            "Wenn Level 35 funktioniert, sollte der gleiche Code auch Level 36 direkt lösen.",
            "Überprüfe, ob alle Attribute korrekt gesetzt sind.",
        ],
        "code": [],
        "methoden": M_ALLE,
    },
    37: {
        "text": [
            "Füge dem Helden die Methoden geh(), links(), rechts() und zurueck() hinzu.",
            "Diese Methoden verändern Position und Richtung des Helden.",
        ],
        "code": [
            "# Methoden werden eingerückt in der Klasse definiert:",
            "class Konto:",
            "    def einzahlen(self, betrag):",
            "        self.guthaben += betrag",
            "    def abheben(self, betrag):",
            "        self.guthaben -= betrag",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 38–39: Modularisierung ──────────────────────────────────────
    38: {
        "text": [
            "Lagere die Helden-Klasse in eine eigene Datei klassen/held.py aus.",
            "Importiere sie dann in schueler.py: from klassen.held import Held",
        ],
        "code": [
            "# Import-Syntax (Beispiel):",
            "# In klassen/konto.py:  class Konto: ...",
            "# In schueler.py:",
            "from klassen.konto import Konto",
        ],
        "methoden": M_ALLE,
    },
    39: {
        "text": [
            "Erzeuge einen Helden und füge ihn dem Level hinzu.",
            "Importiere deine eigene Helden-Klasse aus klassen/held.py.",
        ],
        "code": [
            "from klassen.held import Held",
            "h = Held(...)  # Parameter aus Klassendiagramm ablesen",
            "level.objekt_hinzufuegen(h)",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 40–43: Held erweitern ───────────────────────────────────────
    40: {
        "text": [
            "Ergänze die Held-Klasse um die Methode geh(), die den Helden einen Schritt bewegt.",
            "Nutze die Richtung des Helden, um x oder y entsprechend zu verändern.",
        ],
        "code": [
            "# Tipp: Passe x oder y je nach Richtung an.",
            "# Mögliche Richtungen: 'up', 'down', 'left', 'right'",
        ],
        "methoden": M_ALLE,
    },
    41: {
        "text": [
            "Ergänze links() und rechts() in der Held-Klasse.",
            "Richtungsfolge links: up → left → down → right → up.",
        ],
        "code": [
            "# Tipp: Speichere die Richtungen in einer Liste.",
            "RICHTUNGEN = ['up', 'right', 'down', 'left']",
            "# .index() liefert die Position, Modulo (%) dreht im Kreis.",
        ],
        "methoden": M_ALLE,
    },
    42: {
        "text": [
            "Ergänze zurueck() – dreht den Helden um 180°.",
        ],
        "code": [
            "# Tipp: Zweimal links drehen entspricht 180 Grad.",
        ],
        "methoden": M_ALLE,
    },
    43: {
        "text": [
            "Teste alle Methoden deiner Held-Klasse in diesem Level.",
        ],
        "code": [],
        "methoden": M_ALLE,
    },

    # ── Level 44–45: Hindernis und Zettel ─────────────────────────────────
    44: {
        "text": [
            "Implementiere zusätzlich die Klasse Hindernis.",
            "Hindernis hat: x, y, typ. Der Konstruktor: __init__(self, x, y, art).",
        ],
        "code": [
            "# Analog: Klasse mit x, y und einem Typ-Attribut:",
            "class Konto:",
            "    def __init__(self, nummer, typ):",
            "        self.nr = nummer",
            "        self.typ = typ",
        ],
        "methoden": M_ALLE,
    },
    45: {
        "text": [
            "Implementiere die Klasse Zettel.",
            "Zettel hat: x, y, typ='Zettel'. Mit gib_spruch() wird der Spruch zurückgegeben.",
        ],
        "code": [
            "# Analog: Klasse mit Getter-Methode:",
            "class Konto:",
            "    def __init__(self, nummer, inhaber):",
            "        self.nr = nummer",
            "        self.inh = inhaber",
            "    def get_inhaber(self):",
            "        return self.inh",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 46: Knappe ──────────────────────────────────────────────────
    46: {
        "text": [
            "Implementiere die Klasse Knappe. Sie sieht dem Helden sehr ähnlich.",
            "Knappe hat: x, y, richtung, name, typ. Konstruktor: __init__(self, x, y, art).",
            "Tipp: Schaue dir deine Held-Klasse an – viele Teile kannst du übertragen.",
        ],
        "code": [
            "# Tipp: Knappe und Held sind sehr ähnlich.",
            "# Schaue dir deine Held-Klasse an – viele Teile kannst du übertragen.",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 47–50: Vererbung ────────────────────────────────────────────
    47: {
        "text": [
            "Implementiere die Basisklasse Spielobjekt in spielobjekt.py.",
            "Spielobjekt hat die Attribute x und y. ist_passierbar() gibt standardmäßig False zurück.",
            "Das Attribut typ wird auf None gesetzt (kein Typ für ein generisches Spielobjekt).",
        ],
        "code": [
            "# Analog: Einfache Basisklasse mit zwei Koordinaten:",
            "class Lebewesen:",
            "    def __init__(self, x, y):",
            "        self.x = x",
            "        self.y = y",
            "    def ist_am_leben(self):",
            "        return True",
        ],
        "methoden": M_ALLE,
    },
    48: {
        "text": [
            "Lass Hindernis von Spielobjekt erben.",
            "Rufe im Konstruktor super().__init__(x, y) auf, damit die Basisklasse x und y setzt.",
            "Für private Attribute der Basisklasse nutze: self._Spielobjekt__typ = art",
        ],
        "code": [
            "# Analog: Unterklasse ruft Basisklassen-Konstruktor auf:",
            "class Girokonto(Konto):",
            "    def __init__(self, nummer, inhaber):",
            "        super().__init__(nummer, inhaber)",
            "        self.dispo = 500",
        ],
        "methoden": M_ALLE,
    },
    49: {
        "text": [
            "Lass Zettel von Spielobjekt erben – analog zu Hindernis.",
            "Ergänze die Methode gib_spruch() in Zettel.",
        ],
        "code": [
            "# Analog: Unterklasse erbt und ergänzt eine Methode:",
            "class Girokonto(Konto):",
            "    def __init__(self, nummer, inhaber):",
            "        super().__init__(nummer, inhaber)",
            "        self.dispo = 500",
            "    def get_dispo(self):",
            "        return self.dispo",
        ],
        "methoden": M_ALLE,
    },
    50: {
        "text": [
            "In Python werden private Attribute bei Vererbung mit dem Klassennamen mangled: _Klasse__attribut.",
            "Um das zu vereinfachen, setze alle Attribute in Spielobjekt öffentlich (ohne Unterstrich).",
            "Lade die aktualisierten Dateien aus der OSS und löse Level 50.",
        ],
        "code": [
            "# In Python: Attribute ohne __ sind öffentlich.",
            "class Konto:",
            "    def __init__(self, nr):",
            "        self.nr = nr        # öffentlich",
            "        self.__pin = 1234   # privat (Name-Mangling)",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 51–55: Charakter-Klasse ─────────────────────────────────────
    51: {
        "text": [
            "Implementiere die Klasse Charakter, die von Spielobjekt erbt.",
            "Charakter fügt die Attribute richtung und name hinzu sowie Methoden geh(), links(), rechts().",
        ],
        "code": [
            "# Analog: Zwischenklasse erweitert Basisklasse:",
            "class BankKonto(Konto):",
            "    def __init__(self, nr, inhaber, iban):",
            "        super().__init__(nr, inhaber)",
            "        self.iban = iban",
        ],
        "methoden": M_ALLE,
    },
    52: {
        "text": [
            "Passe Held so an, dass es jetzt von Charakter erbt.",
            "Füge die Methode get_weiblich() hinzu.",
        ],
        "code": [
            "# Analog: Dritte Ebene in der Vererbungskette:",
            "class Girokonto(BankKonto):",
            "    def __init__(self, nr, inhaber, iban):",
            "        super().__init__(nr, inhaber, iban)",
            "        self.dispo = 500",
        ],
        "methoden": M_ALLE,
    },
    53: {
        "text": [
            "Passe Knappe so an, dass es jetzt von Charakter erbt – analog zu Held.",
        ],
        "code": [
            "# Tipp: Analog zur Held-Klasse – Knappe erbt von Charakter.",
        ],
        "methoden": M_ALLE,
    },
    54: {
        "text": [
            "Füge Charakter das Attribut 'level = None' und die Methode set_level(l) hinzu.",
            "Das Framework setzt das Level automatisch, sobald ein Charakter im Level vorhanden ist.",
        ],
        "code": [
            "# Platzhalter-Attribut mit None und Setter:",
            "class Konto:",
            "    def __init__(self):",
            "        self.bank = None  # wird später zugewiesen",
            "    def set_bank(self, b):",
            "        self.bank = b",
        ],
        "methoden": M_ALLE,
    },
    55: {
        "text": [
            "Implementiere Kollisionsprüfung in geh(): Nutze self.level.gib_objekt_bei(nx, ny).",
            "Eine Bewegung ist erlaubt, wenn das Zielfeld None ist oder ist_passierbar() True zurückgibt.",
        ],
        "code": [
            "# Tipp: Berechne das Zielfeld (nx, ny) anhand der Richtung.",
            "# Prüfe mit level.gib_objekt_bei(nx, ny):",
            "#   None                   -> freier Weg, Bewegung erlaubt",
            "#   obj.ist_passierbar()   -> True = Bewegung erlaubt",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 56–57: Komposition ──────────────────────────────────────────
    56: {
        "text": [
            "Implementiere Gegenstand und Inventar.",
            "Gegenstand: art (str), typ='Gegenstand', im_inventar=False. Methode: sammeln().",
            "Inventar: items=[], kapazitaet=10, gold=0. Methoden: item_hinzufuegen(i), hat_item(art), anzahl_items().",
        ],
        "code": [
            "# Analog: Zwei kooperierende Klassen:",
            "class Regal:",
            "    def __init__(self):",
            "        self.produkte = []",
            "    def hinzufuegen(self, p):",
            "        self.produkte.append(p)",
        ],
        "methoden": M_ALLE,
    },
    57: {
        "text": [
            "Füge Held und Knappe jeweils ein Inventar-Attribut (rucksack) hinzu.",
            "Der Held erzeugt beim Start ein Schwert-Gegenstand und legt es in seinen Rucksack.",
        ],
        "code": [
            "# Tipp: Erzeuge das Inventar-Objekt im Konstruktor des Helden.",
            "# Der Rucksack ist ein Attribut – das ist eine Hat-Beziehung.",
        ],
        "methoden": M_ALLE,
    },

    # ── Level 58: Polymorphie ──────────────────────────────────────────────
    58: {
        "text": [
            "Polymorphie: Überschreibe ist_passierbar() in Zettel, sodass Zettel betretbar ist.",
            "Herzen und Zettel sind immer begehbar – gib in ihrer Klasse True zurück.",
        ],
        "code": [
            "# Polymorphie – Methode in Unterklasse überschreiben:",
            "class Girokonto(Konto):",
            "    def ist_ueberziehbar(self):",
            "        return True  # überschreibt das Standardverhalten der Basisklasse",
        ],
        "methoden": M_ALLE,
    },
}

# ---------------------------------------------------------------------------
# Level-Dateien aktualisieren
# ---------------------------------------------------------------------------
updated = 0
skipped = 0
for lvl_nr, hints_data in HINTS.items():
    path = LEVEL_DIR / f"level{lvl_nr}.json"
    if not path.exists():
        print(f"  WARNUNG: {path.name} nicht gefunden – übersprungen.")
        continue

    data = json.loads(path.read_text(encoding="utf-8"))

    # settings-Dict sicherstellen
    if "settings" not in data or data["settings"] is None:
        data["settings"] = {}

    if "hints" in data["settings"]:
        skipped += 1
        continue

    hints_entry = {
        "text":     hints_data.get("text", []),
        "code":     hints_data.get("code", []),
    }
    methoden = hints_data.get("methoden")
    if methoden is not None:
        hints_entry["methoden"] = methoden  # None = kein Eintrag = kein Filter

    data["settings"]["hints"] = hints_entry

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    updated += 1
    print(f"  ✓ level{lvl_nr}.json aktualisiert")

print(f"\nFertig: {updated} aktualisiert, {skipped} übersprungen (hints bereits vorhanden).")
