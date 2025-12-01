from framework.grundlage import level
level.lade(40, weiblich=True)
from framework.grundlage import *

# Execute movements
held.geh()
held.links()
held.geh()

# Check positions
print(f'held.x (direct): {held.x}')
print(f'held.y (direct): {held.y}')

# Get spielfeld from framework
import framework.grundlage as grundlage
f = grundlage.framework
spielfeld = f.spielfeld

# Check via _get_attribute_value (wie Victory-Check)
print(f'spielfeld._get_attribute_value(held, "x"): {spielfeld._get_attribute_value(held, "x", None)}')
print(f'spielfeld._get_attribute_value(held, "y"): {spielfeld._get_attribute_value(held, "y", None)}')

# Check victory condition manually
print(f'\nVictory check:')
print(f'Target: x=2, y=2')
print(f'Reached: {held.x == 2 and held.y == 2}')
print(f'Framework blocking: {getattr(f, "_aktion_blockiert", False)}')
print(f'check_victory(): {spielfeld.check_victory()}')
