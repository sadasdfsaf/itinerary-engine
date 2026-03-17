from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _trip_request() -> dict:
    return {
        "destination": "tokyo",
        "days": 3,
        "travelers": 1,
        "total_budget": 450,
        "budget_currency": "USD",
        "daily_budget_soft_limit": 120,
        "interests": ["food", "culture", "shopping"],
        "excluded_categories": [],
        "pace": "balanced",
        "mobility": "standard",
        "with_kids": False,
        "transport_mode": "mixed",
        "notes": "First time in the city.",
    }


def test_plan_edit_score_api_flow() -> None:
    plan_response = client.post("/plan", json={"trip_request": _trip_request()})
    assert plan_response.status_code == 200
    planned = plan_response.json()
    assert planned["trace"]["planner"] == "baseline"

    edit_response = client.post(
        "/edit",
        json={
            "trip_request": _trip_request(),
            "itinerary": planned["itinerary"],
            "instruction": "Replace the museum on day 2 with a food market.",
        },
    )
    assert edit_response.status_code == 200
    edited = edit_response.json()
    assert edited["affected_days"] == [2]
    assert edited["itinerary"]["version"] == 2

    score_response = client.post(
        "/score",
        json={
            "trip_request": _trip_request(),
            "itinerary": edited["itinerary"],
        },
    )
    assert score_response.status_code == 200
    scored = score_response.json()
    assert scored["scores"]["overall"] >= 0
    assert scored["summary"]
