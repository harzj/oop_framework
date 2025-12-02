from framework.grundlage import level
level.lade(42,weiblich=True)
from framework.grundlage import *
# Ab hier darfst du programmieren:
# Level 42: Move to target (2,2) from (1,1) - Held mit privaten Attributen und Bewegungsmethoden
# Path: down to (1,2), then left-turn to face right, then move to (2,2)
held.geh()       # Move down: (1,1) -> (1,2)
held.links()     # Turn left to face right (east)
held.geh()       # Move right: (1,2) -> (2,2)

# Dieser Befehl muss immer am Ende stehen
framework.starten()
