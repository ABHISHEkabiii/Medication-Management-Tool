import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(ROOT, "MMT_VSCODE")

if not os.path.isdir(PROJECT_ROOT):
    raise SystemExit("Nested MMT_VSCODE folder not found. Please keep the folder structure intact.")

sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from app import app

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=True)
