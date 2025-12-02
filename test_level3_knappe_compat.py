import pygame
pygame.init()

from framework.framework import Framework

fw = Framework('3')
print('Level 3 loaded')
print('Knappe exists:', fw.spielfeld.knappe is not None)
if fw.spielfeld.knappe:
    print('Knappe position:', fw.spielfeld.knappe.x, fw.spielfeld.knappe.y)
    print('Knappe name:', fw.spielfeld.knappe.name)
    
pygame.quit()
print('✓ Level 3 OK')
