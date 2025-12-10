from framework.grundlage import level
level.lade(56, weiblich=True)
from framework.grundlage import *
# Level 56 Expected Fail: Gegenstand ohne 'art' Attribut
# Sollte fehlschlagen wegen fehlendem Attribut

# Dieser Befehl muss immer am Ende stehen
framework.starten()
