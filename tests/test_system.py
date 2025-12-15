"""
Level Test System - GUI Application

Dieses System ermöglicht strukturierte Tests für jedes Level mit:
- Schüler-Implementierungen (schueler.py, klassen/*.py)
- Erwartete Fehlschläge (schueler_fail*.py, held_fail*.py, etc.)
- Funktionale Tests (test_config.json) für Methodenvalidierung
"""

import os
import sys
import json
import glob
import shutil
import threading
import subprocess
import time
import queue
import tkinter as tk
from tkinter import ttk
from pathlib import Path

ROOT = os.path.abspath(os.path.dirname(__file__))
LEVEL_TESTS_DIR = os.path.join(ROOT, "tests", "level_tests")
SCHUELER_PATH = os.path.join(ROOT, "schueler.py")
KLASSEN_DIR = os.path.join(ROOT, "klassen")

pyexe = sys.executable


class TestSystemGui:
    def __init__(self, master):
        self.master = master
        master.title("Level Test System")
        master.geometry("1000x700")

        # Find all test directories
        self.test_dirs = self._discover_test_directories()
        if not self.test_dirs:
            tk.messagebox.showinfo("Info", f"Keine Test-Verzeichnisse in {LEVEL_TESTS_DIR} gefunden.")
        
        self.selected_tests = {}
        self.check_vars = {}
        
        # Top frame: test list and controls
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
        
        # Populate test checkboxes
        for test_info in self.test_dirs:
            name = test_info['name']
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.list_frame, text=name, variable=var)
            cb.pack(anchor='w', padx=4, pady=2)
            self.check_vars[name] = var
        
        # Right controls
        right = ttk.Frame(top)
        right.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=6)
        
        ttk.Label(right, text="Timeout (secs):").pack(anchor='w', pady=(4,2))
        self.timeout_var = tk.StringVar(value="5")
        self.timeout_entry = ttk.Entry(right, textvariable=self.timeout_var, width=12)
        self.timeout_entry.pack(anchor='w')
        
        btn_frame = ttk.Frame(right)
        btn_frame.pack(anchor='w', pady=8)
        
        self.all_btn = ttk.Button(btn_frame, text="Alle", command=self.select_all)
        self.all_btn.pack(side=tk.LEFT, padx=2)
        self.none_btn = ttk.Button(btn_frame, text="Keine", command=self.select_none)
        self.none_btn.pack(side=tk.LEFT, padx=2)
        
        self.run_btn = ttk.Button(right, text="Run Tests", command=self.start_run)
        self.run_btn.pack(fill=tk.X, pady=(10,2))
        
        self.stop_btn = ttk.Button(right, text="Stop", command=self.stop_run, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)
        
        # Text output
        out_frame = ttk.Frame(master)
        out_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=(0,6))
        self.text = tk.Text(out_frame, wrap='none', font=('Consolas', 9))
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
    
    def _discover_test_directories(self):
        """Entdeckt alle Test-Verzeichnisse mit schueler.py oder Klassendateien"""
        if not os.path.exists(LEVEL_TESTS_DIR):
            return []
        
        test_dirs = []
        for entry in sorted(os.listdir(LEVEL_TESTS_DIR)):
            full_path = os.path.join(LEVEL_TESTS_DIR, entry)
            if not os.path.isdir(full_path):
                continue
            
            # Prüfe ob schueler.py oder Klassendateien existieren
            has_schueler = os.path.exists(os.path.join(full_path, "schueler.py"))
            class_files = glob.glob(os.path.join(full_path, "*.py"))
            class_files = [f for f in class_files if os.path.basename(f) not in ['schueler.py', 'test_config.py']]
            
            if has_schueler or class_files:
                test_info = {
                    'name': entry,
                    'path': full_path,
                    'has_schueler': has_schueler,
                    'class_files': class_files
                }
                test_dirs.append(test_info)
        
        return test_dirs
    
    def select_all(self):
        for v in self.check_vars.values():
            v.set(True)
    
    def select_none(self):
        for v in self.check_vars.values():
            v.set(False)
    
    def start_run(self):
        selected = [t for t in self.test_dirs if self.check_vars.get(t['name'], tk.BooleanVar()).get()]
        if not selected:
            self._append_text("Keine Tests ausgewählt.\n")
            return
        
        try:
            timeout = int(self.timeout_var.get())
        except Exception:
            self._append_text("Ungültiger Timeout-Wert.\n")
            return
        
        # Disable UI
        self.run_btn.config(state=tk.DISABLED)
        self.all_btn.config(state=tk.DISABLED)
        self.none_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        for cb in self.list_frame.winfo_children():
            cb.config(state=tk.DISABLED)
        self._stop_event.clear()
        
        # Start worker thread
        self.worker_thread = threading.Thread(
            target=self._run_worker, 
            args=(selected, timeout), 
            daemon=True
        )
        self.worker_thread.start()
    
    def stop_run(self):
        self._stop_event.set()
        self._append_text("Stop angefordert...\n")
    
    def _run_worker(self, selected_tests, timeout_secs):
        """Worker thread für Test-Ausführung"""
        results = []
        backups = {}
        
        for test_info in selected_tests:
            if self._stop_event.is_set():
                break
            
            test_name = test_info['name']
            test_path = test_info['path']
            
            self.queue.put(f"\n{'='*70}\n")
            self.queue.put(f"TEST: {test_name}\n")
            self.queue.put(f"{'='*70}\n")
            
            # Lade Test-Konfiguration falls vorhanden
            test_config = self._load_test_config(test_path)
            
            # Finde alle Testdateien (normal + fail)
            test_files = self._find_test_files(test_path)
            
            for test_file in test_files:
                if self._stop_event.is_set():
                    break
                
                file_name = test_file['name']
                file_path = test_file['path']
                target_path = test_file['target']
                is_fail_test = test_file['is_fail']
                
                self.queue.put(f"\n--- Testing: {file_name} {'(expected FAIL)' if is_fail_test else ''} ---\n")
                
                # Backup und Kopiere Dateien
                try:
                    self._backup_and_copy(test_path, backups)
                except Exception as e:
                    self.queue.put(f"[ERROR] Backup/Copy fehlgeschlagen: {e}\n")
                    results.append((test_name, file_name, False, is_fail_test, True, "backup_error"))
                    continue
                
                # Führe Test aus
                test_result = self._execute_test(
                    test_name, 
                    file_name, 
                    timeout_secs,
                    test_config
                )
                
                # Restore Dateien
                self._restore_backups(backups)
                backups.clear()
                
                # Auswerten
                success = test_result['success']
                expected_outcome = not is_fail_test
                actual_outcome = success
                deviation = (expected_outcome != actual_outcome)
                
                results.append((
                    test_name, 
                    file_name, 
                    success, 
                    is_fail_test, 
                    deviation,
                    test_result.get('reason', '')
                ))
                
                status = "✓ PASS" if success else "✗ FAIL"
                self.queue.put(f"Result: {status}\n")
                if test_result.get('reason'):
                    self.queue.put(f"Reason: {test_result['reason']}\n")
        
        # Summary
        self._print_summary(results)
        self.queue.put("\n[Test run finished]\n")
        self.queue.put("__RUN_FINISHED__")
    
    def _load_test_config(self, test_path):
        """Lädt test_config.json falls vorhanden"""
        config_path = os.path.join(test_path, "test_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.queue.put(f"[WARNING] Konnte test_config.json nicht laden: {e}\n")
        return None
    
    def _find_test_files(self, test_path):
        """Findet alle Testdateien (normal + fail-Varianten)"""
        test_files = []
        
        # schueler.py Varianten
        schueler_main = os.path.join(test_path, "schueler.py")
        if os.path.exists(schueler_main):
            test_files.append({
                'name': 'schueler.py',
                'path': schueler_main,
                'target': SCHUELER_PATH,
                'is_fail': False
            })
        
        # schueler_fail*.py Varianten
        for fail_file in glob.glob(os.path.join(test_path, "schueler_fail*.py")):
            test_files.append({
                'name': os.path.basename(fail_file),
                'path': fail_file,
                'target': SCHUELER_PATH,
                'is_fail': True
            })
        
        # Klassendateien (held.py, knappe.py, etc.)
        for class_file in glob.glob(os.path.join(test_path, "*.py")):
            basename = os.path.basename(class_file)
            if basename in ['schueler.py', 'test_config.py'] or '_fail' in basename:
                continue
            
            test_files.append({
                'name': basename,
                'path': class_file,
                'target': os.path.join(KLASSEN_DIR, basename),
                'is_fail': False
            })
        
        # Klassendateien fail-Varianten (held_fail*.py, etc.)
        for fail_file in glob.glob(os.path.join(test_path, "*_fail*.py")):
            basename = os.path.basename(fail_file)
            if basename.startswith('schueler_fail'):
                continue
            
            # Extrahiere Basisname (z.B. held_fail_setters.py -> held.py)
            base_class = basename.split('_fail')[0] + '.py'
            
            test_files.append({
                'name': basename,
                'path': fail_file,
                'target': os.path.join(KLASSEN_DIR, base_class),
                'is_fail': True
            })
        
        return test_files
    
    def _backup_and_copy(self, test_path, backups):
        """Backup aktuelle Dateien und kopiere Test-Dateien"""
        # Backup schueler.py
        if os.path.exists(SCHUELER_PATH):
            with open(SCHUELER_PATH, 'r', encoding='utf-8') as f:
                backups['schueler.py'] = f.read()
        
        # Backup Klassendateien
        for class_file in glob.glob(os.path.join(test_path, "*.py")):
            basename = os.path.basename(class_file)
            if basename in ['schueler.py', 'test_config.py']:
                continue
            
            # Bestimme Zieldatei (auch für fail-Varianten)
            if '_fail' in basename:
                base_class = basename.split('_fail')[0] + '.py'
            else:
                base_class = basename
            
            target = os.path.join(KLASSEN_DIR, base_class)
            if os.path.exists(target):
                with open(target, 'r', encoding='utf-8') as f:
                    backups[base_class] = f.read()
        
        # Kopiere Test-Dateien
        schueler_test = os.path.join(test_path, "schueler.py")
        if os.path.exists(schueler_test):
            shutil.copy2(schueler_test, SCHUELER_PATH)
        
        for class_file in glob.glob(os.path.join(test_path, "*.py")):
            basename = os.path.basename(class_file)
            if basename in ['schueler.py', 'test_config.py']:
                continue
            
            if '_fail' in basename:
                base_class = basename.split('_fail')[0] + '.py'
            else:
                base_class = basename
            
            target = os.path.join(KLASSEN_DIR, base_class)
            shutil.copy2(class_file, target)
    
    def _restore_backups(self, backups):
        """Stelle Backup-Dateien wieder her"""
        for filename, content in backups.items():
            if filename == 'schueler.py':
                target = SCHUELER_PATH
            else:
                target = os.path.join(KLASSEN_DIR, filename)
            
            try:
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                self.queue.put(f"[WARNING] Konnte {filename} nicht wiederherstellen: {e}\n")
    
    def _execute_test(self, test_name, file_name, timeout_secs, test_config):
        """Führt einen einzelnen Test aus"""
        env = os.environ.copy()
        env["OOP_TEST"] = "1"
        env["PYTHONPATH"] = ROOT
        
        proc = subprocess.Popen(
            [pyexe, SCHUELER_PATH],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            bufsize=1
        )
        
        try:
            out, _ = proc.communicate(timeout=timeout_secs)
            for line in out.splitlines(True):
                self.queue.put(line)
            
            rc = proc.returncode
            
            # Prüfe auf Victory
            success = ("[TEST] Level erfolgreich beendet" in out or 
                      "Victory: True" in out or
                      rc == 0)
            
            # Funktionale Tests aus test_config.json
            if test_config and success:
                func_result = self._run_functional_tests(test_config)
                if not func_result['success']:
                    return {
                        'success': False,
                        'reason': f"Functional test failed: {func_result['reason']}"
                    }
            
            return {'success': success, 'reason': '' if success else f'exit code {rc}'}
            
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                rest = proc.stdout.read() if proc.stdout else ""
                if rest:
                    self.queue.put(rest)
            except Exception:
                pass
            return {'success': False, 'reason': 'timeout'}
        except Exception as e:
            return {'success': False, 'reason': f'exception: {e}'}
    
    def _run_functional_tests(self, test_config):
        """Führt funktionale Tests aus test_config.json aus"""
        # TODO: Implementiere funktionale Tests
        # Format in test_config.json:
        # {
        #   "functional_tests": [
        #     {
        #       "description": "Test geh() method moves hero down",
        #       "setup": {
        #         "held_position": [1, 1, "down"],
        #         "level": 10
        #       },
        #       "actions": [
        #         {"method": "geh", "target": "held"}
        #       ],
        #       "assertions": [
        #         {"attribute": "x", "expected": 1},
        #         {"attribute": "y", "expected": 2},
        #         {"attribute": "richtung", "expected": "down"}
        #       ]
        #     }
        #   ]
        # }
        return {'success': True, 'reason': ''}
    
    def _print_summary(self, results):
        """Druckt Test-Zusammenfassung"""
        self.queue.put(f"\n{'='*70}\n")
        self.queue.put("TEST SUMMARY\n")
        self.queue.put(f"{'='*70}\n")
        
        total = len(results)
        passed = sum(1 for r in results if (r[2] and not r[3]) or (not r[2] and r[3]))
        failed = total - passed
        deviations = [r for r in results if r[4]]
        
        self.queue.put(f"Total: {total}, Passed: {passed}, Failed: {failed}\n")
        
        if deviations:
            self.queue.put(f"\nDEVIATIONS ({len(deviations)}):\n")
            for test_name, file_name, success, is_fail, _, reason in deviations:
                expected = "FAIL" if is_fail else "PASS"
                actual = "PASS" if success else "FAIL"
                self.queue.put(f"  {test_name}/{file_name}: Expected {expected}, got {actual}")
                if reason:
                    self.queue.put(f" ({reason})")
                self.queue.put("\n")
        else:
            self.queue.put("\n✓ All tests passed!\n")
    
    def _append_text(self, txt):
        self.text.insert(tk.END, txt)
        self.text.see(tk.END)
    
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
        self.master.after(100, self._poll_queue)
    
    def _on_run_finished(self):
        self.run_btn.config(state=tk.NORMAL)
        self.all_btn.config(state=tk.NORMAL)
        self.none_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        for cb in self.list_frame.winfo_children():
            cb.config(state=tk.NORMAL)


if __name__ == '__main__':
    root = tk.Tk()
    app = TestSystemGui(root)
    root.mainloop()
