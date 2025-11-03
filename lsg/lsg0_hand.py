from framework.grundlage import level
level.lade(0)
from framework.grundlage import *

#framework = level.framework
#held = level.held

# Befehlsliste:
# geh, links, rechts, nehme_auf(100), attack, was_ist_vor_mir, gib_objekt_vor_dir, ist_auf_herz
# lese_code, code_eingeben

# Ab hier darfst du programmieren:
s=0
held.geh(100)
held.geh(100)
held.lese_code(100)
held.geh(100)
held.links(100)
held.geh(100)
held.bediene_tor(100)
held.geh(100)
held.geh(100)
held.nehme_auf(100)
held.geh(100)
held.geh(100)
held.links(100)
held.code_eingeben(delay_ms=100)
held.geh(100)
held.geh(100)
held.nehme_auf(100)

# Dieser Befehl muss immer am Ende stehen
framework.starten()