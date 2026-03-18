from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    destination: str = Field(..., min_length=1)
    days: int = Field(..., ge=1, le=30)
    travelers: int = Field(default=1, ge=1, le=10)
    total_budget: Optional[float] = Field(default=None, ge=0)
    budget_currency: str = Field(default="USD", min_length=3, max_length=3)
    daily_budget_soft_limit: Optional[float] = Field(default=None, ge=0)
    interests: List[str] = Field(default_factory=list)
    excluded_categories: List[str] = Field(default_factory=list)
    pace: Literal["slow", "balanced", "fast"] = "balanced"
    mobility: Literal["low", "standard", "high"] = "standard"
    with_kids: bool = False
    transport_mode: Literal["walk", "transit", "ride", "mixed"] = "mixed"
    notes: Optional[str] = None

    @property
    def has_budget(self) -> bool:
        return self.total_budget is not None and self.total_budget > 0


class POI(BaseModel):
    poi_id: str
    name: str
    city: str
    category: Literal[
        "landmark",
        "food",
        "museum",
        "park",
        "shopping",
        "neighborhood",
        "activity",
    ]
    district: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    estimated_cost: float = Field(default=0.0, ge=0)
    visit_duration_hours: float = Field(default=1.5, ge=0.5, le=8)
    best_time: Literal["morning", "afternoon", "evening", "flexible"] = "flexible"
    indoor: bool = False
    family_friendly: bool = True
    summary: Optional[str] = None


class PlannedStop(BaseModel):
    stop_id: str
    poi: POI
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    rationale: Optional[str] = None


class DayPlan(BaseModel):
    day_index: int = Field(..., ge=1)
    theme: str
    area_cluster: Optional[str] = None
    activities: List[PlannedStop] = Field(default_factory=list)
    estimated_cost: float = Field(default=0.0, ge=0)
    notes: List[str] = Field(default_factory=list)


class BudgetSummary(BaseModel):
    currency: str = "USD"
    estimated_total: float = Field(default=0.0, ge=0)
    activities_total: float = Field(default=0.0, ge=0)
    food_total: float = Field(default=0.0, ge=0)
    transport_total: float = Field(default=0.0, ge=0)
    buffer_total: float = Field(default=0.0, ge=0)
    within_budget: bool = True


class Itinerary(BaseModel):
    itinerary_id: str
    destination: str
    days: int = Field(..., ge=1)
    summary: str
    assumptions: List[str] = Field(default_factory=list)
    day_plans: List[DayPlan] = Field(default_factory=list)
    budget_summary: BudgetSummary = Field(default_factory=BudgetSummary)
    tags: List[str] = Field(default_factory=list)
    version: int = Field(default=1, ge=1)


class EditIntent(BaseModel):
    action: Literal["replace", "insert", "remove", "move", "slow_down", "tighten_budget"]
    user_instruction: str
    target_day: Optional[int] = Field(default=None, ge=1)
    target_text: Optional[str] = None
    replacement_text: Optional[str] = None
    source_day: Optional[int] = Field(default=None, ge=1)
    constraints: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
