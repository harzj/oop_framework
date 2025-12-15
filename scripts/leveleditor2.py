"""
leveleditor2.py
A redesigned level editor with toolbar and per-tile configuration dialogs.

- Top toolbar with tools (tiles grouped)
- Single click: place/mark tile
- Double click: open a Tk dialog to configure the tile's settings
- Per-tile settings are saved under settings['entities'] keyed by "x,y" and
  also exported in backwards-compatible keys (colors, villagers, quests, codes)

This is intentionally a first iteration focused on structure and compatibility.
"""

import os
import sys
import json
import pygame
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import time
import inspect

# reuse some constants from old editor
TILESIZE = 64
MARGIN = 8
MIN_W, MIN_H = 2, 2

# mapping of toolbar groups -> (code, label, sprite path)
TOOL_DEFS = [
    ("select", "Select", None),
    ("p", "Held/Knappe", "sprites/held.png"),
    ("x", "Monster", "sprites/monster.png"),
    ("y", "Bogenschuetze", "sprites/archer.png"),
    ("k", "Knappe", "sprites/knappe.png"),
    ("h", "Herz", "sprites/herz.png"),
    ("d", "Tuer", "sprites/tuer.png"),
    ("s", "Schluessel", "sprites/key_green.png"),
    ("g", "Tor", "sprites/tor_zu.png"),
    ("c", "Code", "sprites/code.png"),
    ("v", "Villager", "sprites/villager.png"),
]

# helper to ensure pygame initialized for image loading
def _ensure_pygame():
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1,1))


def load_sprite(path, size=None):
    _ensure_pygame()
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size:
                # accept size as int or (w,h)
                if isinstance(size, (list, tuple)) and len(size) == 2:
                    target = (int(size[0]), int(size[1]))
                else:
                    # single number -> square
                    target = (int(size), int(size))
                return pygame.transform.smoothscale(img, target)
            return img
    except Exception:
        pass
    # fallback surface: compute proper width/height
    if isinstance(size, (list, tuple)) and len(size) == 2:
        w, h = int(size[0]), int(size[1])
    elif size:
        w = h = int(size)
    else:
        w = h = TILESIZE
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((120, 120, 120, 60))
    return surf


class LevelEditor2:
    def __init__(self, start_w=8, start_h=6, tilesize=TILESIZE):
        _ensure_pygame()
        pygame.display.set_caption("Level-Editor 2")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)
        self.big = pygame.font.SysFont("consolas", 20, bold=True)

        self.tilesize = tilesize
        self.grid_w = max(MIN_W, start_w)
        self.grid_h = max(MIN_H, start_h)
        self.level = [["w" for _ in range(self.grid_w)] for _ in range(self.grid_h)]

        # settings container (compatibility with old leveleditor)
        self.settings = {}
        self.settings.setdefault('colors', {})
        self.settings.setdefault('villagers', {})
        self.settings.setdefault('quests', {})
        self.settings.setdefault('codes', {})
        # new: per-entity advanced settings
        self.settings.setdefault('entities', {})

        # toolbar
        self.tools = TOOL_DEFS
        self.tool_sprites = {t[0]: (load_sprite(t[2], (32,32)) if t[2] else None) for t in self.tools}
        self.active_tool = 'select'

        # selection/doubleclick tracking
        self.last_click_time = 0
        self.click_interval = 400  # ms for double click detection

        # orientations and per-tile variable exposure
        self.orientations = {}

        # window
        self.panel_h = 80
        self.win_w = max(800, self.grid_w * self.tilesize)
        self.win_h = max(600, self.grid_h * self.tilesize + self.panel_h)
        self.screen = pygame.display.set_mode((self.win_w, self.win_h))

        # load some sprites used for tiles
        self.sprites = {}
        for code, label, path in [(c, l, p) for (c,l,p) in TOOL_DEFS if p]:
            self.sprites[code] = load_sprite(path, (self.tilesize, self.tilesize))
        # fallback for terrain
        self.sprites.setdefault('w', load_sprite('sprites/gras.png', (self.tilesize, self.tilesize)))

    # ------------------ helpers ------------------
    def coord_from_mouse(self, pos):
        mx, my = pos
        # grid origin is offset by MARGIN horizontally and by MARGIN+panel_h vertically
        gx = (mx - MARGIN) // self.tilesize
        gy = (my - MARGIN - self.panel_h) // self.tilesize
        # if click was in the panel area, return None
        if my < self.panel_h + MARGIN:
            return None
        if 0 <= gx < self.grid_w and 0 <= gy < self.grid_h:
            return gx, gy
        return None

    def panel_hit(self, pos):
        x, y = pos
        return y < self.panel_h

    def tool_at_pos(self, pos):
        # compute toolbar item by x position
        x, y = pos
        # two-row toolbar layout: compute number per row
        n = len(self.tools)
        per_row = (n + 1) // 2
        row_h = self.panel_h // 2
        if y >= self.panel_h:
            return None
        row = 0 if y < row_h else 1
        tool_w = max(80, self.win_w // per_row)
        col = int(x // tool_w)
        idx = row * per_row + col
        if 0 <= idx < n:
            return self.tools[idx][0]
        return None

    def set_tile(self, x, y, code):
        # replace and clear any existing entity settings for this coord
        self.level[y][x] = code
        key = f"{x},{y}"
        if key in self.settings.get('entities', {}):
            # if same code, preserve? requirement: replaced => clear
            self.settings['entities'].pop(key, None)
        # keep backwards-compatibility derived fields
        self._sync_entity_to_backcompat(x, y, code)

    def remove_tile(self, x, y):
        self.level[y][x] = 'w'
        key = f"{x},{y}"
        self.settings['entities'].pop(key, None)
        # also remove backcompat entries for colors/villagers/quests/codes as needed
        self._rebuild_backcompat()

    def _sync_entity_to_backcompat(self, x, y, code):
        key = f"{x},{y}"
        ent = self.settings['entities'].get(key, {})
        # colors
        if code.lower() == 'd':
            color = ent.get('color')
            if color:
                self.settings['colors'][key] = color
            else:
                self.settings['colors'].pop(key, None)
        elif code.lower() == 's':
            color = ent.get('color') or 'green'
            self.settings['colors'][key] = color
        else:
            # remove color mapping if tile no longer door/key
            self.settings['colors'].pop(key, None)

        # villagers
        if code.lower() == 'v':
            gender = ent.get('gender')
            if gender:
                self.settings['villagers'][key] = gender
            else:
                self.settings['villagers'].pop(key, None)
        else:
            self.settings['villagers'].pop(key, None)

        # quests
        if code.lower() == 'q':
            qcfg = ent.get('quest', {})
            if qcfg:
                self.settings['quests'][key] = qcfg
        else:
            self.settings['quests'].pop(key, None)

        # codes: if tile is code, store in codes mapping with id
        if code.lower() == 'c':
            cid = ent.get('code_id')
            spell = ent.get('spell')
            if cid and spell:
                self.settings['codes'][cid] = spell

    def _rebuild_backcompat(self):
        # rebuild colors/villagers/quests/codes from entities
        self.settings['colors'].clear()
        self.settings['villagers'].clear()
        self.settings['quests'].clear()
        self.settings['codes'].clear()
        for key, ent in self.settings.get('entities', {}).items():
            # deduce tile from level data
            try:
                x, y = map(int, key.split(','))
                code = self.level[y][x].lower()
            except Exception:
                continue
            if code == 'd' and 'color' in ent:
                self.settings['colors'][key] = ent['color']
            if code == 's' and 'color' in ent:
                self.settings['colors'][key] = ent.get('color', 'green')
            if code == 'v' and 'gender' in ent:
                self.settings['villagers'][key] = ent['gender']
            if code == 'q' and 'quest' in ent:
                self.settings['quests'][key] = ent['quest']
            if code == 'c' and 'code_id' in ent and 'spell' in ent:
                self.settings['codes'][ent['code_id']] = ent['spell']

    # ------------------ drawing ------------------
    def draw(self):
        self.screen.fill((20,20,20))
        # panel
        pygame.draw.rect(self.screen, (40,40,40), (0,0,self.win_w,self.panel_h))
        self._draw_toolbar()
        # grid
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                gx = MARGIN + x * self.tilesize
                gy = MARGIN + y * self.tilesize + self.panel_h
                rect = pygame.Rect(gx, gy, self.tilesize, self.tilesize)
                # base grass
                self.screen.blit(self.sprites.get('w'), (gx, gy))
                code = self.level[y][x]
                if code != 'w':
                    low = code.lower()
                    img = self.sprites.get(low)
                    if img:
                        self.screen.blit(img, (gx, gy))
                    else:
                        pygame.draw.rect(self.screen, (120,120,120), rect)
                # orientation
                key = f"{x},{y}"
                dir = self.orientations.get(key)
                if dir:
                    cx, cy = gx + self.tilesize//2, gy + self.tilesize//2
                    off = self.tilesize//3
                    vecs = {"up":(0,-off),"right":(off,0),"down":(0,off),"left":(-off,0)}
                    dx, dy = vecs.get(dir,(0,off))
                    pygame.draw.line(self.screen,(255,240,0),(cx,cy),(cx+dx,cy+dy),3)
        pygame.display.flip()

    def _draw_toolbar(self):
        n = len(self.tools)
        per_row = (n + 1) // 2
        row_h = self.panel_h // 2
        tool_w = max(80, self.win_w // per_row)
        for i, (code, label, path) in enumerate(self.tools):
            row = i // per_row
            col = i % per_row
            x = col * tool_w
            y = row * row_h
            rect = pygame.Rect(x, y, tool_w, row_h)
            color = (70,70,70) if self.active_tool != code else (100,140,100)
            pygame.draw.rect(self.screen, color, rect)
            # draw sprite if present
            sprite = self.tool_sprites.get(code)
            if sprite:
                self.screen.blit(sprite, (x+8, y+8))
            # draw label
            txt = self.font.render(label, True, (220,220,220))
            self.screen.blit(txt, (x+48, y+8))

    # ------------------ dialogs ------------------
    def open_entity_dialog(self, x, y):
        # get tile code
        code = self.level[y][x]
        key = f"{x},{y}"
        ent = self.settings['entities'].get(key, {})

        # build Tk dialog
        root = tk.Tk()
        root.title(f"Config {code} at {key}")
        frm = ttk.Frame(root, padding=8)
        frm.grid(row=0, column=0)

        row = 0
        ttk.Label(frm, text=f"Tile: {code} @ {key}", font=("Consolas",12,"bold")).grid(row=row,column=0,columnspan=3, sticky='w')
        row += 1

        # Variable exposure
        var_exp = tk.BooleanVar(value=bool(ent.get('expose_var')))
        var_name = tk.StringVar(value=ent.get('var_name',''))
        ttk.Checkbutton(frm, text="Expose as variable", variable=var_exp).grid(row=row,column=0,sticky='w')
        ttk.Entry(frm, textvariable=var_name).grid(row=row,column=1,sticky='w')
        row += 1

        # common: orientation
        ttk.Label(frm, text="Orientation:").grid(row=row,column=0,sticky='w')
        orient_var = tk.StringVar(value=self.orientations.get(key,'down'))
        ttk.Combobox(frm, textvariable=orient_var, values=['up','right','down','left'], width=8).grid(row=row,column=1,sticky='w')
        row += 1

        # entity-specific settings
        if code.lower() == 'p':
            # hero: name and gold
            name_var = tk.StringVar(value=ent.get('name', 'Hero'))
            gold_var = tk.StringVar(value=str(ent.get('gold', 0)))
            ttk.Label(frm, text='Name:').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=name_var).grid(row=row,column=1,sticky='w'); row+=1
            ttk.Label(frm, text='Gold:').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=gold_var).grid(row=row,column=1,sticky='w'); row+=1
        elif code.lower() in ('x','k'):
            # monster/knappe: allow attribute privacy selection (from framework)
            ttk.Label(frm, text='Private attributes (checked = private):').grid(row=row,column=0,sticky='w'); row+=1
            attrs = self._list_framework_attributes_for_code(code)
            attr_vars = {}
            for a in attrs:
                v = tk.BooleanVar(value=(a in ent.get('private_attrs',[])))
                chk = ttk.Checkbutton(frm, text=a, variable=v)
                chk.grid(row=row,column=0,sticky='w'); row+=1
                attr_vars[a]=v
        elif code.lower() == 'd':
            # door: color, randomize, open_by_spell
            color_var = tk.StringVar(value=ent.get('color',''))
            rand_var = tk.BooleanVar(value=bool(ent.get('randomize',False)))
            spell_var = tk.BooleanVar(value=bool(ent.get('spell_opens',False)))
            spell_choice = tk.StringVar(value=ent.get('opens_with',''))
            ttk.Label(frm, text='Color (green/blue/golden/violet/red):').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=color_var).grid(row=row,column=1,sticky='w'); row+=1
            ttk.Checkbutton(frm, text='Randomize color', variable=rand_var).grid(row=row,column=0,sticky='w'); row+=1
            ttk.Checkbutton(frm, text='Opens by spell', variable=spell_var).grid(row=row,column=0,sticky='w');
            # if spell opens selected, choose from existing codes
            ttk.Label(frm, text='Which code id opens (optional):').grid(row=row,column=0,sticky='w')
            codes = list(self.settings.get('codes', {}).keys())
            ttk.Combobox(frm, textvariable=spell_choice, values=codes).grid(row=row,column=1,sticky='w'); row+=1
        elif code.lower() == 's':
            color_var = tk.StringVar(value=ent.get('color','green'))
            rand_var = tk.BooleanVar(value=bool(ent.get('randomize',False)))
            ttk.Label(frm, text='Color:').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=color_var).grid(row=row,column=1,sticky='w'); row+=1
            ttk.Checkbutton(frm, text='Randomize color', variable=rand_var).grid(row=row,column=0,sticky='w'); row+=1
        elif code.lower() == 'g':
            tor_state = tk.StringVar(value=ent.get('state','closed'))
            ttk.Label(frm, text='Initial state (closed/open/random):').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=tor_state).grid(row=row,column=1,sticky='w'); row+=1
        elif code.lower() == 'c':
            # code: custom spell
            cid = ent.get('code_id') or f"code{len(self.settings.get('codes',{})) + 1}"
            spell_var = tk.StringVar(value=ent.get('spell',''))
            id_var = tk.StringVar(value=cid)
            ttk.Label(frm, text='Code id:').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=id_var).grid(row=row,column=1,sticky='w'); row+=1
            ttk.Label(frm, text='Spell (leave empty for auto):').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=spell_var).grid(row=row,column=1,sticky='w'); row+=1
        elif code.lower() == 'v':
            mode_var = tk.StringVar(value=ent.get('villager_mode','items'))
            ttk.Label(frm, text='Villager mode (items/raetsel):').grid(row=row,column=0,sticky='w'); ttk.Entry(frm, textvariable=mode_var).grid(row=row,column=1,sticky='w'); row+=1

        # save / cancel
        def save():
            # common
            ent['expose_var'] = bool(var_exp.get())
            ent['var_name'] = var_name.get().strip() or None
            self.orientations[key] = orient_var.get()

            if code.lower() == 'p':
                ent['name'] = name_var.get()
                try:
                    ent['gold'] = int(gold_var.get())
                except Exception:
                    ent['gold'] = 0
            elif code.lower() in ('x','k'):
                ent['private_attrs'] = [a for a, v in attr_vars.items() if v.get()]
            elif code.lower() == 'd':
                ent['color'] = color_var.get() or None
                ent['randomize'] = bool(rand_var.get())
                ent['spell_opens'] = bool(spell_var.get())
                ent['opens_with'] = spell_choice.get() or None
            elif code.lower() == 's':
                ent['color'] = color_var.get() or 'green'
                ent['randomize'] = bool(rand_var.get())
            elif code.lower() == 'g':
                ent['state'] = tor_state.get()
            elif code.lower() == 'c':
                ent['code_id'] = id_var.get().strip()
                ent['spell'] = spell_var.get().strip() or None
                if ent['code_id']:
                    self.settings.setdefault('codes', {})[ent['code_id']] = ent.get('spell') or ''
            elif code.lower() == 'v':
                ent['villager_mode'] = mode_var.get()

            # variable exposure
            if ent.get('expose_var') and ent.get('var_name'):
                ent['expose_var'] = True
            else:
                ent['expose_var'] = False
                ent['var_name'] = None

            # store entity settings
            self.settings['entities'][key] = ent
            # sync backcompat
            self._sync_entity_to_backcompat(x,y,code)
            root.destroy()

        def cancel():
            root.destroy()

        ttk.Button(frm, text='OK', command=save).grid(row=row, column=0, pady=6)
        ttk.Button(frm, text='Abbrechen', command=cancel).grid(row=row, column=1, pady=6)
        root.mainloop()

    def _list_framework_attributes_for_code(self, code):
        # try to import a corresponding framework class and list public attributes
        mapping = {'k':'Knappe','x':'Monster','y':'Bogenschuetze','p':'Held'}
        clsname = mapping.get(code.lower())
        if not clsname:
            return []
        try:
            mod = __import__('framework.' + clsname.lower(), fromlist=[clsname])
            cls = getattr(mod, clsname)
        except Exception:
            # fallback: import from framework package root
            try:
                mod = __import__('framework', fromlist=[clsname])
                cls = getattr(mod, clsname)
            except Exception:
                return []
        attrs = [a for a in dir(cls) if not a.startswith('_') and not callable(getattr(cls,a, None))]
        # Always include 'typ' as first attribute (standard for all classes)
        if 'typ' not in attrs:
            attrs.insert(0, 'typ')
        elif attrs[0] != 'typ':
            # Move typ to front
            attrs.remove('typ')
            attrs.insert(0, 'typ')
        # include methods optionally
        # methods = [m for m in dir(cls) if callable(getattr(cls,m, None)) and not m.startswith('_')]
        return attrs[:20]  # limit

    # ------------------ IO ------------------
    def to_json(self):
        data = {"tiles": ["".join(row) for row in self.level]}
        # export settings in backwards-compatible form
        data['settings'] = {}
        data['settings'].update(self.settings.get('colors', {}))
        # But we need structured settings: keep both
        data['settings'] = {}
        data['settings']['colors'] = dict(self.settings.get('colors', {}))
        data['settings']['villagers'] = dict(self.settings.get('villagers', {}))
        data['settings']['quests'] = dict(self.settings.get('quests', {}))
        if self.settings.get('codes'):
            data['settings']['codes'] = dict(self.settings.get('codes', {}))
        # store entities advanced settings under entities
        if self.settings.get('entities'):
            data['settings']['entities'] = dict(self.settings.get('entities'))
        # orientations
        if self.orientations:
            data['settings']['orientations'] = dict(self.orientations)
        return data

    def from_json(self, data):
        if 'tiles' not in data:
            raise ValueError("JSON lacks tiles")
        self.grid_h = len(data['tiles'])
        self.grid_w = max(len(r) for r in data['tiles'])
        self.level = [list(r.ljust(self.grid_w, 'w')) for r in data['tiles']]
        s = data.get('settings', {}) or {}
        # load old style color/villager/quests
        self.settings['colors'] = s.get('colors', {}) or {}
        self.settings['villagers'] = s.get('villagers', {}) or {}
        self.settings['quests'] = s.get('quests', {}) or {}
        self.settings['codes'] = s.get('codes', {}) or {}
        self.settings['entities'] = s.get('entities', {}) or {}
        self.orientations = s.get('orientations', {}) or {}
        # ensure sizes
        self._recalc_window()
        self.screen = pygame.display.set_mode((self.win_w, self.win_h))

    def _recalc_window(self):
        self.win_w = max(800, self.grid_w * self.tilesize)
        self.win_h = max(600, self.grid_h * self.tilesize + self.panel_h)

    def resize(self, dx, dy):
        # adjust width
        if dx != 0:
            if dx > 0:
                for row in self.level:
                    row.extend(['w'] * dx)
                self.grid_w += dx
            else:
                if self.grid_w + dx >= MIN_W:
                    for row in self.level:
                        for _ in range(-dx):
                            row.pop()
                    self.grid_w += dx
        # adjust height
        if dy != 0:
            if dy > 0:
                for _ in range(dy):
                    self.level.append(['w'] * self.grid_w)
                self.grid_h += dy
            else:
                if self.grid_h + dy >= MIN_H:
                    for _ in range(-dy):
                        self.level.pop()
                    self.grid_h += dy

        self._recalc_window()
        self.screen = pygame.display.set_mode((self.win_w, self.win_h))

    # ------------------ main loop ------------------
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # toolbar click
                    if self.panel_hit(pos):
                        tool = self.tool_at_pos(pos)
                        if tool:
                            self.active_tool = tool
                        continue
                    coord = self.coord_from_mouse(pos)
                    if coord:
                        x,y = coord
                        now = int(time.time()*1000)
                        if now - self.last_click_time < self.click_interval:
                            # double click
                            self.open_entity_dialog(x,y)
                        else:
                            # single click: according to active tool
                            if self.active_tool == 'select':
                                # mark tile (toggle uppercase)
                                code = self.level[y][x]
                                if code.islower():
                                    self.level[y][x] = code.upper()
                                else:
                                    self.level[y][x] = code.lower()
                            else:
                                self.set_tile(x,y,self.active_tool)
                        self.last_click_time = now
                elif event.type == pygame.MOUSEWHEEL:
                    # rotate orientation of tile under mouse
                    pos = pygame.mouse.get_pos()
                    # Only rotate when mouse is over the grid (not over the toolbar)
                    coord = self.coord_from_mouse(pos)
                    if coord:
                        x,y = coord
                        key = f"{x},{y}"
                        dirs = ['up','right','down','left']
                        cur = self.orientations.get(key,'down')
                        idx = dirs.index(cur) if cur in dirs else 2
                        idx = (idx + (1 if event.y>0 else -1))%4
                        self.orientations[key]=dirs[idx]
                elif event.type == pygame.KEYDOWN:
                    # Save/load
                    if event.key == pygame.K_s:
                        fn = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON Level','*.json')])
                        if fn:
                            with open(fn,'w',encoding='utf-8') as f:
                                json.dump(self.to_json(), f, ensure_ascii=False, indent=2)
                    if event.key == pygame.K_o:
                        fn = filedialog.askopenfilename(filetypes=[('JSON Level','*.json')])
                        if fn:
                            with open(fn,'r',encoding='utf-8') as f:
                                data=json.load(f)
                            self.from_json(data)
                    # Arrow keys: resize grid quickly
                    if event.key == pygame.K_RIGHT:
                        self.resize(+1, 0)
                    elif event.key == pygame.K_LEFT:
                        self.resize(-1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.resize(0, +1)
                    elif event.key == pygame.K_UP:
                        self.resize(0, -1)
            self.draw()
            self.clock.tick(60)
        pygame.quit()


if __name__ == '__main__':
    LevelEditor2().run()
