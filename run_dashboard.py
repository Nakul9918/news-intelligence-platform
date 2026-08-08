"""
Streamlit Dashboard Launcher
"""

import sys
import subprocess

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"])
