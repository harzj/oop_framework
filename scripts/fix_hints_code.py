"""
Patches the 'code' field of hints in level JSON files 35-58.
Replaces actual student-class solutions with safe generic analogies.
"""
import json
from pathlib import Path

LEVEL_DIR = Path(__file__).parent.parent / "level"

# Safe code snippets per level.
# Rule: NEVER show the actual implementation the student needs to write.
#       Use Konto/Girokonto analogies for structure; brief hints for algorithms.
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
        "# Moegliche Richtungen: 'up', 'down', 'left', 'right'",
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
        "# Tipp: Knappe und Held sind sehr aehnlich.",
        "# Schaue dir deine Held-Klasse an – viele Teile kannst du uebertragen.",
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
        "# Analog: Unterklasse erbt und ergaenzt eine Methode:",
        "class Girokonto(Konto):",
        "    def __init__(self, nummer, inhaber):",
        "        super().__init__(nummer, inhaber)",
        "        self.dispo = 500",
        "    def get_dispo(self):",
        "        return self.dispo",
    ],
    50: [
        "# In Python: Attribute ohne __ sind oeffentlich.",
        "class Konto:",
        "    def __init__(self, nr):",
        "        self.nr = nr        # oeffentlich",
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
        "        self.bank = None  # wird spaeter zugewiesen",
        "    def set_bank(self, b):",
        "        self.bank = b",
    ],
    55: [
        "# Tipp: Berechne das Zielfeld (nx, ny) anhand der Richtung.",
        "# Pruefe mit level.gib_objekt_bei(nx, ny):",
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
        "# Polymorphie – Methode in Unterklasse ueberschreiben:",
        "class Girokonto(Konto):",
        "    def ist_ueberziehbar(self):",
        "        return True  # ueberschreibt das Standardverhalten der Basisklasse",
    ],
}


def main():
    updated = 0
    for lvl_nr, safe_code in SAFE_CODE.items():
        path = LEVEL_DIR / f"level{lvl_nr}.json"
        if not path.exists():
            print(f"  WARNUNG: {path.name} nicht gefunden")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        hints = (data.get("settings") or {}).get("hints")
        if hints is None:
            print(f"  WARNUNG: level{lvl_nr}.json hat keine hints-Sektion")
            continue
        hints["code"] = safe_code
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  level{lvl_nr}.json gepatcht")
        updated += 1
    print(f"\nFertig: {updated} Level-Dateien aktualisiert.")


if __name__ == "__main__":
    main()
