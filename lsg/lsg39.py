from framework.grundlage import level
level.lade(39,weiblich=True)
from framework.grundlage import *
# Ab hier darfst du programmieren:
from klassen.held import Held

held = Held(3, 2, "left", weiblich=True)
level.objekt_hinzufuegen(held)

# Dieser Befehl muss immer am Ende stehen
framework.starten()
