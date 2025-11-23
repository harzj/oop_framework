from framework.grundlage import level
level.lade(31,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
for x in range(4):
    held.setze_position(3+2*x,0)
    held.geh()
    held.nimm_herz()


# Dieser Befehl muss immer am Ende stehen
framework.starten()
