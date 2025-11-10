from framework.objekt import Objekt
o = Objekt('Test')
print('obj dict:', object.__getattribute__(o,'__dict__'))
print('has typ?', 'typ' in object.__getattribute__(o,'__dict__'))
