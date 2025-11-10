from framework.spielfeld import Spielfeld
s = Spielfeld('tests/tmp_level_random.json', framework=None)
print('spawned objects:')
for o in s.objekte:
    t = getattr(o,'typ', o.__class__.__name__)
    print(' -', t, 'at', getattr(o,'x',None), getattr(o,'y',None), 'farbe/color/key_color:', getattr(o,'farbe', getattr(o,'color', getattr(o,'key_color', None))))
