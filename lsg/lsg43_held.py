from framework.grundlage import level
level.lade(43,weiblich=True)
from framework.grundlage import *
# Ab hier darfst du programmieren:
# Level 43: Move to target (2,2) from (1,1) - Held mit set_richtung
held.set_richtung("right")
held.geh()       # Move right: (1,1) -> (2,1)
held.set_richtung("down")
held.geh()       # Move down: (2,1) -> (2,2)

# Dieser Befehl muss immer am Ende stehen
framework.starten()
