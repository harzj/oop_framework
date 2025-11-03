from framework.grundlage import level
level.lade(17,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
while held.verbleibende_herzen() > 0:
    vorne = held.was_ist_vorn()
    if held.ist_auf_herz():
        held.nimm_herz(100)
    elif vorne == "Baum":
        held.links(100)
    else:
        held.geh(100)
    



# Dieser Befehl muss immer am Ende stehen
framework.starten()