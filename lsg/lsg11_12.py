from framework.grundlage import level
level.lade(12)
from framework.grundlage import *

# Ab hier darfst du programmieren:
held.links(100)
held.geh(100)
while held.ist_auf_herz():
    held.nehme_auf(100)
    held.geh(100)


# Dieser Befehl muss immer am Ende stehen
framework.starten()