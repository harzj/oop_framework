import os
import sys
import glob
import threading
import subprocess
import time
import queue
import tkinter as tk
from tkinter import ttk
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LSG_DIR = os.path.join(ROOT, "lsg")
TESTS_DIR = os.path.join(ROOT, "tests")

pyexe = sys.executable


class RunLsgGui:
    def __init__(self, master):
        self.master = master
        master.title("run_lsg_tests GUI")
        master.geometry("900x600")

        self.files = sorted(glob.glob(os.path.join(LSG_DIR, "lsg*.py")))
        if not self.files:
            tk.messagebox.showerror("Fehler", "Keine lsg/*.py Dateien gefunden.")
            master.destroy()
            return

        self.selected = {}
        self.check_vars = {}
        
        # Logging setup
        self.log_file = None
        self.log_path = None

        # Top frame: file list and controls
        top = ttk.Frame(master)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=6, pady=6)

        left = ttk.Frame(top)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollable checkbox list
        canvas = tk.Canvas(left)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        self.list_frame = ttk.Frame(canvas)

        self.list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.list_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate checkboxes
        for path in self.files:
            name = os.path.basename(path)
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.list_frame, text=name, variable=var)
            cb.pack(anchor='w', padx=4, pady=2)
            self.check_vars[name] = var

        # Right controls
        right = ttk.Frame(top)
        right.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=6)

        ttk.Label(right, text="Delay (ms, -1 to keep scripts'):").pack(anchor='w', pady=(4,2))
        self.delay_var = tk.StringVar(value=os.getenv("RUN_LSG_DELAY_MS", "0"))
        self.delay_entry = ttk.Entry(right, textvariable=self.delay_var, width=12)
        self.delay_entry.pack(anchor='w')

        ttk.Label(right, text="Timeout (secs, 0=unlimited):").pack(anchor='w', pady=(8,2))
        self.timeout_var = tk.StringVar(value=os.getenv("RUN_LSG_TIMEOUT_SECS", "3"))
        self.timeout_entry = ttk.Entry(right, textvariable=self.timeout_var, width=12)
        self.timeout_entry.pack(anchor='w')

        btn_frame = ttk.Frame(right)
        btn_frame.pack(anchor='w', pady=8)

        self.all_btn = ttk.Button(btn_frame, text="Alle", command=self.select_all)
        self.all_btn.pack(side=tk.LEFT, padx=2)
        self.none_btn = ttk.Button(btn_frame, text="Keine", command=self.select_none)
        self.none_btn.pack(side=tk.LEFT, padx=2)

        # Phase selection buttons
        phase_frame = ttk.Frame(right)
        phase_frame.pack(anchor='w', pady=4)
        
        self.phase1_btn = ttk.Button(phase_frame, text="Phase 1", command=self.select_phase1)
        self.phase1_btn.pack(side=tk.LEFT, padx=2)
        self.phase2_btn = ttk.Button(phase_frame, text="Phase 2", command=self.select_phase2)
        self.phase2_btn.pack(side=tk.LEFT, padx=2)

        # Filter dropdown
        ttk.Label(right, text="Filter:").pack(anchor='w', pady=(8,2))
        self.filter_var = tk.StringVar(value="alle")
        self.filter_combo = ttk.Combobox(right, textvariable=self.filter_var, 
                                         values=["alle", "nur erfolg", "nur fail"],
                                         state="readonly", width=12)
        self.filter_combo.pack(anchor='w')
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_filter)

        self.run_btn = ttk.Button(right, text="Run", command=self.start_run)
        self.run_btn.pack(fill=tk.X, pady=(10,2))

        self.stop_btn = ttk.Button(right, text="Stop", command=self.stop_run, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)

        # Text output
        out_frame = ttk.Frame(master)
        out_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=(0,6))
        self.text = tk.Text(out_frame, wrap='none')
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        out_scroll = ttk.Scrollbar(out_frame, orient='vertical', command=self.text.yview)
        out_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=out_scroll.set)

        # Queue and threading
        self.queue = queue.Queue()
        self.worker_thread = None
        self._stop_event = threading.Event()

        # Poll queue periodically
        self.master.after(100, self._poll_queue)

    def select_all(self):
        for v in self.check_vars.values():
            v.set(True)

    def select_none(self):
        for v in self.check_vars.values():
            v.set(False)
    
    def select_phase1(self):
        """Select Phase 1 tests (Level 0-34)"""
        for name, v in self.check_vars.items():
            # Extract level number from filename
            if self._is_phase1(name):
                v.set(True)
            else:
                v.set(False)
    
    def select_phase2(self):
        """Select Phase 2 tests (Level 35+)"""
        for name, v in self.check_vars.items():
            # Extract level number from filename
            if not self._is_phase1(name):
                v.set(True)
            else:
                v.set(False)
    
    def _is_phase1(self, filename):
        """Check if filename is a Phase 1 test (Level 0-34)"""
        import re
        # Extract level number from filename like lsg1.py, lsg10.py, etc.
        match = re.search(r'lsg(\d+)', filename)
        if match:
            level_num = int(match.group(1))
            return 0 <= level_num <= 34
        return False
    
    def apply_filter(self, event=None):
        """Apply filter based on expected outcome"""
        filter_val = self.filter_var.get()
        
        for name, v in self.check_vars.items():
            if filter_val == "alle":
                # Show all (don't change selection)
                pass
            elif filter_val == "nur erfolg":
                # Show only tests expected to succeed
                expected_fail = "expected_fail" in name
                if expected_fail:
                    v.set(False)
            elif filter_val == "nur fail":
                # Show only tests expected to fail
                expected_fail = "expected_fail" in name
                if not expected_fail:
                    v.set(False)

    def start_run(self):
        selected_files = [os.path.join(LSG_DIR, n) for n, v in self.check_vars.items() if v.get()]
        if not selected_files:
            self._append_text("Keine Dateien ausgewählt.\n")
            return

        # parse delay
        try:
            delay = int(self.delay_var.get())
        except Exception:
            self._append_text("Ungültiger Delay-Wert, bitte Ganzzahl eingeben.\n")
            return
        
        # parse timeout
        try:
            timeout = int(self.timeout_var.get())
        except Exception:
            self._append_text("Ungültiger Timeout-Wert, bitte Ganzzahl eingeben.\n")
            return

        # Open log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(TESTS_DIR, f"run_lsg_tests_{timestamp}.log")
        try:
            self.log_file = open(self.log_path, 'w', encoding='utf-8')
            self._append_text(f"Logging to: {self.log_path}\n")
            self._log(f"=== Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            self._log(f"Selected files: {len(selected_files)}\n")
            self._log(f"Delay: {delay}ms, Timeout: {timeout}s\n\n")
        except Exception as e:
            self._append_text(f"[WARNING] Could not create log file: {e}\n")
            self.log_file = None
        
        # disable UI controls while running
        self.run_btn.config(state=tk.DISABLED)
        self.all_btn.config(state=tk.DISABLED)
        self.none_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        for cb in self.list_frame.winfo_children():
            cb.config(state=tk.DISABLED)
        self._stop_event.clear()

        # start background thread
        self.worker_thread = threading.Thread(target=self._run_worker, args=(selected_files, delay, timeout), daemon=True)
        self.worker_thread.start()

    def stop_run(self):
        # signal worker to stop; it will attempt to terminate current subprocess
        self._stop_event.set()
        self._append_text("Stop requested. Trying to terminate running tests...\n")

    def _run_worker(self, files, delay_ms, timeout_secs):
        results = []
        try:
            self._run_worker_impl(files, delay_ms, timeout_secs, results)
        except KeyboardInterrupt:
            msg = "\n[ERROR] Test run interrupted by user (KeyboardInterrupt)\n"
            self.queue.put(msg)
            self._log(msg)
        except Exception as e:
            msg = f"\n[ERROR] Test run crashed with exception: {e}\n"
            self.queue.put(msg)
            self._log(msg)
            import traceback
            tb = traceback.format_exc()
            self.queue.put(tb)
            self._log(tb)
        finally:
            # Close log file
            if self.log_file:
                self._log(f"\n=== Test Run Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                try:
                    self.log_file.close()
                except Exception:
                    pass
                self.log_file = None
            
            self.queue.put("\n[run finished]\n")
            self.queue.put("__RUN_FINISHED__")
    
    def _run_worker_impl(self, files, delay_ms, timeout_secs, results):
        for path in files:
            if self._stop_event.is_set():
                stop_msg = "\n[STOPPED] Test run stopped by user\n"
                self.queue.put(stop_msg)
                self._log(stop_msg)
                break
            name = os.path.basename(path)
            msg = f"\n=== Running {name} ===\n"
            self.queue.put(msg)
            self._log(msg)
            
            # For lsg35.py, lsg36.py, lsg37.py: backup schueler.py and extract class from lsg file
            # For lsg38.py: backup klassen/held.py and replace with held_lsg_37.py
            # For lsg31.py: backup framework/held.py and activate setze_position (if False -> if True)
            # For lsg40*.py: backup klassen/held.py and replace with appropriate held_variant_*.py
            schueler_path = os.path.join(ROOT, "schueler.py")
            held_klassen_path = os.path.join(ROOT, "klassen", "held.py")
            hindernis_klassen_path = os.path.join(ROOT, "klassen", "hindernis.py")
            zettel_klassen_path = os.path.join(ROOT, "klassen", "zettel.py")
            spielobjekt_klassen_path = os.path.join(ROOT, "klassen", "spielobjekt.py")
            held_framework_path = os.path.join(ROOT, "framework", "held.py")
            schueler_backup = None
            held_backup = None
            hindernis_backup = None
            zettel_backup = None
            spielobjekt_backup = None
            framework_held_backup = None
            inventar_backup = None
            gegenstand_backup = None
            knappe_backup = None
            needs_schueler_replacement = name in ["lsg35.py", "lsg36.py", "lsg37.py"]
            needs_level35_held_replacement = name in ["lsg35.py", "lsg36.py", "lsg37.py"]
            needs_held_replacement = name == "lsg38.py"
            needs_framework_held_modification = name == "lsg31.py"
            needs_level39_held_replacement = name.startswith("lsg39")
            needs_level40_held_replacement = name.startswith("lsg40")
            needs_level41_held_replacement = name.startswith("lsg41")
            needs_level42_held_replacement = name.startswith("lsg42")
            needs_level43_held_replacement = name.startswith("lsg43")
            needs_level44_hindernis_replacement = name.startswith("lsg44")
            needs_level45_zettel_replacement = name.startswith("lsg45")
            needs_level50_replacement = name.startswith("lsg50")
            needs_level56_replacement = name.startswith("lsg56")
            needs_level57_replacement = name.startswith("lsg57")
            
            if needs_schueler_replacement:
                try:
                    # Backup existing schueler.py
                    if os.path.exists(schueler_path):
                        with open(schueler_path, 'r', encoding='utf-8') as f:
                            schueler_backup = f.read()
                    
                    # Extract Held class from lsg file
                    with open(path, 'r', encoding='utf-8') as f:
                        lsg_content = f.read()
                    
                    # Find the class definition in lsg file (between imports and framework.starten())
                    import_end = lsg_content.find("# Ab hier darfst du programmieren:")
                    starten_start = lsg_content.find("# Dieser Befehl muss immer am Ende stehen")
                    
                    if import_end != -1 and starten_start != -1:
                        class_code = lsg_content[import_end:starten_start].strip()
                        # Write to schueler.py
                        with open(schueler_path, 'w', encoding='utf-8') as f:
                            f.write(class_code + "\n")
                        self._log_and_queue(f"[info] Extracted Held class to schueler.py for {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not extract class for {name}: {e}\n")
            
            # Level 35-37: Replace klassen/held.py with simple version (no Charakter inheritance)
            if needs_level35_held_replacement:
                try:
                    # Backup existing klassen/held.py
                    if os.path.exists(held_klassen_path):
                        with open(held_klassen_path, 'r', encoding='utf-8') as f:
                            held_backup = f.read()
                    
                    # Copy held_35.py to klassen/held.py
                    held_35_path = os.path.join(ROOT, "klassen", "held_35.py")
                    if os.path.exists(held_35_path):
                        with open(held_35_path, 'r', encoding='utf-8') as f:
                            held_35_content = f.read()
                        with open(held_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(held_35_content)
                        self._log_and_queue(f"[info] Copied held_35.py to klassen/held.py for {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace held.py for {name}: {e}\n")
            
            if needs_held_replacement:
                try:
                    # Backup existing klassen/held.py
                    if os.path.exists(held_klassen_path):
                        with open(held_klassen_path, 'r', encoding='utf-8') as f:
                            held_backup = f.read()
                    
                    # Copy held_lsg_38.py to klassen/held.py
                    held_lsg_path = os.path.join(ROOT, "lsg", "held_lsg_38.py")
                    if os.path.exists(held_lsg_path):
                        with open(held_lsg_path, 'r', encoding='utf-8') as f:
                            held_lsg_content = f.read()
                        with open(held_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(held_lsg_content)
                        self._log_and_queue(f"[info] Copied held_lsg_38.py to klassen/held.py for {name}\n")
                    else:
                        self._log_and_queue(f"[warning] held_lsg_38.py not found\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace klassen/held.py for {name}: {e}\n")
            
            if needs_framework_held_modification:
                try:
                    import re
                    # Backup existing framework/held.py
                    if os.path.exists(held_framework_path):
                        with open(held_framework_path, 'r', encoding='utf-8') as f:
                            framework_held_backup = f.read()
                        
                        # Modify setze_position: if False -> if True
                        pattern = r'(def setze_position\s*\([^)]*\):\s*[^\n]*\n(?:[^\n]*\n)*?\s*)if False:'
                        modified_content = re.sub(pattern, r'\1if True:', framework_held_backup)
                        
                        # Write modified content
                        with open(held_framework_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        self._log_and_queue(f"[info] Activated setze_position in framework/held.py for {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not modify framework/held.py for {name}: {e}\n")
            
            if needs_level39_held_replacement:
                try:
                    # Backup existing klassen/held.py
                    if os.path.exists(held_klassen_path):
                        with open(held_klassen_path, 'r', encoding='utf-8') as f:
                            held_backup = f.read()
                    
                    # Copy held_38.py to klassen/held.py (Level 39 uses public attributes like Level 38)
                    held_38_path = os.path.join(ROOT, "klassen", "held_38.py")
                    if os.path.exists(held_38_path):
                        with open(held_38_path, 'r', encoding='utf-8') as f:
                            held_38_content = f.read()
                        with open(held_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(held_38_content)
                        self._log_and_queue(f"[info] Copied held_38.py to klassen/held.py for {name}\n")
                    else:
                        self._log_and_queue(f"[warning] held_38.py not found\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace klassen/held.py for {name}: {e}\n")
            
            if needs_level40_held_replacement:
                try:
                    # Backup existing klassen/held.py
                    if os.path.exists(held_klassen_path):
                        with open(held_klassen_path, 'r', encoding='utf-8') as f:
                            held_backup = f.read()
                    
                    # Determine which variant to use based on test name
                    variant_name = "correct"  # default for lsg40.py
                    if "public_attributes" in name:
                        variant_name = "public_attributes"
                    elif "missing_getters" in name:
                        variant_name = "missing_getters"
                    elif "missing_setters" in name:
                        variant_name = "missing_setters"
                    
                    # Copy appropriate held_variant_*.py to klassen/held.py
                    held_variant_path = os.path.join(ROOT, "lsg", f"held_variant_{variant_name}.py")
                    if os.path.exists(held_variant_path):
                        with open(held_variant_path, 'r', encoding='utf-8') as f:
                            held_variant_content = f.read()
                        with open(held_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(held_variant_content)
                        self._log_and_queue(f"[info] Copied held_variant_{variant_name}.py to klassen/held.py for {name}\n")
                    else:
                        self._log_and_queue(f"[warning] held_variant_{variant_name}.py not found\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace klassen/held.py for {name}: {e}\n")
            
            if needs_level41_held_replacement or needs_level42_held_replacement or needs_level43_held_replacement:
                try:
                    # Backup existing klassen/held.py
                    if os.path.exists(held_klassen_path):
                        with open(held_klassen_path, 'r', encoding='utf-8') as f:
                            held_backup = f.read()
                    
                    # Check if this is an expected_fail variant test
                    if "expected_fail" in name:
                        # Use variant files for expected_fail tests
                        variant_name = "correct"  # default
                        if "public_attributes" in name:
                            variant_name = "public_attributes"
                        elif "missing_getters" in name:
                            variant_name = "missing_getters"
                        elif "missing_setters" in name:
                            variant_name = "missing_setters"
                        
                        held_variant_path = os.path.join(ROOT, "lsg", f"held_variant_{variant_name}.py")
                        if os.path.exists(held_variant_path):
                            with open(held_variant_path, 'r', encoding='utf-8') as f:
                                held_variant_content = f.read()
                            with open(held_klassen_path, 'w', encoding='utf-8') as f:
                                f.write(held_variant_content)
                            self._log_and_queue(f"[info] Copied held_variant_{variant_name}.py to klassen/held.py for {name}\n")
                        else:
                            self._log_and_queue(f"[warning] held_variant_{variant_name}.py not found\n")
                    else:
                        # For normal level 41-43 tests, use held_lsg_XX.py files
                        # Extract just the level number (41, 42, or 43)
                        level_num = name.replace("lsg", "").replace(".py", "").split("_")[0]
                        held_lsg_path = os.path.join(ROOT, "lsg", f"held_lsg{level_num}.py")
                        if os.path.exists(held_lsg_path):
                            with open(held_lsg_path, 'r', encoding='utf-8') as f:
                                held_lsg_content = f.read()
                            with open(held_klassen_path, 'w', encoding='utf-8') as f:
                                f.write(held_lsg_content)
                            self._log_and_queue(f"[info] Copied held_lsg{level_num}.py to klassen/held.py for {name}\n")
                        else:
                            self._log_and_queue(f"[warning] held_lsg{level_num}.py not found\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace klassen/held.py for {name}: {e}\n")
            
            if needs_level44_hindernis_replacement:
                try:
                    # Backup existing klassen/hindernis.py
                    if os.path.exists(hindernis_klassen_path):
                        with open(hindernis_klassen_path, 'r', encoding='utf-8') as f:
                            hindernis_backup = f.read()
                    
                    # Copy hindernis_correct.py to klassen/hindernis.py
                    hindernis_correct_path = os.path.join(ROOT, "klassen", "hindernis_correct.py")
                    if os.path.exists(hindernis_correct_path):
                        with open(hindernis_correct_path, 'r', encoding='utf-8') as f:
                            hindernis_content = f.read()
                        with open(hindernis_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(hindernis_content)
                        self._log_and_queue(f"[info] Copied hindernis_correct.py to klassen/hindernis.py for {name}\n")
                    else:
                        self._log_and_queue(f"[warning] hindernis_correct.py not found\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace klassen/hindernis.py for {name}: {e}\n")
            
            if needs_level45_zettel_replacement:
                try:
                    # Backup existing klassen/zettel.py
                    if os.path.exists(zettel_klassen_path):
                        with open(zettel_klassen_path, 'r', encoding='utf-8') as f:
                            zettel_backup = f.read()
                    
                    # Copy zettel_correct.py to klassen/zettel.py
                    zettel_correct_path = os.path.join(ROOT, "klassen", "zettel_correct.py")
                    if os.path.exists(zettel_correct_path):
                        with open(zettel_correct_path, 'r', encoding='utf-8') as f:
                            zettel_content = f.read()
                        with open(zettel_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(zettel_content)
                        self._log_and_queue(f"[info] Copied zettel_correct.py to klassen/zettel.py for {name}\n")
                    else:
                        self._log_and_queue(f"[warning] zettel_correct.py not found\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace klassen/zettel.py for {name}: {e}\n")
            
            if needs_level50_replacement:
                try:
                    # Backup existing klassen files
                    if os.path.exists(spielobjekt_klassen_path):
                        with open(spielobjekt_klassen_path, 'r', encoding='utf-8') as f:
                            spielobjekt_backup = f.read()
                    if os.path.exists(hindernis_klassen_path):
                        with open(hindernis_klassen_path, 'r', encoding='utf-8') as f:
                            hindernis_backup = f.read()
                    if os.path.exists(zettel_klassen_path):
                        with open(zettel_klassen_path, 'r', encoding='utf-8') as f:
                            zettel_backup = f.read()
                    
                    # Determine which variant to use based on test name
                    if "zettel49" in name:
                        # Use zettel_49 (private attrs) - should fail
                        zettel_variant_path = os.path.join(ROOT, "klassen", "zettel_49.py")
                        hindernis_variant_path = os.path.join(ROOT, "klassen", "hindernis_50.py")
                        spielobjekt_variant_path = os.path.join(ROOT, "klassen", "spielobjekt_50.py")
                    elif "hindernis_missing_typ" in name:
                        # Use hindernis without x attribute - should fail (attribute test)
                        zettel_variant_path = os.path.join(ROOT, "klassen", "zettel_50.py")
                        hindernis_variant_path = os.path.join(ROOT, "klassen", "hindernis_50_missing_typ.py")
                        spielobjekt_variant_path = os.path.join(ROOT, "klassen", "spielobjekt_50.py")
                    elif "spielobjekt_private" in name:
                        # Use spielobjekt with private attrs - should fail
                        zettel_variant_path = os.path.join(ROOT, "klassen", "zettel_50.py")
                        hindernis_variant_path = os.path.join(ROOT, "klassen", "hindernis_50.py")
                        spielobjekt_variant_path = os.path.join(ROOT, "klassen", "spielobjekt_50_private.py")
                    elif "no_inheritance" in name:
                        # Use classes without inheritance - should fail
                        zettel_variant_path = os.path.join(ROOT, "klassen", "zettel_50_no_inherit.py")
                        hindernis_variant_path = os.path.join(ROOT, "klassen", "hindernis_50_no_inherit.py")
                        spielobjekt_variant_path = os.path.join(ROOT, "klassen", "spielobjekt_50.py")
                    else:
                        # Normal lsg50.py - use correct variants
                        zettel_variant_path = os.path.join(ROOT, "klassen", "zettel_50.py")
                        hindernis_variant_path = os.path.join(ROOT, "klassen", "hindernis_50.py")
                        spielobjekt_variant_path = os.path.join(ROOT, "klassen", "spielobjekt_50.py")
                    
                    # Copy spielobjekt variant
                    if os.path.exists(spielobjekt_variant_path):
                        with open(spielobjekt_variant_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(spielobjekt_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied {os.path.basename(spielobjekt_variant_path)} to klassen/spielobjekt.py for {name}\n")
                    
                    # Copy hindernis variant
                    if os.path.exists(hindernis_variant_path):
                        with open(hindernis_variant_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(hindernis_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied {os.path.basename(hindernis_variant_path)} to klassen/hindernis.py for {name}\n")
                    
                    # Copy zettel variant
                    if os.path.exists(zettel_variant_path):
                        with open(zettel_variant_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(zettel_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied {os.path.basename(zettel_variant_path)} to klassen/zettel.py for {name}\n")
                        
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace klassen files for {name}: {e}\n")
            
            # Level 56: Inventar and Gegenstand class variants
            if needs_level56_replacement:
                inventar_klassen_path = os.path.join(ROOT, "klassen", "inventar.py")
                gegenstand_klassen_path = os.path.join(ROOT, "klassen", "gegenstand.py")
                
                try:
                    # Backup existing files
                    if os.path.exists(inventar_klassen_path):
                        with open(inventar_klassen_path, 'r', encoding='utf-8') as f:
                            inventar_backup = f.read()
                    if os.path.exists(gegenstand_klassen_path):
                        with open(gegenstand_klassen_path, 'r', encoding='utf-8') as f:
                            gegenstand_backup = f.read()
                    
                    # Determine variants based on test name
                    if "gegenstand_missing_art" in name:
                        gegenstand_variant = "gegenstand_56_missing_art.py"
                        inventar_variant = "inventar_56.py"
                    elif "gegenstand_missing_sammeln" in name:
                        gegenstand_variant = "gegenstand_56_missing_sammeln.py"
                        inventar_variant = "inventar_56.py"
                    elif "inventar_missing_items" in name:
                        gegenstand_variant = "gegenstand_56.py"
                        inventar_variant = "inventar_56_missing_items.py"
                    elif "inventar_missing_method" in name:
                        gegenstand_variant = "gegenstand_56.py"
                        inventar_variant = "inventar_56_missing_method.py"
                    else:
                        # Normal lsg56.py - use correct files
                        gegenstand_variant = "gegenstand_56.py"
                        inventar_variant = "inventar_56.py"
                    
                    # Copy variants
                    gegenstand_src = os.path.join(ROOT, "klassen", gegenstand_variant)
                    if os.path.exists(gegenstand_src):
                        with open(gegenstand_src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(gegenstand_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied {gegenstand_variant} to klassen/gegenstand.py for {name}\n")
                    
                    inventar_src = os.path.join(ROOT, "klassen", inventar_variant)
                    if os.path.exists(inventar_src):
                        with open(inventar_src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(inventar_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied {inventar_variant} to klassen/inventar.py for {name}\n")
                        
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace level 56 files for {name}: {e}\n")
            
            # Level 57: Held and Knappe with Inventar
            if needs_level57_replacement:
                held_klassen_path = os.path.join(ROOT, "klassen", "held.py")
                knappe_klassen_path = os.path.join(ROOT, "klassen", "knappe.py")
                inventar_klassen_path = os.path.join(ROOT, "klassen", "inventar.py")
                gegenstand_klassen_path = os.path.join(ROOT, "klassen", "gegenstand.py")
                
                try:
                    # Backup existing files
                    if os.path.exists(held_klassen_path):
                        with open(held_klassen_path, 'r', encoding='utf-8') as f:
                            held_backup = f.read()
                    if os.path.exists(knappe_klassen_path):
                        with open(knappe_klassen_path, 'r', encoding='utf-8') as f:
                            knappe_backup = f.read()
                    if os.path.exists(inventar_klassen_path):
                        with open(inventar_klassen_path, 'r', encoding='utf-8') as f:
                            inventar_backup = f.read()
                    if os.path.exists(gegenstand_klassen_path):
                        with open(gegenstand_klassen_path, 'r', encoding='utf-8') as f:
                            gegenstand_backup = f.read()
                    
                    # Determine variants based on test name
                    if "held_no_schwert" in name:
                        held_file = "held_57_no_schwert.py"
                        knappe_file = "knappe_57.py"
                    elif "held_no_rucksack" in name:
                        held_file = "held_57_no_rucksack.py"
                        knappe_file = "knappe_57.py"
                    elif "knappe_with_items" in name:
                        held_file = "held_57.py"
                        knappe_file = "knappe_57_with_items.py"
                    elif "knappe_no_rucksack" in name:
                        held_file = "held_57.py"
                        knappe_file = "knappe_57_no_rucksack.py"
                    else:
                        # Normal lsg57.py - use correct files
                        held_file = "held_57.py"
                        knappe_file = "knappe_57.py"
                    
                    # Copy Held variant
                    held_src = os.path.join(ROOT, "klassen", held_file)
                    if os.path.exists(held_src):
                        with open(held_src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(held_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied {held_file} to klassen/held.py for {name}\n")
                    
                    # Copy Knappe variant
                    knappe_src = os.path.join(ROOT, "klassen", knappe_file)
                    if os.path.exists(knappe_src):
                        with open(knappe_src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(knappe_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied {knappe_file} to klassen/knappe.py for {name}\n")
                    
                    # Copy correct Inventar and Gegenstand (always use correct versions for level 57)
                    inventar_src = os.path.join(ROOT, "klassen", "inventar_56.py")
                    if os.path.exists(inventar_src):
                        with open(inventar_src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(inventar_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied inventar_56.py to klassen/inventar.py for {name}\n")
                    
                    gegenstand_src = os.path.join(ROOT, "klassen", "gegenstand_56.py")
                    if os.path.exists(gegenstand_src):
                        with open(gegenstand_src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(gegenstand_klassen_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._log_and_queue(f"[info] Copied gegenstand_56.py to klassen/gegenstand.py for {name}\n")
                        
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not replace level 57 files for {name}: {e}\n")
            
            env = os.environ.copy()
            env["OOP_TEST"] = "1"
            env["PYTHONPATH"] = ROOT
            env["RUN_LSG_DELAY_MS"] = str(delay_ms)

            proc = subprocess.Popen(
                [pyexe, path], cwd=ROOT,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=env, text=True, bufsize=1
            )

            # store proc so stop can kill it
            self._current_proc = proc

            try:
                if timeout_secs and timeout_secs > 0:
                    # Use timeout
                    out, _ = proc.communicate(timeout=timeout_secs)
                    for line in out.splitlines(True):
                        self.queue.put(line)
                        self._log(line)
                else:
                    # No timeout - stream output
                    with proc.stdout:
                        for line in proc.stdout:
                            # forward line to main thread
                            self.queue.put(line)
                            self._log(line)
                            if self._stop_event.is_set():
                                try:
                                    proc.kill()
                                except Exception:
                                    pass
                                break
                    proc.wait()
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    rest = proc.stdout.read() if proc.stdout else ""
                    if rest:
                        self.queue.put(rest)
                        self._log(rest)
                except Exception:
                    pass
                timeout_msg = "=> TIMEOUT\n"
                self.queue.put(timeout_msg)
                self._log(timeout_msg)
                # Determine expected outcome for timeout case
                expected_fail = "expected_fail" in name
                expected_outcome = not expected_fail
                actual_outcome = False  # timeout = fail
                deviation = (expected_outcome != actual_outcome)
                results.append((name, False, 124, expected_outcome, deviation))
                self._current_proc = None
                continue
            except Exception as e:
                exc_msg = f"[runner] Exception: {e}\n"
                self.queue.put(exc_msg)
                self._log(exc_msg)
                try:
                    proc.kill()
                except Exception:
                    pass

            rc = proc.returncode if proc else -1
            ok = (rc == 0)
            # Determine expected outcome
            expected_fail = "expected_fail" in name
            expected_outcome = not expected_fail  # True for normal tests, False for expected_fail tests
            actual_outcome = ok
            deviation = (expected_outcome != actual_outcome)
            
            results.append((name, ok, rc, expected_outcome, deviation))
            result_msg = f"=> {'OK' if ok else f'FAIL (code {rc})'}\n"
            self.queue.put(result_msg)
            self._log(result_msg)
            
            # Restore schueler.py if it was replaced
            if needs_schueler_replacement and schueler_backup is not None:
                try:
                    with open(schueler_path, 'w', encoding='utf-8') as f:
                        f.write(schueler_backup)
                    self._log_and_queue(f"[info] Restored schueler.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore schueler.py: {e}\n")
            
            # Restore klassen/held.py if it was replaced (lsg35-37, lsg38, lsg39, or lsg40-43)
            if (needs_level35_held_replacement or needs_held_replacement or needs_level39_held_replacement or needs_level40_held_replacement or needs_level41_held_replacement or needs_level42_held_replacement or needs_level43_held_replacement) and held_backup is not None:
                try:
                    with open(held_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(held_backup)
                    self._log_and_queue(f"[info] Restored klassen/held.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/held.py: {e}\n")
            
            # Restore klassen/hindernis.py if it was replaced (lsg44 or lsg50)
            if (needs_level44_hindernis_replacement or needs_level50_replacement) and hindernis_backup is not None:
                try:
                    with open(hindernis_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(hindernis_backup)
                    self._log_and_queue(f"[info] Restored klassen/hindernis.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/hindernis.py: {e}\n")
            
            # Restore klassen/zettel.py if it was replaced (lsg45 or lsg50)
            if (needs_level45_zettel_replacement or needs_level50_replacement) and zettel_backup is not None:
                try:
                    with open(zettel_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(zettel_backup)
                    self._log_and_queue(f"[info] Restored klassen/zettel.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/zettel.py: {e}\n")
            
            # Restore klassen/spielobjekt.py if it was replaced (lsg50)
            if needs_level50_replacement and spielobjekt_backup is not None:
                try:
                    with open(spielobjekt_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(spielobjekt_backup)
                    self._log_and_queue(f"[info] Restored klassen/spielobjekt.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/spielobjekt.py: {e}\n")
            
            # Restore klassen/spielobjekt.py if it was replaced (lsg50)
            if needs_level50_replacement and spielobjekt_backup is not None:
                try:
                    with open(spielobjekt_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(spielobjekt_backup)
                    self._log_and_queue(f"[info] Restored klassen/spielobjekt.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/spielobjekt.py: {e}\n")
            
            # Restore klassen/inventar.py if it was replaced (lsg56 or lsg57)
            if (needs_level56_replacement or needs_level57_replacement) and inventar_backup is not None:
                try:
                    inventar_klassen_path = os.path.join(ROOT, "klassen", "inventar.py")
                    with open(inventar_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(inventar_backup)
                    self._log_and_queue(f"[info] Restored klassen/inventar.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/inventar.py: {e}\n")
            
            # Restore klassen/gegenstand.py if it was replaced (lsg56 or lsg57)
            if (needs_level56_replacement or needs_level57_replacement) and gegenstand_backup is not None:
                try:
                    gegenstand_klassen_path = os.path.join(ROOT, "klassen", "gegenstand.py")
                    with open(gegenstand_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(gegenstand_backup)
                    self._log_and_queue(f"[info] Restored klassen/gegenstand.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/gegenstand.py: {e}\n")
            
            # Restore klassen/held.py if it was replaced (lsg57)
            if needs_level57_replacement and held_backup is not None:
                try:
                    held_klassen_path = os.path.join(ROOT, "klassen", "held.py")
                    with open(held_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(held_backup)
                    self._log_and_queue(f"[info] Restored klassen/held.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/held.py: {e}\n")
            
            # Restore klassen/knappe.py if it was replaced (lsg57)
            if needs_level57_replacement and knappe_backup is not None:
                try:
                    knappe_klassen_path = os.path.join(ROOT, "klassen", "knappe.py")
                    with open(knappe_klassen_path, 'w', encoding='utf-8') as f:
                        f.write(knappe_backup)
                    self._log_and_queue(f"[info] Restored klassen/knappe.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore klassen/knappe.py: {e}\n")
            
            # Restore framework/held.py if it was modified
            if needs_framework_held_modification and framework_held_backup is not None:
                try:
                    with open(held_framework_path, 'w', encoding='utf-8') as f:
                        f.write(framework_held_backup)
                    self._log_and_queue(f"[info] Restored framework/held.py after {name}\n")
                except Exception as e:
                    self._log_and_queue(f"[warning] Could not restore framework/held.py: {e}\n")

        # summary
        summary_msg = "\n--- summary ---\n"
        self.queue.put(summary_msg)
        self._log(summary_msg)
        
        total_tests = len(results)
        deviations = []
        
        for name, ok, code, expected_outcome, deviation in results:
            status = "OK" if ok else f"FAIL ({code})"
            if deviation:
                expected_str = "PASS" if expected_outcome else "FAIL"
                actual_str = "PASS" if ok else "FAIL"
                deviation_marker = f" [DEVIATION: Expected {expected_str}, got {actual_str}]"
                deviations.append((name, expected_str, actual_str))
            else:
                deviation_marker = ""
            line = f"{name}: {status}{deviation_marker}\n"
            self.queue.put(line)
            self._log(line)
        
        # Deviation summary
        if deviations:
            dev_header = f"\n--- DEVIATIONS ({len(deviations)}/{total_tests}) ---\n"
            self.queue.put(dev_header)
            self._log(dev_header)
            for name, expected, actual in deviations:
                dev_line = f"{name}: Expected {expected}, got {actual}\n"
                self.queue.put(dev_line)
                self._log(dev_line)
        else:
            all_ok = f"\n--- All tests matched expectations ({total_tests}/{total_tests}) ---\n"
            self.queue.put(all_ok)
            self._log(all_ok)

    def _append_text(self, txt):
        self.text.insert(tk.END, txt)
        self.text.see(tk.END)
    
    def _log(self, txt):
        """Write to log file if open."""
        if self.log_file:
            try:
                self.log_file.write(txt)
                self.log_file.flush()
            except Exception:
                pass
    
    def _log_and_queue(self, msg):
        """Write to both queue and log file."""
        self.queue.put(msg)
        self._log(msg)

    def _poll_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                if item == "__RUN_FINISHED__":
                    self._on_run_finished()
                    continue
                self._append_text(item)
        except queue.Empty:
            pass
        # keep polling
        self.master.after(100, self._poll_queue)

    def _on_run_finished(self):
        self.run_btn.config(state=tk.NORMAL)
        self.all_btn.config(state=tk.NORMAL)
        self.none_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        for cb in self.list_frame.winfo_children():
            cb.config(state=tk.NORMAL)
        self._current_proc = None


if __name__ == '__main__':
    root = tk.Tk()
    app = RunLsgGui(root)
    root.mainloop()
