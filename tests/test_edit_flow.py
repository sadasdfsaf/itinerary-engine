from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.edit_parser.rule_based import RuleBasedEditParser
from itinerary_engine.patcher.engine import PatchEngine
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import TripRequest


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
