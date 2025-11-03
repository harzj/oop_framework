import os, subprocess, sys, glob, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LSG_DIR = os.path.join(ROOT, "lsg")

pyexe = sys.executable
results = []

# Wenn RUN_LSG_TIMEOUT_SECS > 0 gesetzt ist, wird dieser Timeout pro Level verwendet (Sekunden).
# Setze nicht oder auf 0, um unbegrenzt zu warten (empfohlen, wenn Framework im Test-Modus selbst endet).
TIMEOUT_SECS = int(os.getenv("RUN_LSG_TIMEOUT_SECS", "0"))

paths = sorted(glob.glob(os.path.join(LSG_DIR, "lsg*.py")))
if not paths:
    print("Keine lsg/*.py Dateien gefunden.")
    sys.exit(1)

for path in paths:
    name = os.path.basename(path)
    print(f"\n=== Running {name} ===")
    env = os.environ.copy()
    env["OOP_TEST"] = "1"
    env["PYTHONPATH"] = ROOT  # damit 'import framework' aus lsg funktioniert

    proc = subprocess.Popen(
        [pyexe, path],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env=env, text=True, bufsize=1
    )

    out_lines = []
    start = time.time()

    try:
        if TIMEOUT_SECS and TIMEOUT_SECS > 0:
            # communicate mit Timeout (einfacher Fall)
            out, _ = proc.communicate(timeout=TIMEOUT_SECS)
            out_lines = out.splitlines(True)
            for l in out_lines:
                print(l, end="")
        else:
            # Live-Streaming und unbegrenztes Warten
            with proc.stdout:
                for line in proc.stdout:
                    print(line, end="")
                    out_lines.append(line)
            proc.wait()
    except subprocess.TimeoutExpired:
        proc.kill()
        # versuche Restausgabe einzulesen
        try:
            rest = proc.stdout.read() if proc.stdout else ""
            if rest:
                print(rest)
                out_lines.append(rest)
        except Exception:
            pass
        print("=> TIMEOUT")
        results.append((name, False, 124))
        continue

    rc = proc.returncode
    ok = (rc == 0)
    print(f"=> {'OK' if ok else f'FAIL (code {rc})'}")
    results.append((name, ok, rc))

print("\n--- summary ---")
for name, ok, code in results:
    print(name, "OK" if ok else f"FAIL ({code})")

sys.exit(0 if all(r[1] for r in results) else 2)