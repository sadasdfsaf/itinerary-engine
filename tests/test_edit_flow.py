from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.edit_parser.rule_based import RuleBasedEditParser
from itinerary_engine.patcher.engine import PatchEngine
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import POI, EditIntent, TripRequest


def test_replace_edit_targets_day_two_and_updates_version() -> None:
    request = TripRequest(
        destination="tokyo",
        days=3,
        total_budget=450,
        interests=["food", "culture", "shopping"],
        pace="balanced",
    )
    selector = SimpleCandidateSelector(StaticCatalogAdapter())
    planner = BaselinePlanner(selector)
    parser = RuleBasedEditParser()
    patcher = PatchEngine(selector, planner)

    itinerary = planner.plan(request)
    intent = parser.parse("Replace the museum on day 2 with a food market.")
    updated, affected_days = patcher.apply(itinerary, intent, request)

    assert intent.target_day == 2
    assert intent.target_text == "museum"
    assert intent.replacement_text == "food market"
    assert affected_days == [2]
    assert updated.version == 2
    assert updated.day_plans[1].activities[1].poi.category == "food"


def test_same_day_move_is_a_no_op() -> None:
    request = TripRequest(
        destination="tokyo",
        days=3,
        total_budget=450,
        interests=["food", "culture", "shopping"],
        pace="balanced",
    )
    selector = SimpleCandidateSelector(StaticCatalogAdapter())
    planner = BaselinePlanner(selector)
    patcher = PatchEngine(selector, planner)

    itinerary = planner.plan(request)
    original_stop_ids = [activity.stop_id for activity in itinerary.day_plans[1].activities]
    intent = EditIntent(
        action="move",
        user_instruction="Move the museum to day 2.",
        target_day=2,
        source_day=2,
        target_text="museum",
    )

    updated, affected_days = patcher.apply(itinerary, intent, request)

    assert affected_days == []
    assert updated.version == itinerary.version
    assert [activity.stop_id for activity in updated.day_plans[1].activities] == original_stop_ids


def test_refresh_recomputes_notes_after_replacing_evening_stop() -> None:
    request = TripRequest(
        destination="tokyo",
        days=3,
        total_budget=450,
        interests=["food", "culture", "shopping"],
        pace="balanced",
    )
    selector = SimpleCandidateSelector(StaticCatalogAdapter())
    planner = BaselinePlanner(selector)
    patcher = PatchEngine(selector, planner)

    itinerary = planner.plan(request)
    assert "Reserve evening energy for the final stop." in itinerary.day_plans[2].notes

    intent = EditIntent(
        action="replace",
        user_instruction="Replace shibuya with a food market.",
        target_day=3,
        target_text="shibuya",
        replacement_text="food market",
    )
    updated, affected_days = patcher.apply(itinerary, intent, request)

    assert affected_days == [3]
    assert "Reserve evening energy for the final stop." not in updated.day_plans[2].notes


def test_slow_down_no_op_does_not_bump_version() -> None:
    request = TripRequest(
        destination="tokyo",
        days=3,
        total_budget=450,
        interests=["food", "culture", "shopping"],
        pace="slow",
    )
    selector = SimpleCandidateSelector(StaticCatalogAdapter())
    planner = BaselinePlanner(selector)
    patcher = PatchEngine(selector, planner)

    itinerary = planner.plan(request)
    intent = EditIntent(action="slow_down", user_instruction="Make it less packed.")

    updated, affected_days = patcher.apply(itinerary, intent, request)

    assert affected_days == []
    assert updated.version == itinerary.version
    assert updated.model_dump() == itinerary.model_dump()


def test_reindex_day_recomputes_start_times_after_remove() -> None:
    request = TripRequest(
        destination="tokyo",
        days=3,
        total_budget=450,
        interests=["food", "culture", "shopping"],
        pace="balanced",
    )
    selector = SimpleCandidateSelector(StaticCatalogAdapter())
    planner = BaselinePlanner(selector)
    patcher = PatchEngine(selector, planner)
    itinerary = planner.plan(request)
    removed_stop = itinerary.day_plans[0].activities[1]

    intent = EditIntent(
        action="remove",
        user_instruction="Remove a stop on day 1.",
        target_day=1,
        target_text=removed_stop.poi.name,
    )
    updated, affected_days = patcher.apply(itinerary, intent, request)

    assert affected_days == [1]
    day_one_times = [activity.start_time for activity in updated.day_plans[0].activities]
    assert day_one_times == ["09:00", "13:00"]


class ReplacementCatalogAdapter:
    def search(self, destination: str) -> list[POI]:
        return [
            POI(
                poi_id="food_existing",
                name="Existing Food Hall",
                city="Test City",
                category="food",
                tags=["food"],
                estimated_cost=10,
            ),
            POI(
                poi_id="museum_target",
                name="Target Museum",
                city="Test City",
                category="museum",
                tags=["culture"],
                estimated_cost=12,
                indoor=True,
            ),
            POI(
                poi_id="park_existing",
                name="Existing Park",
                city="Test City",
                category="park",
                tags=["nature"],
                estimated_cost=0,
            ),
            POI(
                poi_id="food_new",
                name="New Food Market",
                city="Test City",
                category="food",
                tags=["food", "market"],
                estimated_cost=15,
            ),
        ]


def test_replace_skips_same_day_existing_pois() -> None:
    request = TripRequest(destination="test", days=1, interests=[], pace="balanced")
    selector = SimpleCandidateSelector(ReplacementCatalogAdapter())
    planner = BaselinePlanner(selector)
    patcher = PatchEngine(selector, planner)

    itinerary = planner.plan(request)
    original_ids = [activity.poi.poi_id for activity in itinerary.day_plans[0].activities]
    assert original_ids == ["food_existing", "museum_target", "park_existing"]

    intent = EditIntent(
        action="replace",
        user_instruction="Replace the museum with food.",
        target_day=1,
        target_text="museum",
        replacement_text="food",
    )
    updated, affected_days = patcher.apply(itinerary, intent, request)

    updated_ids = [activity.poi.poi_id for activity in updated.day_plans[0].activities]

    assert affected_days == [1]
    assert updated_ids == ["food_existing", "food_new", "park_existing"]
    assert len(updated_ids) == len(set(updated_ids))
