from typing import List, Optional, Sequence

from itinerary_engine.adapters.catalog import POICatalogAdapter
from itinerary_engine.schema.models import POI, TripRequest


class SimpleCandidateSelector:
    def __init__(self, adapter: POICatalogAdapter):
        self.adapter = adapter

    def select(self, request: TripRequest, limit: int = 8) -> List[POI]:
        pool = self.adapter.search(request.destination)
        ranked = sorted(pool, key=lambda poi: self._score(poi, request), reverse=True)
        return ranked[:limit]

    def find_best_match(
        self,
        request: TripRequest,
        query: str,
        limit: int = 1,
        exclude_ids: Optional[Sequence[str]] = None,
    ) -> List[POI]:
        exclude_set = set(exclude_ids or [])
        pool = [
            poi
            for poi in self.adapter.search(request.destination)
            if poi.poi_id not in exclude_set
        ]
        ranked = sorted(pool, key=lambda poi: self._query_score(poi, query, request), reverse=True)
        return ranked[:limit]

    def _score(self, poi: POI, request: TripRequest) -> float:
        interests = {item.lower() for item in request.interests}
        tags = {item.lower() for item in poi.tags}
        interest_overlap = len(tags & interests)
        exclusion_penalty = 3 if poi.category in request.excluded_categories else 0
        family_bonus = 1 if request.with_kids and poi.family_friendly else 0
        indoor_bonus = 0.5 if request.mobility == "low" and poi.indoor else 0
        pace_penalty = 1 if request.pace == "slow" and poi.visit_duration_hours > 2.0 else 0
        cost_penalty = 0
        if request.daily_budget_soft_limit and poi.estimated_cost > request.daily_budget_soft_limit:
            cost_penalty = 2
        return (
            (interest_overlap * 3)
            + family_bonus
            + indoor_bonus
            - pace_penalty
            - exclusion_penalty
            - cost_penalty
        )

    def _query_score(self, poi: POI, query: str, request: TripRequest) -> float:
        query_lower = query.strip().lower()
        tokens = [token for token in query_lower.replace("-", " ").split() if token]
        name_score = 5 if query_lower and query_lower in poi.name.lower() else 0
        category_score = 3 if query_lower == poi.category.lower() else 0
        if tokens and not category_score and poi.category.lower() in tokens:
            category_score = 2
        tag_score = 0
        for token in tokens:
            tag_score += sum(2 for tag in poi.tags if token in tag.lower())
        return self._score(poi, request) + name_score + category_score + tag_score
