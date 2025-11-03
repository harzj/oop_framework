from grundlage import level

level.lade(1)
framework = level.framework
held = level.held

# Befehlsliste:
# geh, links, rechts, nehme_auf (für Herzen), attack, was_ist_vor_mir, gib_objekt_vor_dir, ist_auf_herz
# lese_code, code_eingeben

# Ab hier darfst du programmieren:
held.geh()
held.geh()
held.lese_code()
held.geh()
held.links()
held.geh()
held.code_eingeben()
for i in range(4):
    held.geh()
    if held.ist_auf_herz():
        held.nehme_auf()





framework.starten()