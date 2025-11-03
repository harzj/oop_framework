from framework.grundlage import level
level.lade(104,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:


knappe = held.gib_knappe()
knappe.geh(100)
monster = knappe.gib_objekt_vor_dir()

t = monster.gib_objekt_vor_dir().gib_spruch()

monster.rechts(100)
monster.angriff()
door = held.gib_objekt_vor_dir()

door.spruch_anwenden(t)
held.geh(100)
held.geh(100)
held.geh(100)
held.nimm_herz(100)




# Dieser Befehl muss immer am Ende stehen
framework.starten()