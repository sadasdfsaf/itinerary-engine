from typing import Dict, Iterable, List, Optional

from itinerary_engine.schema.api import ScoreBreakdown
from itinerary_engine.schema.models import Itinerary, PlannedStop, TripRequest


class ItineraryScorer:
    DEFAULT_WEIGHTS = {
        "budget_fit": 1.0,
        "interest_match": 1.0,
        "pacing": 1.0,
        "editability": 1.0,
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        merged = dict(self.DEFAULT_WEIGHTS)
        if weights:
            merged.update(weights)
        self.weights = merged

    def score(self, request: TripRequest, itinerary: Itinerary) -> ScoreBreakdown:
        budget_fit = self._budget_fit(request, itinerary)
        interest_match = self._interest_match(request, itinerary)
        pacing = self._pacing(request, itinerary)
        editability = self._editability(itinerary)
        numerator = (
            (budget_fit * self.weights["budget_fit"])
            + (interest_match * self.weights["interest_match"])
            + (pacing * self.weights["pacing"])
            + (editability * self.weights["editability"])
        )
        denominator = sum(self.weights.values()) or 1.0
        overall = round(numerator / denominator, 2)
        return ScoreBreakdown(
            overall=overall,
            budget_fit=budget_fit,
            interest_match=interest_match,
            pacing=pacing,
            editability=editability,
        )

    def summary(self, scores: ScoreBreakdown) -> List[str]:
        lines = [
            "Budget fit is {0:.0%}.".format(scores.budget_fit),
            "Interest match is {0:.0%}.".format(scores.interest_match),
            "Pacing score is {0:.0%}.".format(scores.pacing),
        ]
        if scores.editability >= 0.8:
            lines.append("Itinerary structure is patch-friendly.")
        return lines

    def _budget_fit(self, request: TripRequest, itinerary: Itinerary) -> float:
        if request.total_budget is None or request.total_budget <= 0:
            return 0.8
        estimated = itinerary.budget_summary.estimated_total
        if estimated <= request.total_budget:
            return 1.0
        overflow = estimated - request.total_budget
        penalty = min(1.0, overflow / request.total_budget)
        return round(max(0.0, 1.0 - penalty), 2)

    def _interest_match(self, request: TripRequest, itinerary: Itinerary) -> float:
        if not request.interests:
            return 0.7
        activity_tags = set()
        for activity in self._activities(itinerary):
            activity_tags.add(activity.poi.category.lower())
            for tag in activity.poi.tags:
                activity_tags.add(tag.lower())
        matched = 0
        for interest in request.interests:
            if interest.lower() in activity_tags:
                matched += 1
        return round(matched / max(1, len(request.interests)), 2)

    def _pacing(self, request: TripRequest, itinerary: Itinerary) -> float:
        expected = {"slow": 2, "balanced": 3, "fast": 4}[request.pace]
        actual = sum(len(day.activities) for day in itinerary.day_plans) / max(1, request.days)
        delta = abs(expected - actual)
        return round(max(0.0, 1.0 - (delta * 0.3)), 2)

    def _editability(self, itinerary: Itinerary) -> float:
        activities = list(self._activities(itinerary))
        if not activities:
            return 0.0
        stable_ids = all(bool(activity.stop_id) for activity in activities)
        evenly_split = all(1 <= len(day.activities) <= 4 for day in itinerary.day_plans)
        score = 0.5
        if stable_ids:
            score += 0.3
        if evenly_split:
            score += 0.2
        return round(min(score, 1.0), 2)

    def _activities(self, itinerary: Itinerary) -> Iterable[PlannedStop]:
        for day in itinerary.day_plans:
            for activity in day.activities:
                yield activity
