from framework.grundlage import level
level.lade(40, weiblich=True)
from framework.grundlage import *

# Check if geh method is the wrapped version
geh_method = held.geh
print(f'geh method: {geh_method}')
print(f'geh method name: {geh_method.__name__ if hasattr(geh_method, "__name__") else "N/A"}')

print(f'\nBefore geh():')
print(f'MetaHeld.x: {held.x}')
print(f'MetaHeld.y: {held.y}')
print(f'Student.__x: {held._student.get_x()}')
print(f'Student.__y: {held._student.get_y()}')

held.geh()

print(f'\nAfter geh():')
print(f'MetaHeld.x: {held.x}')
print(f'MetaHeld.y: {held.y}')
print(f'Student.__x: {held._student.get_x()}')
print(f'Student.__y: {held._student.get_y()}')
