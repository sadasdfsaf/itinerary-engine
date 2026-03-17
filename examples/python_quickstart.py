# ruff: noqa: E402

import sys
from pathlib import Path


def bootstrap() -> None:
    repo_root = Path(__file__).resolve().parents[1]
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


bootstrap()

from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import TripRequest

request = TripRequest(
    destination="tokyo",
    days=3,
    total_budget=450,
    interests=["food", "culture", "shopping"],
    pace="balanced",
)

selector = SimpleCandidateSelector(StaticCatalogAdapter())
planner = BaselinePlanner(selector)
itinerary = planner.plan(request)

print(itinerary.summary)
print(itinerary.budget_summary.estimated_total)
