# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on Keep a Changelog, and the project follows SemVer from `v0.1.0`.

## [0.1.0] - 2026-03-18

Initial public release of `itinerary-engine`.

### Added

- Monorepo structure for `schema`, `planner`, `candidate_selector`, `edit_parser`, `patcher`, `evaluator`, `adapters`, `api-server`, and `playground`.
- Pydantic schemas for `TripRequest`, `Itinerary`, `BudgetSummary`, `POI`, `DayPlan`, and `EditIntent`.
- FastAPI endpoints for `POST /plan`, `POST /edit`, and `POST /score`.
- Next.js playground for interactive planning, editing, and scoring demos.
- CI workflow, issue templates, PR template, security policy, and contributing docs.

### Changed

- Promoted `itinerary-engine` to a public GitHub repository with Apache-2.0 licensing and release metadata.
- Added a project changelog, Dependabot configuration, and CodeQL analysis workflow for long-term maintenance.

### Fixed

- Removed duplicate candidate selection in `/plan` by routing through planner trace output.
- Hardened patch flows for out-of-range day edits, same-day moves, partial replan edge cases, and note refresh behavior.
- Fixed pacing, budget, and replacement selection logic that could degrade itinerary quality.
- Reduced planner repetition and improved test harness coverage for the monorepo layout.
