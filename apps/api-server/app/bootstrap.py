import sys
from pathlib import Path


def bootstrap_workspace() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    package_roots = [
        repo_root / "packages" / "schema",
        repo_root / "packages" / "planner",
        repo_root / "packages" / "candidate_selector",
        repo_root / "packages" / "edit_parser",
        repo_root / "packages" / "patcher",
        repo_root / "packages" / "evaluator",
        repo_root / "packages" / "adapters",
    ]
    for package_root in package_roots:
        package_path = str(package_root)
        if package_path not in sys.path:
            sys.path.insert(0, package_path)
