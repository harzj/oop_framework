from framework.grundlage import level
level.lade(0)
from framework.grundlage import *

#framework = level.framework
#held = level.held

# Befehlsliste:
# geh, links, rechts, nehme_auf(100), attack, was_ist_vor_mir, gib_objekt_vor_dir, ist_auf_herz
# lese_code, code_eingeben

# Ab hier darfst du programmieren:
s=100
held.geh(s)
held.links(s)
held.geh()
held.geh()
held.geh()
held.links()
held.geh()

# Dieser Befehl muss immer am Ende stehen
framework.starten()