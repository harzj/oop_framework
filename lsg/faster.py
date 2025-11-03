import os
import re

# Nutzer nach Wert fragen
wert = input("Welchen Wert soll in die Methoden eingesetzt werden? ")

# Pfad des aktuellen Skripts
pfad = os.path.dirname(os.path.abspath(__file__))

# Methoden, die einfach den Wert als ersten Parameter bekommen
methoden_normal = [
    r'geh', r'links', r'rechts', r'zurueck',
    r'nimm_herz', r'nehme_auf', r'lese_spruch', r'lese_code',
    r'bediene_tor'
]

# Methoden, die das benannte Argument delay_ms=wert bekommen
methoden_delay = [
    r'spruch_sagen', r'code_eingeben'
]

# Muster für die beiden Gruppen
muster = []
for m in methoden_normal:
    # Ersetze sowohl leere als auch bestehende Klammern
    muster.append((rf'(\b{m})\s*\([^)]*\)', rf'\1({wert})'))

for m in methoden_delay:
    muster.append((rf'(\b{m})\s*\([^)]*\)', rf'\1(delay_ms={wert})'))

for datei in os.listdir(pfad):
    if datei.startswith("lsg") and datei.endswith(".py"):
        dateipfad = os.path.join(pfad, datei)
        with open(dateipfad, "r", encoding="utf-8") as f:
            inhalt = f.read()

        neuer_inhalt = inhalt
        for pattern, ersatz in muster:
            neuer_inhalt = re.sub(pattern, ersatz, neuer_inhalt)

        if neuer_inhalt != inhalt:
            with open(dateipfad, "w", encoding="utf-8") as f:
                f.write(neuer_inhalt)
            print(f"Geändert: {datei}")

print("Fertig.")
