import os, sys
import pygame
# ensure project root on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from leveleditor import LevelEditor
import time

# Initialize editor
ed = LevelEditor(start_w=6, start_h=6)
# Place a key at (1,1) and villager at (2,2)
ed.level[1][1] = 's'
ed.colors['1,1'] = 'green'
ed.level[2][2] = 'v'
ed.villagers['2,2'] = 'female'
# Also place a normal door at (3,1) and a colored door at (4,1)
ed.level[1][3] = 'd'
ed.colors['3,1'] = None
ed.level[1][4] = 'd'
ed.colors['4,1'] = 'green'

# Recompute window & draw one frame
ed._recalc_window()
ed.screen = pygame.display.set_mode((ed.win_w, ed.win_h))
ed.draw()
# Save screenshot to inspect
pygame.image.save(ed.screen, 'tests/editor_test_out.png')
print('Saved tests/editor_test_out.png')
pygame.quit()
