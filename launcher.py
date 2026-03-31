"""
launcher.py - Entry point for the Mehal Lab Inventory .exe
"""
import os
import sys

# Fix for console=False (PyInstaller windowed mode)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8", errors="replace")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8", errors="replace")

import time
import socket
import webbrowser
import threading

# Determine base paths
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BUNDLE_DIR

os.chdir(EXE_DIR)
sys.path.insert(0, BUNDLE_DIR)
sys.path.insert(0, EXE_DIR)

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(EXE_DIR, "mehal_lab.db")
os.environ.setdefault("SECRET_KEY", "mehal-lab-secret-key-2024")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
os.environ["FRONTEND_DIR"] = os.path.join(BUNDLE_DIR, "frontend")

HOST = "127.0.0.1"
PORT = 8000
URL = "http://" + HOST + ":" + str(PORT)


def is_server_running():
    """Check if the server is already running on our port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((HOST, PORT))
        sock.close()
        return result == 0
    except Exception:
        return False


def seed_if_needed():
    db_path = os.path.join(EXE_DIR, "mehal_lab.db")
    if not os.path.exists(db_path):
        from app.seed import seed
        seed()


def open_browser(delay=0):
    if delay > 0:
        time.sleep(delay)
    webbrowser.open(URL)


def main():
    # If server is already running, just open browser and exit
    if is_server_running():
        webbrowser.open(URL)
        sys.exit(0)

    # First launch: seed database and start server
    seed_if_needed()

    # Open browser after server has time to start
    threading.Thread(target=open_browser, daemon=True, args=(2.5,)).start()

    import uvicorn
    from app.main import app

    try:
        uvicorn.run(app, host=HOST, port=PORT, log_level="error", access_log=False)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
