from framework.grundlage import level
level.lade(6,weiblich=False)
from framework.grundlage import *

# Ab hier darfst du programmieren:
held.links(100)

knappe.links(100)
for i in range(2):
    for i in range(3):
        knappe.geh(100)
        knappe.nimm_herz(100)
    knappe.rechts(100)
    held.geh(100)
    held.geh(100)
    held.nimm_herz(100)

# Dieser Befehl muss immer am Ende stehen
framework.starten()