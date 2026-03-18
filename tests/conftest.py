import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SERVER_PATH = REPO_ROOT / "apps" / "api-server"
PACKAGE_ROOTS = [
    REPO_ROOT / "packages" / "schema",
    REPO_ROOT / "packages" / "planner",
    REPO_ROOT / "packages" / "candidate_selector",
    REPO_ROOT / "packages" / "edit_parser",
    REPO_ROOT / "packages" / "patcher",
    REPO_ROOT / "packages" / "evaluator",
    REPO_ROOT / "packages" / "adapters",
]

if str(API_SERVER_PATH) not in sys.path:
    sys.path.insert(0, str(API_SERVER_PATH))

for package_root in PACKAGE_ROOTS:
    package_path = str(package_root)
    if package_path not in sys.path:
        sys.path.insert(0, package_path)
