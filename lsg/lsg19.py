from framework.grundlage import level
level.lade(19,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
while held.verbleibende_herzen() > 0:
    vorne = held.was_ist_vorn()
    links = held.was_ist_links()
    rechts = held.was_ist_rechts()

    if held.ist_auf_herz():
        held.nimm_herz(100)
    elif rechts == "Herz" or rechts == "Weg":
        held.rechts(100)
        held.geh(100)
    elif vorne == "Weg" or vorne == "Herz":
        held.geh(100)

    else:
        held.links(100)
    



# Dieser Befehl muss immer am Ende stehen
framework.starten()