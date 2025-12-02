"""
Shortcut zu run_lsg_tests_gui.py

Startet die GUI zum Testen aller Musterlösungen.
"""

import sys
from pathlib import Path
import tkinter as tk

# Add tests directory to path
tests_dir = Path(__file__).parent / 'tests'
sys.path.insert(0, str(tests_dir))

# Import the GUI class
from run_lsg_tests_gui import RunLsgGui

if __name__ == '__main__':
    root = tk.Tk()
    app = RunLsgGui(root)
    root.mainloop()
