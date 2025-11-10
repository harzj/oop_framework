from framework.spielfeld import Spielfeld
s = Spielfeld('tests/tmp_level_key.json', framework=None)
print('spawned:', [(getattr(o,'typ',o.__class__.__name__), getattr(o,'name',None)) for o in s.objekte])
for o in s.objekte:
    if getattr(o,'typ','').lower().startswith('schluessel') or o.__class__.__name__.lower().startswith('schluessel'):
        print('found key attrs:', getattr(o,'color',None), getattr(o,'farbe',None), getattr(o,'sprite_pfad',None))
