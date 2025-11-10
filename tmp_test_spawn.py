import traceback
from framework.spielfeld import Spielfeld

print('creating Spielfeld for v/items...')
s = Spielfeld('tmp_level_v_items.json', framework=None, auto_erzeuge_objekte=True)
print('spawned objects (v/items):', [ (getattr(o,'typ', o.__class__.__name__), getattr(o,'name',None)) for o in s.objekte ])
for o in s.objekte:
    if getattr(o,'typ', '').lower() == 'villager' or o.__class__.__name__.lower()=='villager':
        try:
            offers = getattr(o, 'angebote', None)
            print('villager offers count:', len(offers) if offers is not None else 'no offers attr')
        except Exception:
            traceback.print_exc()

print('\ncreating Spielfeld for q/raetsel...')
s2 = Spielfeld('tmp_level_q_raetsel.json', framework=None, auto_erzeuge_objekte=True)
print('spawned objects (q/raetsel):', [ (getattr(o,'typ', o.__class__.__name__), getattr(o,'name',None)) for o in s2.objekte ])
for o in s2.objekte:
    if getattr(o,'typ','').lower()=='questgeber' or o.__class__.__name__.lower()=='questgeber':
        print('questgeber attrs: _vorgegebene_frage=', getattr(o,'_vorgegebene_frage',None), '_letzte_raetsel=', getattr(o,'_letzte_raetsel',None))
