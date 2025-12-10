from framework.grundlage import level
level.lade(57, weiblich=True)
from framework.grundlage import *
# Level 57 Expected Fail: Held ohne Schwert im Inventar
# Sollte fehlschlagen wegen fehlendem Schwert

# Dieser Befehl muss immer am Ende stehen
framework.starten()
