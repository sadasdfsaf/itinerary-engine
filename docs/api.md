# API Design

## `POST /plan`

### Request schema

```json
{
  "trip_request": {
    "destination": "tokyo",
    "days": 3,
    "total_budget": 450,
    "interests": ["food", "culture", "shopping"],
    "pace": "balanced"
  }
}
```

### Response schema

```json
{
  "itinerary": {},
  "scores": {
    "overall": 0.95,
    "budget_fit": 1.0,
    "interest_match": 1.0,
    "pacing": 0.8,
    "editability": 1.0
  },
  "trace": {
    "planner": "baseline",
    "candidate_count": 7
  }
}
```

### Example response

```json
{
  "itinerary": {
    "itinerary_id": "trip_tokyo_3d",
    "destination": "tokyo",
    "days": 3,
    "summary": "A balanced 3-day plan for tokyo focused on food, culture, shopping.",
    "assumptions": [
      "Static catalog adapter used",
      "Travel time is heuristic in v0.1",
      "Food and transport estimates are coarse"
    ],
    "day_plans": [],
    "budget_summary": {
      "currency": "USD",
      "estimated_total": 210.0,
      "activities_total": 120.0,
      "food_total": 60.0,
      "transport_total": 30.0,
      "buffer_total": 0.0,
      "within_budget": true
    },
    "tags": ["balanced", "editable"],
    "version": 1
  },
  "scores": {
    "overall": 0.95,
    "budget_fit": 1.0,
    "interest_match": 1.0,
    "pacing": 0.8,
    "editability": 1.0
  },
  "trace": {
    "planner": "baseline",
    "candidate_count": 7
  }
}
```

### Possible errors

- `400` invalid request body
- `422` schema validation failed
- `503` candidate provider unavailable

## `POST /edit`

### Request schema

```json
{
  "trip_request": {
    "destination": "tokyo",
    "days": 3,
    "total_budget": 450,
    "interests": ["food", "culture", "shopping"]
  },
  "itinerary": {},
  "instruction": "Replace the museum on day 2 with a food market."
}
```

### Response schema

```json
{
  "edit_intent": {},
  "itinerary": {},
  "affected_days": [2],
  "scores": {}
}
```

### Example response

```json
{
  "edit_intent": {
    "action": "replace",
    "user_instruction": "Replace the museum on day 2 with a food market.",
    "target_day": 2,
    "target_text": "museum",
    "replacement_text": "food market",
    "source_day": null,
    "constraints": [],
    "confidence": 0.91
  },
  "itinerary": {
    "itinerary_id": "trip_tokyo_3d",
    "version": 2
  },
  "affected_days": [2],
  "scores": {
    "overall": 0.95,
    "budget_fit": 1.0,
    "interest_match": 1.0,
    "pacing": 0.8,
    "editability": 1.0
  }
}
```

### Possible errors

- `400` instruction missing
- `409` edit conflict or target not found
- `422` schema validation failed

## `POST /score`

### Request schema

```json
{
  "trip_request": {
    "destination": "tokyo",
    "days": 3,
    "total_budget": 450,
    "interests": ["food", "culture", "shopping"]
  },
  "itinerary": {}
}
```

### Response schema

```json
{
  "scores": {
    "overall": 0.95,
    "budget_fit": 1.0,
    "interest_match": 1.0,
    "pacing": 0.8,
    "editability": 1.0
  },
  "summary": [
    "Budget fit is 100%.",
    "Interest match is 100%.",
    "Pacing score is 80%.",
    "Itinerary structure is patch-friendly."
  ]
}
```

### Possible errors

- `400` itinerary missing
- `422` schema validation failed

## Error shape

```json
{
  "detail": "human-readable message"
}
```
