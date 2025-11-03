from framework.grundlage import level
level.lade(21,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
tuer = held.gib_objekt_vor_dir()
knappe = held.gib_knappe()
knappe.geh(100)
zettel = knappe.gib_objekt_vor_dir()

t = zettel.gib_spruch()
tuer.spruch_anwenden(t)
held.geh(100)
held.geh(100)
held.nimm_herz(100)



# Dieser Befehl muss immer am Ende stehen
framework.starten()