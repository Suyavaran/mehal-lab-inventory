"""
launcher.py - Entry point for the Mehal Lab Inventory .exe
"""
import os
import sys
import time
import webbrowser
import threading

# Determine base paths
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    # _MEIPASS is where PyInstaller extracts bundled files
    BUNDLE_DIR = sys._MEIPASS
    # The folder where the .exe actually lives (for database, .env)
    EXE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BUNDLE_DIR

os.chdir(EXE_DIR)
sys.path.insert(0, BUNDLE_DIR)
sys.path.insert(0, EXE_DIR)

# Set environment variables
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(EXE_DIR, 'mehal_lab.db')}"
os.environ.setdefault("SECRET_KEY", "mehal-lab-secret-key-2024")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "480")

# Tell the app where to find frontend files
os.environ["FRONTEND_DIR"] = os.path.join(BUNDLE_DIR, "frontend")

HOST = "127.0.0.1"
PORT = 8000


def seed_if_needed():
    db_path = os.path.join(EXE_DIR, "mehal_lab.db")
    if not os.path.exists(db_path):
        print("=" * 50)
        print("  First run - setting up database...")
        print("=" * 50)
        from app.seed import seed
        seed()
    else:
        print("Database found at:", db_path)


def open_browser():
    time.sleep(2.5)
    url = f"http://{HOST}:{PORT}"
    print(f"\nOpening browser: {url}")
    print("If browser doesn't open, go to that URL manually.\n")
    webbrowser.open(url)


def main():
    print()
    print("=" * 50)
    print("  Mehal Lab Inventory System")
    print("  Yale School of Medicine - Liver Center")
    print("=" * 50)
    print()
    print(f"  Bundle dir: {BUNDLE_DIR}")
    print(f"  Exe dir:    {EXE_DIR}")
    print()

    seed_if_needed()

    threading.Thread(target=open_browser, daemon=True).start()

    print(f"Starting server on http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.\n")

    import uvicorn
    from app.main import app

    try:
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
