from framework.grundlage import level
level.lade(24,weiblich=True)
from framework.grundlage import *

# Ab hier darfst du programmieren:
knappe.y = 5
held.x = 4
for i in range(2):
    held.geh(100)
    held.nimm_herz(100)
    knappe.geh(100)
    knappe.nimm_herz(100)
# Dieser Befehl muss immer am Ende stehen
framework.starten()