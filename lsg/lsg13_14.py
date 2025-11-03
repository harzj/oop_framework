from framework.grundlage import level
level.lade(13)
from framework.grundlage import *

# Ab hier darfst du programmieren:
held.links(100)
while held.verbleibende_herzen() >0:
    held.geh(100)
    if held.ist_auf_herz():
        held.nehme_auf(100)
    


# Dieser Befehl muss immer am Ende stehen
framework.starten()