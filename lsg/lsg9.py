from framework.grundlage import level
level.lade(9,weiblich=False)
from framework.grundlage import *

# Ab hier darfst du programmieren:
held.links(100)
for i in range(7):
    held.geh(100)
    if held.ist_auf_herz():
        held.nimm_herz(100)

# Dieser Befehl muss immer am Ende stehen
framework.starten()