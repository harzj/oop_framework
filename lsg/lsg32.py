from framework.grundlage import level
level.lade(32,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
for i in range(3):
    level.objekt_hinzufuegen(Tor(2+2*i,1,False))
    held.geh()
    held.geh()
    held.nimm_herz()




# Dieser Befehl muss immer am Ende stehen
framework.starten()
