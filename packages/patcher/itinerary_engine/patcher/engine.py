from copy import deepcopy
from typing import List, Optional, Tuple

from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import (
    POI,
    DayPlan,
    EditIntent,
    Itinerary,
    PlannedStop,
    TripRequest,
)


class PatchConflictError(ValueError):
    pass


class PatchEngine:
    def __init__(self, selector: SimpleCandidateSelector, planner: BaselinePlanner):
        self.selector = selector
        self.planner = planner

    def apply(
        self,
        itinerary: Itinerary,
        intent: EditIntent,
        request: TripRequest,
    ) -> Tuple[Itinerary, List[int]]:
        updated = deepcopy(itinerary)
        affected_days: List[int] = []

        if intent.action == "remove":
            affected_days = self._remove(updated, intent)
        elif intent.action == "replace":
            affected_days = self._replace(updated, intent, request)
        elif intent.action == "insert":
            affected_days = self._insert(updated, intent, request)
        elif intent.action == "move":
            affected_days = self._move(updated, intent)
        elif intent.action == "slow_down":
            affected_days = self._slow_down(updated, request)
        elif intent.action == "tighten_budget":
            affected_days = self._tighten_budget(updated, request)
        else:
            raise PatchConflictError("Unsupported edit action.")

        if not affected_days:
            return updated, []
        self._repair_days(updated, request, affected_days)
        updated.version += 1
        self.planner.refresh(updated, request)
        return updated, sorted(set(affected_days))

    def _remove(self, itinerary: Itinerary, intent: EditIntent) -> List[int]:
        stop, day = self._find_stop(itinerary, intent.target_text, intent.target_day)
        if not stop or day is None:
            raise PatchConflictError("Target activity not found for removal.")
        day_plan = itinerary.day_plans[day - 1]
        day_plan.activities = [item for item in day_plan.activities if item.stop_id != stop.stop_id]
        return [day]

    def _replace(self, itinerary: Itinerary, intent: EditIntent, request: TripRequest) -> List[int]:
        stop, day = self._find_stop(itinerary, intent.target_text, intent.target_day)
        if not stop or day is None:
            raise PatchConflictError("Target activity not found for replacement.")
        day_plan = itinerary.day_plans[day - 1]
        replacement = self._resolve_replacement(
            request,
            intent.replacement_text,
            exclude_ids=[activity.poi.poi_id for activity in day_plan.activities],
        )
        for index, item in enumerate(day_plan.activities):
            if item.stop_id == stop.stop_id:
                day_plan.activities[index] = self.planner.make_stop(day, index, replacement)
                break
        return [day]

    def _insert(self, itinerary: Itinerary, intent: EditIntent, request: TripRequest) -> List[int]:
        target_day = intent.target_day or 1
        if target_day < 1 or target_day > len(itinerary.day_plans):
            raise PatchConflictError("Target day is out of range.")
        replacement = self._resolve_replacement(request, intent.replacement_text)
        day_plan = itinerary.day_plans[target_day - 1]
        day_plan.activities.append(
            self.planner.make_stop(target_day, len(day_plan.activities), replacement)
        )
        return [target_day]

    def _move(self, itinerary: Itinerary, intent: EditIntent) -> List[int]:
        stop, source_day = self._find_stop(itinerary, intent.target_text, intent.source_day)
        if not stop or source_day is None:
            raise PatchConflictError("Target activity not found for move.")
        target_day = intent.target_day
        if target_day is None or target_day < 1 or target_day > len(itinerary.day_plans):
            raise PatchConflictError("Target day is out of range.")
        if source_day == target_day:
            return []
        source_plan = itinerary.day_plans[source_day - 1]
        target_plan = itinerary.day_plans[target_day - 1]
        source_plan.activities = [
            item for item in source_plan.activities if item.stop_id != stop.stop_id
        ]
        target_plan.activities.append(
            self.planner.make_stop(target_day, len(target_plan.activities), stop.poi)
        )
        return [source_day, target_day]

    def _slow_down(self, itinerary: Itinerary, request: TripRequest) -> List[int]:
        target_count = max(2, self.planner.max_stops(request) - 1)
        affected = []
        for day_plan in itinerary.day_plans:
            if len(day_plan.activities) > target_count:
                day_plan.activities = day_plan.activities[:target_count]
                affected.append(day_plan.day_index)
        return affected

    def _tighten_budget(self, itinerary: Itinerary, request: TripRequest) -> List[int]:
        affected = []
        for day_plan in itinerary.day_plans:
            if not day_plan.activities:
                continue
            expensive = max(day_plan.activities, key=lambda item: item.poi.estimated_cost)
            cheaper_options = self.selector.find_best_match(
                request,
                expensive.poi.category,
                limit=3,
                exclude_ids=[activity.poi.poi_id for activity in day_plan.activities],
            )
            cheaper_options = [
                poi
                for poi in cheaper_options
                if poi.estimated_cost < expensive.poi.estimated_cost
            ]
            if cheaper_options:
                cheaper = cheaper_options[0]
                for index, item in enumerate(day_plan.activities):
                    if item.stop_id == expensive.stop_id:
                        day_plan.activities[index] = self.planner.make_stop(
                            day_plan.day_index,
                            index,
                            cheaper,
                        )
                        affected.append(day_plan.day_index)
                        break
        return affected

    def _repair_days(
        self,
        itinerary: Itinerary,
        request: TripRequest,
        affected_days: List[int],
    ) -> None:
        for day_index in sorted(set(affected_days)):
            day_plan = itinerary.day_plans[day_index - 1]
            if not day_plan.activities:
                fallback = self.selector.select(request, limit=1)
                if fallback:
                    day_plan.activities = [self.planner.make_stop(day_index, 0, fallback[0])]
            self._reindex_day(day_plan)

    def _reindex_day(self, day_plan: DayPlan) -> None:
        rebuilt = []
        for index, activity in enumerate(day_plan.activities):
            refreshed = self.planner.make_stop(day_plan.day_index, index, activity.poi)
            rebuilt.append(
                PlannedStop(
                    stop_id="d{0}_s{1}_{2}".format(
                        day_plan.day_index,
                        index + 1,
                        activity.poi.poi_id,
                    ),
                    poi=activity.poi,
                    start_time=refreshed.start_time,
                    end_time=activity.end_time,
                    rationale=activity.rationale or refreshed.rationale,
                )
            )
        day_plan.activities = rebuilt

    def _find_stop(
        self,
        itinerary: Itinerary,
        target_text: Optional[str],
        preferred_day: Optional[int],
    ) -> Tuple[Optional[PlannedStop], Optional[int]]:
        if not target_text:
            return None, None
        query = target_text.strip().lower()
        day_plans = itinerary.day_plans
        if preferred_day:
            if preferred_day < 1 or preferred_day > len(itinerary.day_plans):
                return None, None
            day_plans = [itinerary.day_plans[preferred_day - 1]]
        for day_plan in day_plans:
            for activity in day_plan.activities:
                haystack = " ".join(
                    [
                        activity.poi.name.lower(),
                        activity.poi.category.lower(),
                        " ".join(activity.poi.tags).lower(),
                    ]
                )
                if query in haystack:
                    return activity, day_plan.day_index
        return None, None

    def _resolve_replacement(
        self,
        request: TripRequest,
        replacement_text: Optional[str],
        exclude_ids: Optional[List[str]] = None,
    ) -> POI:
        if not replacement_text:
            raise PatchConflictError("Replacement text is required for this edit.")
        matches = self.selector.find_best_match(
            request,
            replacement_text,
            limit=1,
            exclude_ids=exclude_ids,
        )
        if matches:
            return matches[0]
        raise PatchConflictError("No suitable replacement candidate found.")
