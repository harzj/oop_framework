from framework.grundlage import level
level.lade(34,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
schluessel = Schluessel(1,0)
schluessel.set_farbe("red")
level.objekt_hinzufuegen(schluessel)
tuer = held.gib_objekt_vor_dir()
tuer.verwende_schluessel(schluessel)
held.geh()
held.geh()
held.nimm_herz()




# Dieser Befehl muss immer am Ende stehen
framework.starten()
