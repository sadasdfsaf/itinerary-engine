from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.edit_parser.rule_based import RuleBasedEditParser
from itinerary_engine.patcher.engine import PatchEngine
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import EditIntent, TripRequest


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
