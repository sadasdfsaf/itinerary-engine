from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .models import EditIntent, Itinerary, TripRequest


class ScoreBreakdown(BaseModel):
    overall: float = Field(..., ge=0, le=1)
    budget_fit: float = Field(..., ge=0, le=1)
    interest_match: float = Field(..., ge=0, le=1)
    pacing: float = Field(..., ge=0, le=1)
    editability: float = Field(..., ge=0, le=1)


class PlanRequest(BaseModel):
    trip_request: TripRequest
    candidate_limit: int = Field(default=8, ge=3, le=20)


class PlanResponse(BaseModel):
    itinerary: Itinerary
    scores: ScoreBreakdown
    trace: Dict[str, Any] = Field(default_factory=dict)


class EditRequest(BaseModel):
    trip_request: TripRequest
    itinerary: Itinerary
    instruction: str = Field(..., min_length=1)


class EditResponse(BaseModel):
    edit_intent: EditIntent
    itinerary: Itinerary
    affected_days: List[int] = Field(default_factory=list)
    scores: ScoreBreakdown


class ScoreRequest(BaseModel):
    trip_request: TripRequest
    itinerary: Itinerary


class ScoreResponse(BaseModel):
    scores: ScoreBreakdown
    summary: List[str] = Field(default_factory=list)
