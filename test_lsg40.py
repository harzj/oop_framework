from framework.grundlage import level
level.lade(40, weiblich=True)
from framework.grundlage import *

print(f'Start: x={held.x}, y={held.y}, richtung={held.richtung}')
held.geh()
print(f'Nach geh(): x={held.x}, y={held.y}')
held.links()
print(f'Nach links(): richtung={held.richtung}')
held.geh()
print(f'Nach geh(): x={held.x}, y={held.y}')
print(f'\nZiel: x=2, y=2')
print(f'Erreicht: {held.x == 2 and held.y == 2}')
