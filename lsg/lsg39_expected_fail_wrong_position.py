from framework.grundlage import level
level.lade(39,weiblich=True)
from framework.grundlage import *
# Ab hier darfst du programmieren:
from klassen.held import Held

# FEHLER: Falsche Position (3,3) statt (3,2)
held = Held(3, 3, "left", weiblich=True)
level.objekt_hinzufuegen(held)

# Dieser Befehl muss immer am Ende stehen
framework.starten()
