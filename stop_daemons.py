"""
============================================================
News Intelligence Platform — Master Daemon Shutdown
============================================================
"""

import os
import sys
import json
import psutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
PID_FILE = RUNTIME_DIR / "pids.json"

def stop_all():
    print("=" * 70)
    print("STOPPING ALL PLATFORM DAEMONS")
    print("=" * 70)
    
    if not PID_FILE.exists():
        print("No active daemon PIDs found.")
        return

    try:
        with open(PID_FILE, "r") as f:
            pids = json.load(f)
    except Exception:
        pids = {}

    for name, pid in pids.items():
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=3)
            print(f"  [-] {name.capitalize():<15}: STOPPED (PID: {pid})")
        except psutil.NoSuchProcess:
            print(f"  [-] {name.capitalize():<15}: (PID {pid} was not running)")
        except psutil.TimeoutExpired:
            p.kill()
            print(f"  [-] {name.capitalize():<15}: KILLED (PID: {pid})")
        except Exception as e:
            print(f"  [-] {name.capitalize():<15}: ERROR stopping PID {pid}: {e}")

    PID_FILE.unlink(missing_ok=True)

    print("=" * 70)
    print("ALL DAEMONS SHUTDOWN COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    stop_all()
