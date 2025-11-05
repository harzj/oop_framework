import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from leveleditor import LevelEditor
ed = LevelEditor(start_w=6, start_h=6)
# Setup sample like before
ed.level[1][1] = 's'
ed.colors['1,1'] = 'green'
ed.level[2][2] = 'v'
ed.villagers['2,2'] = 'female'
ed.level[1][3] = 'd'
ed.colors['3,1'] = None
ed.level[1][4] = 'd'
ed.colors['4,1'] = 'green'

for y in range(ed.grid_h):
    for x in range(ed.grid_w):
        code = ed.level[y][x]
        if code == 'w':
            continue
        low = code.lower()
        key_coord = f"{x},{y}"
        sprite = None
        if low == 'd':
            col = ed.colors.get(key_coord)
            if col:
                sprite = ed.sprites.get(f"locked_door_{col}")
            else:
                sprite = ed.sprites.get('d')
        elif low == 's':
            col = ed.colors.get(key_coord) or 'green'
            sprite = ed.sprites.get(f"key_{col}")
        elif low == 'v':
            gender = ed.villagers.get(key_coord)
            if isinstance(gender, str) and gender.lower() in ('female','weiblich','w'):
                sprite = ed.sprites.get('v_female')
            else:
                sprite = ed.sprites.get('v')
        else:
            sprite = ed.sprites.get(low)
        print(f"tile {x},{y} code={code} -> sprite key: {sprite}")
