from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.schema.models import POI, TripRequest


class PaceCatalogAdapter:
    def search(self, destination: str) -> list[POI]:
        return [
            POI(
                poi_id="short_stop",
                name="Short Stop",
                city="Test City",
                category="landmark",
                tags=["culture"],
                estimated_cost=10,
                visit_duration_hours=1.0,
            ),
            POI(
                poi_id="long_stop",
                name="Long Stop",
                city="Test City",
                category="landmark",
                tags=["culture"],
                estimated_cost=10,
                visit_duration_hours=3.0,
            ),
        ]


def test_fast_pace_penalizes_long_duration_stops() -> None:
    selector = SimpleCandidateSelector(PaceCatalogAdapter())

    slow_request = TripRequest(destination="pace", days=2, interests=["culture"], pace="slow")
    fast_request = TripRequest(destination="pace", days=2, interests=["culture"], pace="fast")

    short_stop, long_stop = PaceCatalogAdapter().search("pace")

    assert selector._score(long_stop, slow_request) == selector._score(short_stop, slow_request)
    assert selector._score(long_stop, fast_request) < selector._score(short_stop, fast_request)
