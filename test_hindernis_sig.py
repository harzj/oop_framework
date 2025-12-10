import sys
sys.path.insert(0, 'klassen')

from hindernis import Hindernis as HindernisCorrect
from hindernis_50_missing_x import Hindernis as HindernisBroken

print("Testing correct Hindernis(0, 0, 'Baum'):")
obj1 = HindernisCorrect(0, 0, 'Baum')
print(f"  __dict__: {obj1.__dict__}")
print(f"  hasattr(obj1, 'x'): {hasattr(obj1, 'x')}")

print("\nTesting broken Hindernis(0, 0, 'Baum'):")
try:
    obj2 = HindernisBroken(0, 0, 'Baum')
    print(f"  __dict__: {obj2.__dict__}")
    print(f"  hasattr(obj2, 'x'): {hasattr(obj2, 'x')}")
except TypeError as e:
    print(f"  TypeError: {e}")
