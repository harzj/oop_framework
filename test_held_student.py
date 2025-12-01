from framework.grundlage import level
level.lade(40, weiblich=True)
from framework.grundlage import *

print(f'Student.__x via getter before: {held._student.get_x()}')
print(f'Student.__y via getter before: {held._student.get_y()}')
print(f'Student.__richtung via getter before: {held._student.get_richtung()}')

# Call method directly on student
held._student.geh()

print(f'Student.__x via getter after: {held._student.get_x()}')
print(f'Student.__y via getter after: {held._student.get_y()}')
print(f'Student.__richtung via getter after: {held._student.get_richtung()}')
