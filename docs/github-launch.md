# GitHub Launch Notes

## Suggested Repository Description

Editable itinerary runtime for developer products: schema, planner, patcher, adapters, evaluator.

## Suggested Topics

- itinerary
- travel-tech
- ai-runtime
- fastapi
- nextjs
- planner
- patch-engine
- developer-tools
- open-source
- pydantic

## Suggested Social Preview Copy

Open-source editable itinerary engine for developers. Generate structured trips, parse natural-language edits, patch impacted days, and score itinerary quality.

## Suggested First Release

### Tag

`v0.1.0`

### Title

`v0.1.0: editable itinerary runtime baseline`

### Release Notes

```markdown
## Highlights

- Stable `TripRequest` and `Itinerary` schemas
- Baseline multi-day planner
- Rule-based natural-language edit intent parser
- Partial replan patch engine
- FastAPI reference server with `/plan`, `/edit`, `/score`
- Next.js playground
- Docs, examples, CI, and tests

## Scope

This release is intentionally small. It establishes the runtime boundaries:
schema, planner, patcher, adapters, evaluator, and serving layer.

## Non-goals

- booking
- maps stack
- generic multi-agent orchestration
- polished consumer travel app
```

## GitHub Repo Settings Checklist

- Set default branch to `main`
- Enable Discussions
- Enable Issues
- Enable Security Advisories
- Require PR review before merge once maintainers grow
- Protect `main` after the initial bootstrap
