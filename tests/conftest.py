import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SERVER_PATH = REPO_ROOT / "apps" / "api-server"

if str(API_SERVER_PATH) not in sys.path:
    sys.path.insert(0, str(API_SERVER_PATH))
