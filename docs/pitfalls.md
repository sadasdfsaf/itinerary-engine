# Top 10 Failure Modes

## 1. Turning the project into a demo instead of a framework

If most energy goes into UI polish and chat tone, the engine layer will stay weak. Keep the playground secondary.

## 2. Unstable schema

If `TripRequest` and `Itinerary` change every week, nobody can build on top of the project safely.

## 3. Weak patch engine

If every edit triggers full regeneration, the project loses its main differentiation.

## 4. README reads like product marketing

Developers adopt repos that expose architecture, boundaries, examples, and tradeoffs quickly.

## 5. Name is too generic or too vague

A weak repository name reduces searchability and makes positioning harder.

## 6. No examples

Without ready-to-run payloads, contributors cannot understand the intended data flow.

## 7. No benchmark or evaluation layer

Planning quality becomes subjective and hard to improve over time.

## 8. Monorepo structure is messy

If parser, planner, adapters, and demo code blur together, extensibility collapses early.

## 9. Hard-binding to one provider

If the core assumes one map, POI, or LLM vendor, open-source value drops sharply.

## 10. Open-source and commercial boundary is unclear

If maintainers cannot explain what stays open and what might be hosted/commercial later, trust erodes.

## Mitigation Rule

Every release should answer five questions clearly:

- What is the schema contract?
- What edits are actually supported?
- What is deterministic vs provider-dependent?
- What adapters exist?
- How do we measure quality?
