from framework.grundlage import level
level.lade(40, weiblich=True)
from framework.grundlage import *
from klassen.held import Held

# Level 40: Private Attribute ohne Getter
held = Held(3, 2, "left", weiblich=True)
level.objekt_hinzufuegen(held)

framework.starten()
