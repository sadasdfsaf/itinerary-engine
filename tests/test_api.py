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


def test_edit_with_out_of_range_day_returns_conflict() -> None:
    plan_response = client.post("/plan", json={"trip_request": _trip_request()})
    planned = plan_response.json()

    edit_response = client.post(
        "/edit",
        json={
            "trip_request": _trip_request(),
            "itinerary": planned["itinerary"],
            "instruction": "Remove museum on day 99",
        },
    )

    assert edit_response.status_code == 409


def test_edit_with_mismatched_destination_returns_unprocessable_entity() -> None:
    plan_response = client.post("/plan", json={"trip_request": _trip_request()})
    planned = plan_response.json()
    mismatched_request = _trip_request()
    mismatched_request["destination"] = "kyoto"

    edit_response = client.post(
        "/edit",
        json={
            "trip_request": mismatched_request,
            "itinerary": planned["itinerary"],
            "instruction": "Replace the museum on day 2 with a food market.",
        },
    )

    assert edit_response.status_code == 422


def test_cors_default_origins_are_restricted() -> None:
    cors_middleware = next(
        middleware for middleware in app.user_middleware if middleware.cls.__name__ == "CORSMiddleware"
    )
    assert cors_middleware.kwargs["allow_origins"] == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
