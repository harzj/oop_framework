import json
from leveleditor import LevelEditor
with open('tests/tmp_level_random.json','r',encoding='utf-8') as f:
    d=json.load(f)
le=LevelEditor()
le.from_json(d)
print('editor.level_settings:', le.level_settings)
print('editor.colors:', le.colors)
