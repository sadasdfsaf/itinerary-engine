from itinerary_engine.evaluator.scorer import ItineraryScorer
from itinerary_engine.schema.models import BudgetSummary, Itinerary, TripRequest


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
