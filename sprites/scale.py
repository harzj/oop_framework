from PIL import Image
import os

# Pfad zum Ordner mit den Bildern
ordner = "."  # <- anpassen, z. B. "./sprites" oder "." für aktuellen Ordner

for datei in os.listdir(ordner):
    if datei.lower().endswith(".png"):
        pfad = os.path.join(ordner, datei)
        with Image.open(pfad) as img:
            neue_breite = img.width // 2
            neue_hoehe = img.height // 2
            verkleinert = img.resize((neue_breite, neue_hoehe), Image.LANCZOS)
            verkleinert.save(pfad)
            print(f"Verkleinert: {datei} → {neue_breite}x{neue_hoehe}")

print("Fertig! Alle PNGs wurden um 50 % verkleinert.")
