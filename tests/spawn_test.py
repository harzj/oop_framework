import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from framework.spielfeld import Spielfeld
import pygame

# create a temporary level json
level = {
    "tiles": [
        "wwwwww",
        "wsdwww",
        "wvwwww",
        "wwdwww",
        "wwwwww",
    ],
    "settings": {
        "colors": {"2,1": "green", "4,1": "green"},
        "villagers": {"1,2": "female"}
    }
}
path = 'tests/tmp_level.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(level, f, ensure_ascii=False, indent=2)

pygame.init()
# instantiate Spielfeld
from framework import framework as fw_mod
spielfeld = Spielfeld(path, fw_mod, feldgroesse=64, auto_erzeuge_objekte=True)
# create screen
screen = pygame.display.set_mode((spielfeld.level.breite*64, spielfeld.level.hoehe*64))
spielfeld.zeichne(screen)
pygame.image.save(screen, 'tests/spawn_test_out.png')
print('Saved tests/spawn_test_out.png')
pygame.quit()
