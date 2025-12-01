from framework.grundlage import level
level.lade(40, weiblich=True)
from framework.grundlage import *

print(f'Held type: {type(held).__name__}')
print(f'Has _student: {hasattr(held, "_student")}')
if hasattr(held, '_student'):
    print(f'Student type: {type(held._student).__name__}')
    print(f'MetaHeld.x before: {held.x}')
    print(f'Student.__x via getter before: {held._student.get_x()}')
    
    held.geh()
    
    print(f'MetaHeld.x after geh: {held.x}')
    print(f'Student.__x via getter after: {held._student.get_x()}')
