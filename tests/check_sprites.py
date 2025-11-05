import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from leveleditor import LevelEditor
ed = LevelEditor(start_w=2, start_h=2)
needed = ["key_green","key_red","locked_door_green","locked_door_blue","v","v_female"]
for k in needed:
    print(k, 'in sprites:', k in ed.sprites, 'object:', type(ed.sprites.get(k)))
