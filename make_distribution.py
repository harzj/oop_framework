"""
Shortcut zu make_framework_version_zip.py

Erstellt eine Distribution im dist/ Verzeichnis.
Inkludiert README_SCHUELER.md aus docs/ Verzeichnis.

Usage:
  python make_distribution.py         -> Interaktive Eingabe der Versionsnummer
  python make_distribution.py 9       -> Erstellt framework_version_9.zip
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

# Import and run
from make_framework_version_zip import main

if __name__ == '__main__':
    sys.exit(main(sys.argv))
