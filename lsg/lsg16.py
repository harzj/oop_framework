from framework.grundlage import level
level.lade(16,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren: 
while held.verbleibende_herzen() >0:
    if held.ist_auf_herz():
        held.nimm_herz(100)
    elif held.was_ist_vorn() == "Weg" or held.was_ist_vorn() == "Herz":
        held.geh(100)
    else:
        held.links(100)
    


# Dieser Befehl muss immer am Ende stehen
framework.starten()