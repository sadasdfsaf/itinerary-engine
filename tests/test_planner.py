from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import TripRequest


def test_baseline_planner_generates_editable_itinerary() -> None:
    request = TripRequest(
        destination="tokyo",
        days=3,
        total_budget=450,
        interests=["food", "culture", "shopping"],
        pace="balanced",
    )

    planner = BaselinePlanner(SimpleCandidateSelector(StaticCatalogAdapter()))
    itinerary = planner.plan(request)

    assert itinerary.destination == "tokyo"
    assert itinerary.days == 3
    assert len(itinerary.day_plans) == 3
    assert itinerary.version == 1
    assert itinerary.tags == ["balanced", "editable"]
    assert all(day.activities for day in itinerary.day_plans)
    assert all(activity.stop_id for day in itinerary.day_plans for activity in day.activities)
    assert itinerary.budget_summary.estimated_total > 0
