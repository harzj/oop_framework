from framework.grundlage import level
level.lade(341,weiblich=True)
from framework.grundlage import *
# Ab hier darfst du programmieren:
level.objekt_hinzufuegen(Hindernis("Busch",2,0))
level.objekt_hinzufuegen(Hindernis("Berg",0,1))
level.objekt_hinzufuegen(Hindernis("Baum",0,2))
level.objekt_hinzufuegen(Hindernis("Baum",4,3))
level.objekt_hinzufuegen(Monster(2,1,"down"))
level.objekt_hinzufuegen(Herz(2,2))
level.objekt_hinzufuegen(Herz(3,3))
level.objekt_hinzufuegen(Herz(4,4))
s = Schluessel(0,4)
level.objekt_hinzufuegen(s)
s.set_farbe("blue")
level.objekt_hinzufuegen(Tuer(3,4,"blue"))
level.objekt_hinzufuegen(Held(1,2,"down",False))
level.objekt_hinzufuegen(Knappe(3,2,"down"))

# Dieser Befehl muss immer am Ende stehen
framework.starten()

