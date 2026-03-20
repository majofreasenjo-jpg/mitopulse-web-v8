
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import uvicorn
uvicorn.run("api.app:app",host="0.0.0.0",port=8000,app_dir=str(ROOT))
