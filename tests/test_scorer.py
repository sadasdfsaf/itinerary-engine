from itinerary_engine.evaluator.scorer import ItineraryScorer
from itinerary_engine.schema.models import BudgetSummary, Itinerary, TripRequest
import pytest


def test_scorer_accepts_custom_weights() -> None:
    request = TripRequest(destination="tokyo", days=2, total_budget=100, interests=["food"])
    itinerary = Itinerary(
        itinerary_id="demo",
        destination="tokyo",
        days=2,
        summary="demo",
        day_plans=[],
        budget_summary=BudgetSummary(
            currency="USD",
            estimated_total=140,
            activities_total=100,
            food_total=20,
            transport_total=20,
            buffer_total=0,
            within_budget=False,
        ),
        tags=["editable"],
    )

    balanced = ItineraryScorer().score(request, itinerary)
    budget_heavy = ItineraryScorer(weights={"budget_fit": 5.0}).score(request, itinerary)

    assert balanced.overall != budget_heavy.overall


def test_zero_budget_scores_as_unset_budget() -> None:
    request = TripRequest(destination="tokyo", days=2, total_budget=0, interests=["food"])
    itinerary = Itinerary(
        itinerary_id="demo",
        destination="tokyo",
        days=2,
        summary="demo",
        day_plans=[],
        budget_summary=BudgetSummary(
            currency="USD",
            estimated_total=140,
            activities_total=100,
            food_total=20,
            transport_total=20,
            buffer_total=0,
            within_budget=True,
        ),
        tags=["editable"],
    )

    score = ItineraryScorer().score(request, itinerary)

    assert score.budget_fit == 0.8


def test_scorer_rejects_unknown_weight_key() -> None:
    with pytest.raises(ValueError, match="Unknown score weights"):
        ItineraryScorer(weights={"unknown": 1.0})


def test_scorer_rejects_negative_weight() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ItineraryScorer(weights={"pacing": -1.0})
