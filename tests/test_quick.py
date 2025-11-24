import pygame
pygame.init()
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from framework.spielfeld import Spielfeld

class F:
    weiblich = False
    _aktion_blockiert = False
    def taste_registrieren(self, k, c):
        pass

fw = F()
level37_path = os.path.join(root_dir, 'level', 'level37.json')
sp = Spielfeld(level37_path, fw, feldgroesse=32)
h = sp.held

print(f'Start: ({h.x},{h.y}), direction={h.richtung}')
h.rechts()  # face east
h.geh()     # move to (2,1)
h.rechts()  # face south  
h.geh()     # move to (2,2)
h.geh()     # move to (2,3)
print(f'End: ({h.x},{h.y}), direction={h.richtung}')

v = sp.check_victory()
print(f'Victory: {v}')

if v:
    print('✓ VICTORY TRIGGERED!')
else:
    print('✗ Victory check failed')
    sys.exit(1)
