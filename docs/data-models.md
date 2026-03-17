# Data Models

The following Pydantic-style models are the v0.1 core contracts. They are intentionally practical rather than exhaustive.

## TripRequest

```python
class TripRequest(BaseModel):
    destination: str
    days: int
    travelers: int = 1
    total_budget: Optional[float] = None
    budget_currency: str = "USD"
    daily_budget_soft_limit: Optional[float] = None
    interests: List[str] = []
    excluded_categories: List[str] = []
    pace: Literal["slow", "balanced", "fast"] = "balanced"
    mobility: Literal["low", "standard", "high"] = "standard"
    with_kids: bool = False
    transport_mode: Literal["walk", "transit", "ride", "mixed"] = "mixed"
    notes: Optional[str] = None
```

## POI

```python
class POI(BaseModel):
    poi_id: str
    name: str
    city: str
    category: str
    district: Optional[str] = None
    tags: List[str] = []
    estimated_cost: float = 0.0
    visit_duration_hours: float = 1.5
    best_time: Literal["morning", "afternoon", "evening", "flexible"] = "flexible"
    indoor: bool = False
    family_friendly: bool = True
    summary: Optional[str] = None
```

## DayPlan

```python
class DayPlan(BaseModel):
    day_index: int
    theme: str
    area_cluster: Optional[str] = None
    activities: List[PlannedStop] = []
    estimated_cost: float = 0.0
    notes: List[str] = []
```

## BudgetSummary

```python
class BudgetSummary(BaseModel):
    currency: str = "USD"
    estimated_total: float = 0.0
    activities_total: float = 0.0
    food_total: float = 0.0
    transport_total: float = 0.0
    buffer_total: float = 0.0
    within_budget: bool = True
```

## Itinerary

```python
class Itinerary(BaseModel):
    itinerary_id: str
    destination: str
    days: int
    summary: str
    assumptions: List[str] = []
    day_plans: List[DayPlan] = []
    budget_summary: BudgetSummary = BudgetSummary()
    tags: List[str] = []
    version: int = 1
```

## EditIntent

```python
class EditIntent(BaseModel):
    action: Literal["replace", "insert", "remove", "move", "slow_down", "tighten_budget"]
    user_instruction: str
    target_day: Optional[int] = None
    target_text: Optional[str] = None
    replacement_text: Optional[str] = None
    source_day: Optional[int] = None
    constraints: List[str] = []
    confidence: float = 0.5
```

## Design Notes

- `TripRequest` is product-facing and should stay compact
- `Itinerary` must contain stable `itinerary_id`, `day_index`, and stop-level IDs for patching
- `EditIntent` should remain typed even if parsed from LLM or rule-based systems
- `BudgetSummary` is approximate in v0.1; it exists to support API and UI contracts early
