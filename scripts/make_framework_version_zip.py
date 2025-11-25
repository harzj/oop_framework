"""
Create a release ZIP containing selected project parts.

Usage:
  - Run interactively: python scripts/make_framework_version_zip.py
    -> it will prompt for a version number
  - Or pass version on command line: python scripts/make_framework_version_zip.py 6

Produces: framework_version_<ver>.zip in the current working directory.
Includes:
 - framework/ folder, but excludes any __pycache__ directories and their contents
 - sprites/ folder completely
 - leveleditor.py and schueler.py
 - from level/ only files matching ^level\d+\.json$
 - pygame library from current environment (bundled for offline use)

"""

import os
import sys
import re
import zipfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_DIR = ROOT / "framework"
LEVEL_DIR = ROOT / "level"
SPRITES_DIR = ROOT / "sprites"
LEVELEDITOR = ROOT / "leveleditor.py"
SCHUELER = ROOT / "schueler.py"
SCHUELER_TEMPLATE = Path(__file__).parent / "schueler_template.py"  # Kanonische Vorlage
README_SCHUELER = ROOT / "README_SCHUELER.md"

LEVEL_FILE_RE = re.compile(r"^level\d+\.json$")


def gather_framework_files(root_dir: Path):
    """Yield (filepath, arcname) for framework folder excluding __pycache__ dirs."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove any __pycache__ dirs from traversal
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fname in filenames:
            # skip .pyc or other compiled files
            if fname.endswith('.pyc'):
                continue
            fpath = Path(dirpath) / fname
            arcname = fpath.relative_to(ROOT)
            yield fpath, str(arcname).replace('\\', '/')


def gather_sprites(root_dir: Path):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            arcname = fpath.relative_to(ROOT)
            yield fpath, str(arcname).replace('\\', '/')


def gather_levels(level_dir: Path):
    if not level_dir.exists():
        return
    for item in sorted(level_dir.iterdir()):
        if item.is_file() and LEVEL_FILE_RE.match(item.name):
            arcname = item.relative_to(ROOT)
            yield item, str(arcname).replace('\\', '/')


def add_file_to_zip(zf: zipfile.ZipFile, filepath: Path, arcname: str):
    zf.write(filepath, arcname)
    print(f"Added: {arcname}")


def gather_pygame_library():
    """Find and gather pygame library files from site-packages."""
    try:
        import pygame
        pygame_path = Path(pygame.__file__).parent
        
        # Yield all pygame files
        for dirpath, dirnames, filenames in os.walk(pygame_path):
            # Skip __pycache__ and tests
            dirnames[:] = [d for d in dirnames if d not in ('__pycache__', 'tests', 'docs')]
            
            for fname in filenames:
                # Skip .pyc files and test files
                if fname.endswith('.pyc') or fname.startswith('test_'):
                    continue
                    
                fpath = Path(dirpath) / fname
                # Create archive name: lib/pygame/...
                rel_path = fpath.relative_to(pygame_path.parent)
                arcname = f"lib/{rel_path}"
                yield fpath, str(arcname).replace('\\', '/')
                
        # Also include pygame metadata (for version info, etc.)
        site_packages = pygame_path.parent
        for item in site_packages.glob('pygame-*.dist-info'):
            if item.is_dir():
                for fpath in item.rglob('*'):
                    if fpath.is_file() and not fpath.name.endswith('.pyc'):
                        rel_path = fpath.relative_to(site_packages)
                        arcname = f"lib/{rel_path}"
                        yield fpath, str(arcname).replace('\\', '/')
                        
    except ImportError:
        print("Warnung: pygame nicht installiert. Wird übersprungen.")
        return


def main(argv):
    if len(argv) >= 2:
        version = argv[1]
    else:
        version = input("Versionsnummer (z.B. 6): ").strip()

    if not version:
        print("Keine Versionsnummer angegeben. Abbruch.")
        return 2

    zipname = f"framework_version_{version}.zip"
    zip_path = Path.cwd() / zipname
    if zip_path.exists():
        ans = input(f"{zipname} existiert bereits. Überschreiben? [j/N]: ").strip().lower()
        if ans not in ('j', 'y'):
            print("Abgebrochen.")
            return 1

    print(f"Erstelle {zip_path} ...")

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # framework folder (walk, exclude __pycache__)
        if FRAMEWORK_DIR.exists():
            for fpath, arc in gather_framework_files(FRAMEWORK_DIR):
                add_file_to_zip(zf, fpath, arc)
        else:
            print("Warnung: framework/ Verzeichnis nicht gefunden.")

        # sprites folder (full)
        if SPRITES_DIR.exists():
            for fpath, arc in gather_sprites(SPRITES_DIR):
                add_file_to_zip(zf, fpath, arc)
        else:
            print("Warnung: sprites/ Verzeichnis nicht gefunden.")

        # leveleditor.py and schueler.py
        if LEVELEDITOR.exists():
            add_file_to_zip(zf, LEVELEDITOR, str(LEVELEDITOR.relative_to(ROOT)).replace('\\', '/'))
        else:
            print("Warnung: leveleditor.py nicht gefunden.")

        # Verwende immer die kanonische Template-Datei, um sicherzustellen,
        # dass eine saubere schueler.py in der Distribution enthalten ist
        if SCHUELER_TEMPLATE.exists():
            add_file_to_zip(zf, SCHUELER_TEMPLATE, 'schueler.py')
            print("OK: schueler.py (aus Template)")
        elif SCHUELER.exists():
            add_file_to_zip(zf, SCHUELER, str(SCHUELER.relative_to(ROOT)).replace('\\', '/'))
            print("Warnung: schueler_template.py nicht gefunden, verwende aktuelle schueler.py")
        else:
            print("Warnung: schueler.py nicht gefunden.")
        
        # README for students
        if README_SCHUELER.exists():
            add_file_to_zip(zf, README_SCHUELER, str(README_SCHUELER.relative_to(ROOT)).replace('\\', '/'))
        else:
            print("Warnung: README_SCHUELER.md nicht gefunden.")

        # level JSON files matching level<digits>.json
        for fpath, arc in gather_levels(LEVEL_DIR):
            add_file_to_zip(zf, fpath, arc)
        
        # klassen/ folder (empty directory structure for student classes)
        zf.writestr('klassen/__init__.py', '')
        print("OK: leerer klassen/ Ordner erstellt")
        
        # pygame library (bundled)
        print("\nBündle pygame Bibliothek...")
        pygame_count = 0
        for fpath, arc in gather_pygame_library():
            add_file_to_zip(zf, fpath, arc)
            pygame_count += 1
        if pygame_count > 0:
            print(f"✓ {pygame_count} pygame Dateien hinzugefügt")

    print(f"\nFertig: {zip_path}")
    print(f"\nHinweis: pygame ist im 'lib/' Ordner enthalten.")
    print(f"Die Schüler müssen pygame nicht mehr separat installieren!")
    return 0


if __name__ == '__main__':
    rc = main(sys.argv)
    sys.exit(rc)
