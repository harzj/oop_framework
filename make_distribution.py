"""
OOP-Venture Distribution Builder

Erstellt eine Release-ZIP unter dist/.
Die Versionsnummer wird semi-automatisch aus version.json erzeugt.

Dateiname: oopventure_MAJOR_MINOR_PATCH_BUILD.zip

Beispiel-Workflow:
  Aktuelle Version: 1.0.0 Build 0
  (2) Patch   -> oopventure_1_0_1_0.zip
  (3) Feature -> oopventure_1_1_0_0.zip
  (4) Major   -> oopventure_2_0_0_0.zip
  (1) Build   -> oopventure_2_0_0_1.zip
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent
VERSION_FILE = ROOT / "version.json"


def _load_version():
    if VERSION_FILE.exists():
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"major": 1, "minor": 0, "patch": 0, "build": 0}


def _save_version(v):
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(v, f, indent=2)
        f.write('\n')


def _fmt_filename(v):
    """Underscores only – safe for filenames on all OS."""
    return f"{v['major']}_{v['minor']}_{v['patch']}_{v['build']}"


def _fmt_display(v):
    """Human-readable version string."""
    return f"{v['major']}.{v['minor']}.{v['patch']} Build {v['build']}"


def _fmt(v):
    """Kept for internal use (passed to zip builder)."""
    return _fmt_filename(v)


def _bump(v, bump_type):
    v = dict(v)
    if bump_type == 1:    # build only
        v['build'] += 1
    elif bump_type == 2:  # patch  -> reset build
        v['patch'] += 1
        v['build'] = 0
    elif bump_type == 3:  # feature -> reset patch + build
        v['minor'] += 1
        v['patch'] = 0
        v['build'] = 0
    elif bump_type == 4:  # major  -> reset all
        v['major'] += 1
        v['minor'] = 0
        v['patch'] = 0
        v['build'] = 0
    return v


def main():
    scripts_dir = ROOT / 'scripts'
    sys.path.insert(0, str(scripts_dir))
    from make_framework_version_zip import main as build_zip

    v = _load_version()
    from datetime import date
    today = date.today().strftime("%d.%m.%Y")
    print(f"OOPventure Version {_fmt_display(v)} vom {today}")
    print()
    print("Art der Änderung:")
    print(f"  (1) Build    – kleinere Änderungen  ({_fmt_filename(v)} → {_fmt_filename(_bump(v,1))})")
    print(f"  (2) Patch    – Bugfixes             ({_fmt_filename(v)} → {_fmt_filename(_bump(v,2))})")
    print(f"  (3) Feature  – neues Feature        ({_fmt_filename(v)} → {_fmt_filename(_bump(v,3))})")
    print(f"  (4) Major    – Versionssprung       ({_fmt_filename(v)} → {_fmt_filename(_bump(v,4))})")
    print()

    while True:
        choice = input("Wahl [1–4]: ").strip()
        if choice in ('1', '2', '3', '4'):
            break
        print("Bitte eine Zahl zwischen 1 und 4 eingeben.")

    new_v = _bump(v, int(choice))
    from datetime import date
    today = date.today().strftime("%d.%m.%Y")
    print(f"\nNeue Version     : OOPventure Version {_fmt_display(new_v)} vom {today}")
    print(f"Dateiname        : oopventure_{_fmt_filename(new_v)}.zip")
    confirm = input("Bestätigen und ZIP erstellen? [J/n]: ").strip().lower()
    if confirm == 'n':
        print("Abgebrochen.")
        return 1

    _save_version(new_v)
    print(f"version.json aktualisiert -> {_fmt_display(new_v)}\n")

    return build_zip(['make_framework_version_zip.py', _fmt_filename(new_v)])


if __name__ == '__main__':
    sys.exit(main())
