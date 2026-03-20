import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
subprocess.call([sys.executable, str(ROOT / "apps" / "enterprise_ui" / "app.py")], cwd=ROOT)
