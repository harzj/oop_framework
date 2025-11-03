from framework.grundlage import level
level.lade(7)
from framework.grundlage import *

# Ab hier darfst du programmieren:
held.bediene_tor(100)
held.geh(100)
held.geh(100)
held.lese_spruch(100)
for i in range(4):
    held.geh(100)
held.links(100)
held.spruch_sagen(delay_ms=100)
held.geh(100)
for i in range(4):
    held.geh(100)
    held.nimm_herz(100)
    held.links(100)
    held.geh(100)
    held.rechts(100)



# Dieser Befehl muss immer am Ende stehen
framework.starten()