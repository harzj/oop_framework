from framework.grundlage import level
level.lade(22,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
zettel = level.gib_objekt_bei(3,2)
tuer = level.gib_objekt_bei(0,2)
t = zettel.gib_spruch()
tuer.spruch_anwenden(t)
held.geh(100)
held.geh(100)
held.nimm_herz(100)

# Dieser Befehl muss immer am Ende stehen
framework.starten()