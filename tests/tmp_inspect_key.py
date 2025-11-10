from framework.schluessel import Schluessel
try:
    k = Schluessel(1,1)
    print('constructed ok, type:', type(k))
    print('object dict:', object.__getattribute__(k, '__dict__'))
    print('has typ?', 'typ' in object.__getattribute__(k, '__dict__'))
except Exception as e:
    import traceback
    traceback.print_exc()
    print('construction failed:', e)
