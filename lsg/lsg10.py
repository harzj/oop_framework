from framework.grundlage import level
level.lade(10,weiblich=False)
from framework.grundlage import *

# Ab hier darfst du programmieren:
for i in range(10):
    held.geh(100)
    if held.ist_auf_herz():
        held.nimm_herz(100)
        held.links(100)
for i in range(4):
    knappe.geh(100)
    if knappe.ist_auf_herz():
        knappe.nimm_herz(100)

# Dieser Befehl muss immer am Ende stehen
framework.starten()