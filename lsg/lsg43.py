from framework.grundlage import level
level.lade(43,weiblich=True)
from framework.grundlage import *
# Ab hier darfst du programmieren:
# Level 43: Move to target with set_richtung
held.set_richtung("down")
held.geh()
held.set_richtung("right")
held.geh()

# Dieser Befehl muss immer am Ende stehen
framework.starten()
