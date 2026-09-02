"""
NexaHRM — AI-Powered Workforce Intelligence Platform
Entry point for local development and production deployment.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    import subprocess
    print("=" * 60)
    print("  NexaHRM // AI-Powered Workforce Intelligence Platform")
    print("  Launching Streamlit application...")
    print("=" * 60)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(BASE_DIR / "ui" / "app.py"),
        "--server.port", os.environ.get("PORT", "8502"),
        "--server.address", "0.0.0.0"
    ])
