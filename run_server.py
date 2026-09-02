"""
NexaHRM — Production FastAPI REST API Server Runner
Launches the FastAPI backend serving JSON REST endpoints.
"""

import os
import sys
import uvicorn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 65)
    print("  NexaHRM // Enterprise FastAPI REST API Server")
    print(f"  Server listening on http://{host}:{port}")
    print("=" * 65)
    uvicorn.run("core.api:app", host=host, port=port, reload=False)
