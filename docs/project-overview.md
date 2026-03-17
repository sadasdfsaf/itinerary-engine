# Project Overview

## 1. One-line Positioning

`itinerary-engine` is a developer-first open-source runtime for generating, editing, patching, and evaluating structured travel itineraries.

## 2. Core Value

- Turn itinerary generation from unstructured chat output into a stable runtime primitive
- Expose clear schema boundaries for API, web, and mini-program integration
- Support local edits and partial replan instead of full regeneration
- Keep provider integrations behind adapters so the core remains portable
- Make itinerary quality measurable with evaluator hooks

## 3. Suitable Scenarios

- Travel SaaS backend
- AI trip planning API
- Consumer app itinerary editor
- Mini-program day-by-day trip builder
- Internal operations tooling for destination content teams
- Offline evaluation and provider comparison pipelines

## 4. How It Differs

### Versus a generic agent framework

- The primary abstraction is `itinerary`, not `agent`
- Focuses on schemas, patch semantics, and scoring contracts
- Optimized for deterministic interfaces and product integration
- Does not try to orchestrate arbitrary tools or role-playing workflows

### Versus a travel demo app

- Prioritizes engine modularity over polished end-user UX
- Exposes reusable planner, parser, patcher, evaluator, and adapters
- Keeps the playground as a demo surface, not the product itself
- Treats editability as a core invariant, not a UI trick

## 5. Why This Project Should Be Open Source

- The ecosystem lacks a neutral itinerary runtime layer
- Developer teams need a portable core that is not tied to one vendor
- Schema and evaluation should be reviewable in public
- Open examples lower adoption friction for API and app builders
- A public adapter model creates a healthier extension ecosystem

## 6. Repository Name Suggestions

| Candidate | Comment |
| --- | --- |
| `itinerary-engine` | Best long-term brand. Short, stable, and broad enough for future expansion. |
| `editable-itinerary-engine` | Best for search and传播. It directly communicates the differentiated idea. |
| `trip-runtime` | Strong technical flavor, but slightly abstract for travel-specific discovery. |
| `itinerary-core` | Good for developers, but weaker as a public brand. |
| `open-itinerary` | Memorable, but less precise about being an engine/runtime. |

### Recommended picks

- Best long-term brand: `itinerary-engine`
- Best for search and传播: `editable-itinerary-engine`
- Best for first-glance comprehension: `editable-itinerary-engine`

## 7. License Recommendation

| License | Pros | Cons | Fit for this project |
| --- | --- | --- | --- |
| Apache-2.0 | Permissive, explicit patent grant, enterprise friendly | Slightly longer and more formal than MIT | Best default |
| MIT | Extremely simple, highly adopted | Weaker patent story, less explicit legal guardrails | Good but not ideal |
| AGPL-3.0 | Strong copyleft even for network services | Significantly reduces adoption by infra/product teams | Too restrictive for a runtime layer |

### Final recommendation

Use `Apache-2.0`.

Reason:

- This project is infrastructure-like and should maximize adoption
- Patent grant matters more here than in a tiny utility library
- It preserves room for commercial usage without forcing closed forks to reveal service code
