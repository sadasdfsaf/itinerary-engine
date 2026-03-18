from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import POI, TripRequest


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


def test_baseline_planner_avoids_duplicate_pois_when_unique_candidates_are_enough() -> None:
    request = TripRequest(
        destination="tokyo",
        days=3,
        total_budget=450,
        interests=["food", "culture", "shopping"],
        pace="balanced",
    )

    planner = BaselinePlanner(SimpleCandidateSelector(StaticCatalogAdapter()))
    itinerary = planner.plan(request)

    poi_ids = [activity.poi.poi_id for day in itinerary.day_plans for activity in day.activities]
    assert len(poi_ids) == len(set(poi_ids))


class TinyCatalogAdapter:
    def search(self, destination: str) -> list[POI]:
        return [
            POI(
                poi_id="tiny_1",
                name="Tiny One",
                city="Test City",
                category="landmark",
                estimated_cost=0,
                tags=["culture"],
            ),
            POI(
                poi_id="tiny_2",
                name="Tiny Two",
                city="Test City",
                category="food",
                estimated_cost=10,
                tags=["food"],
            ),
        ]


def test_baseline_planner_keeps_each_day_non_empty_even_with_small_catalog() -> None:
    request = TripRequest(
        destination="tiny",
        days=3,
        interests=["food", "culture"],
        pace="balanced",
    )

    planner = BaselinePlanner(SimpleCandidateSelector(TinyCatalogAdapter()))
    itinerary = planner.plan(request)

    assert len(itinerary.day_plans) == 3
    assert all(day.activities for day in itinerary.day_plans)
