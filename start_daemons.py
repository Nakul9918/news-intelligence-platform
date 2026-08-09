"""
============================================================
News Intelligence Platform — Master Daemon Controller
============================================================
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
LOGS_DIR = PROJECT_ROOT / "logs"

RUNTIME_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

PYTHON_EXE = sys.executable

SERVICES = [
    ("ingestion", "ingestion_service.py"),
    ("consumer", "streaming/realtime_consumer.py"),
    ("orchestrator", "pipeline_orchestrator.py"),
    ("api", "run_api.py"),
    ("dashboard", "run_dashboard.py"),
]

PID_FILE = RUNTIME_DIR / "pids.json"

def start_all():
    print("=" * 70)
    print("STARTING ALL PLATFORM DAEMONS")
    print("=" * 70)
    
    pids = {}
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r") as f:
                pids = json.load(f)
        except Exception:
            pids = {}

    CREATE_NO_WINDOW = 0x08000000

    for name, script in SERVICES:
        script_path = PROJECT_ROOT / script
        log_out = open(LOGS_DIR / f"{name}.log", "a", encoding="utf-8")
        log_err = open(LOGS_DIR / f"{name}_err.log", "a", encoding="utf-8")

        proc = subprocess.Popen(
            [PYTHON_EXE, "-u", str(script_path)],
            stdout=log_out,
            stderr=log_err,
            cwd=str(PROJECT_ROOT),
            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        pids[name] = proc.pid
        print(f"  [+] {name.capitalize():<15}: STARTED (PID: {proc.pid})")

    with open(PID_FILE, "w") as f:
        json.dump(pids, f, indent=2)

    print("=" * 70)
    print("ALL DAEMONS STARTED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    start_all()
