"""One-time script: replaces code hints in level35-58 JSON with safe analogies."""
import json
import pathlib

SAFE_CODE = {
    35: [
        "# Analog: Klasse mit Attributen aus Parametern befüllen:",
        "class Konto:",
        "    def __init__(self, nummer, inhaber):",
        "        self.nr = nummer     # Parameter wird genutzt!",
        "        self.inh = inhaber",
        "        self.guthaben = 0    # fester Startwert",
    ],
    36: [],
    37: [
        "# Methoden werden eingerückt in der Klasse definiert:",
        "class Konto:",
        "    def einzahlen(self, betrag):",
        "        self.guthaben += betrag",
        "    def abheben(self, betrag):",
        "        self.guthaben -= betrag",
    ],
    38: [
        "# Import-Syntax (Beispiel):",
        "# In klassen/konto.py:  class Konto: ...",
        "# In schueler.py:",
        "from klassen.konto import Konto",
    ],
    39: [
        "from klassen.held import Held",
        "h = Held(...)  # Parameter aus Klassendiagramm ablesen",
        "level.objekt_hinzufuegen(h)",
    ],
    40: [
        "# Tipp: Passe x oder y je nach Richtung an.",
        "# Mögliche Richtungen: 'up', 'down', 'left', 'right'",
    ],
    41: [
        "# Tipp: Speichere die Richtungen in einer Liste.",
        "RICHTUNGEN = ['up', 'right', 'down', 'left']",
        "# .index() liefert die Position, Modulo (%) dreht im Kreis.",
    ],
    42: [
        "# Tipp: Zweimal links drehen entspricht 180 Grad.",
    ],
    43: [],
    44: [
        "# Analog: Klasse mit x, y und einem Typ-Attribut:",
        "class Konto:",
        "    def __init__(self, nummer, typ):",
        "        self.nr = nummer",
        "        self.typ = typ",
    ],
    45: [
        "# Analog: Klasse mit Getter-Methode:",
        "class Konto:",
        "    def __init__(self, nummer, inhaber):",
        "        self.nr = nummer",
        "        self.inh = inhaber",
        "    def get_inhaber(self):",
        "        return self.inh",
    ],
    46: [
        "# Tipp: Knappe und Held sind sehr ähnlich.",
        "# Schaue dir deine Held-Klasse an – viele Teile kannst du übertragen.",
    ],
    47: [
        "# Analog: Einfache Basisklasse mit zwei Koordinaten:",
        "class Lebewesen:",
        "    def __init__(self, x, y):",
        "        self.x = x",
        "        self.y = y",
        "    def ist_am_leben(self):",
        "        return True",
    ],
    48: [
        "# Analog: Unterklasse ruft Basisklassen-Konstruktor auf:",
        "class Girokonto(Konto):",
        "    def __init__(self, nummer, inhaber):",
        "        super().__init__(nummer, inhaber)",
        "        self.dispo = 500",
    ],
    49: [
        "# Analog: Unterklasse erbt und ergänzt eine Methode:",
        "class Girokonto(Konto):",
        "    def __init__(self, nummer, inhaber):",
        "        super().__init__(nummer, inhaber)",
        "        self.dispo = 500",
        "    def get_dispo(self):",
        "        return self.dispo",
    ],
    50: [
        "# In Python: Attribute ohne __ sind öffentlich.",
        "class Konto:",
        "    def __init__(self, nr):",
        "        self.nr = nr        # öffentlich",
        "        self.__pin = 1234   # privat (Name-Mangling)",
    ],
    51: [
        "# Analog: Zwischenklasse erweitert Basisklasse:",
        "class BankKonto(Konto):",
        "    def __init__(self, nr, inhaber, iban):",
        "        super().__init__(nr, inhaber)",
        "        self.iban = iban",
    ],
    52: [
        "# Analog: Dritte Ebene in der Vererbungskette:",
        "class Girokonto(BankKonto):",
        "    def __init__(self, nr, inhaber, iban):",
        "        super().__init__(nr, inhaber, iban)",
        "        self.dispo = 500",
    ],
    53: [
        "# Tipp: Analog zur Held-Klasse – Knappe erbt von Charakter.",
    ],
    54: [
        "# Platzhalter-Attribut mit None und Setter:",
        "class Konto:",
        "    def __init__(self):",
        "        self.bank = None  # wird später zugewiesen",
        "    def set_bank(self, b):",
        "        self.bank = b",
    ],
    55: [
        "# Tipp: Berechne das Zielfeld (nx, ny) anhand der Richtung.",
        "# Prüfe mit level.gib_objekt_bei(nx, ny):",
        "#   None                   -> freier Weg, Bewegung erlaubt",
        "#   obj.ist_passierbar()   -> True = Bewegung erlaubt",
    ],
    56: [
        "# Analog: Zwei kooperierende Klassen:",
        "class Regal:",
        "    def __init__(self):",
        "        self.produkte = []",
        "    def hinzufuegen(self, p):",
        "        self.produkte.append(p)",
    ],
    57: [
        "# Tipp: Erzeuge das Inventar-Objekt im Konstruktor des Helden.",
        "# Der Rucksack ist ein Attribut – das ist eine Hat-Beziehung.",
    ],
    58: [
        "# Polymorphie – Methode in Unterklasse überschreiben:",
        "class Girokonto(Konto):",
        "    def ist_ueberziehbar(self):",
        "        return True  # überschreibt das Standardverhalten",
    ],
}

lvl_dir = pathlib.Path(__file__).parent.parent / "level"
patched = 0
for lvl_num, code in SAFE_CODE.items():
    p = lvl_dir / f"level{lvl_num}.json"
    if not p.exists():
        print(f"SKIP (missing): {p.name}")
        continue
    data = json.loads(p.read_text(encoding="utf-8"))
    s = data.setdefault("settings", {})
    h = s.setdefault("hints", {})
    h["code"] = code
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    patched += 1
    print(f"OK  {p.name}")

print(f"\nPatched {patched} files.")
