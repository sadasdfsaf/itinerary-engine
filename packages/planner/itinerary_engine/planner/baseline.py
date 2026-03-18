from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple, Union

from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.schema.models import (
    POI,
    BudgetSummary,
    DayPlan,
    Itinerary,
    PlannedStop,
    TripRequest,
)


class BaselinePlanner:
    def __init__(self, selector: SimpleCandidateSelector):
        self.selector = selector

    def plan(self, request: TripRequest, candidate_limit: int = 8) -> Itinerary:
        itinerary, _ = self.plan_with_trace(request, candidate_limit=candidate_limit)
        return itinerary

    def plan_with_trace(
        self,
        request: TripRequest,
        candidate_limit: int = 8,
    ) -> Tuple[Itinerary, Dict[str, Union[str, int]]]:
        max_stops = self.max_stops(request)
        needed = max(candidate_limit, request.days * max_stops)
        candidates = self.selector.select(request, limit=needed)
        if not candidates:
            raise ValueError("No candidates available for destination.")

        day_plans: List[DayPlan] = []
        day_stop_counts = self._day_stop_counts(
            day_count=request.days,
            max_stops=max_stops,
            candidate_count=len(candidates),
        )
        cursor = 0
        for day_index, stop_count in enumerate(day_stop_counts, start=1):
            activities: List[PlannedStop] = []
            for slot_index in range(stop_count):
                if cursor < len(candidates):
                    poi = candidates[cursor]
                else:
                    poi = candidates[cursor % len(candidates)]
                cursor += 1
                activities.append(self.make_stop(day_index, slot_index, poi))
            day_plans.append(
                DayPlan(
                    day_index=day_index,
                    theme=self._theme_for(activities),
                    area_cluster=self._area_for(activities),
                    activities=activities,
                    estimated_cost=self.estimate_day_cost(activities),
                    notes=self._notes_for_day(request, activities),
                )
            )

        budget_summary = self.build_budget_summary(day_plans, request)
        itinerary = Itinerary(
            itinerary_id=self._itinerary_id(request),
            destination=request.destination,
            days=request.days,
            summary=self.summarize_request(request),
            assumptions=[
                "Static catalog adapter used",
                "Travel time is heuristic in v0.1",
                "Food and transport estimates are coarse",
            ],
            day_plans=day_plans,
            budget_summary=budget_summary,
            tags=self._itinerary_tags(request),
            version=1,
        )
        return itinerary, {"planner": "baseline", "candidate_count": len(candidates)}

    def max_stops(self, request: TripRequest) -> int:
        if request.pace == "slow":
            return 2
        if request.pace == "fast":
            return 4
        return 3

    def make_stop(self, day_index: int, slot_index: int, poi: POI) -> PlannedStop:
        time_by_slot = ["09:00", "13:00", "18:00", "20:00"]
        start = time_by_slot[slot_index] if slot_index < len(time_by_slot) else None
        return PlannedStop(
            stop_id="d{0}_s{1}_{2}".format(day_index, slot_index + 1, poi.poi_id),
            poi=poi,
            start_time=start,
            rationale="Selected for balance between interests, cost, and day density.",
        )

    def estimate_day_cost(self, activities: Sequence[PlannedStop]) -> float:
        return round(sum(stop.poi.estimated_cost for stop in activities), 2)

    def build_budget_summary(
        self,
        day_plans: Sequence[DayPlan],
        request: TripRequest,
    ) -> BudgetSummary:
        activities_total = round(sum(day.estimated_cost for day in day_plans), 2)
        food_total = round(20 * request.travelers * request.days, 2)
        transport_total = round(10 * request.travelers * request.days, 2)
        estimated_total = round(activities_total + food_total + transport_total, 2)
        budget_limit = (
            request.total_budget if request.total_budget not in (None, 0) else estimated_total
        )
        return BudgetSummary(
            currency=request.budget_currency,
            estimated_total=estimated_total,
            activities_total=activities_total,
            food_total=food_total,
            transport_total=transport_total,
            buffer_total=0.0,
            within_budget=estimated_total <= budget_limit,
        )

    def summarize_request(self, request: TripRequest) -> str:
        interests = ", ".join(request.interests) if request.interests else "general discovery"
        return "A {0} {1}-day plan for {2} focused on {3}.".format(
            request.pace,
            request.days,
            request.destination,
            interests,
        )

    def refresh(self, itinerary: Itinerary, request: TripRequest) -> Itinerary:
        for day_plan in itinerary.day_plans:
            day_plan.theme = self._theme_for(day_plan.activities)
            day_plan.area_cluster = self._area_for(day_plan.activities)
            day_plan.estimated_cost = self.estimate_day_cost(day_plan.activities)
            day_plan.notes = self._notes_for_day(request, day_plan.activities)
        itinerary.summary = self.summarize_request(request)
        itinerary.tags = self._itinerary_tags(request)
        itinerary.budget_summary = self.build_budget_summary(itinerary.day_plans, request)
        return itinerary

    def _theme_for(self, activities: Sequence[PlannedStop]) -> str:
        counter: Counter = Counter()
        for activity in activities:
            counter.update(activity.poi.tags)
        if not counter:
            return "mixed"
        return "{0}-led day".format(counter.most_common(1)[0][0])

    def _area_for(self, activities: Sequence[PlannedStop]) -> Optional[str]:
        districts = [activity.poi.district for activity in activities if activity.poi.district]
        return districts[0] if districts else None

    def _notes_for_day(self, request: TripRequest, activities: Sequence[PlannedStop]) -> List[str]:
        notes = []
        if request.pace == "slow":
            notes.append("Keep transitions loose and leave room for rest.")
        if any(activity.poi.best_time == "evening" for activity in activities):
            notes.append("Reserve evening energy for the final stop.")
        if activities and len(activities) < self.max_stops(request):
            notes.append("Planner reduced stop count to avoid repeating the same POIs too early.")
        return notes

    def _itinerary_tags(self, request: TripRequest) -> List[str]:
        tags = [request.pace, "editable"]
        if request.with_kids:
            tags.append("family")
        return tags

    def _itinerary_id(self, request: TripRequest) -> str:
        slug = request.destination.strip().lower().replace(" ", "_")
        return "trip_{0}_{1}d".format(slug, request.days)

    def _day_stop_counts(self, day_count: int, max_stops: int, candidate_count: int) -> List[int]:
        total_slots = min(day_count * max_stops, candidate_count)
        total_slots = max(day_count, total_slots)
        base, remainder = divmod(total_slots, day_count)
        counts = []
        for day_index in range(day_count):
            counts.append(base + (1 if day_index < remainder else 0))
        return counts
