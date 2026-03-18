# itinerary-engine

> Editable itinerary runtime for developer products.  
> 面向开发者的可编辑旅行行程引擎。

`itinerary-engine` is an open-source runtime for generating, editing, patching, and scoring structured travel itineraries. It is designed for builders who need a stable itinerary core behind web apps, mini-programs, internal tools, and APIs.

`itinerary-engine` 是一个开源的结构化旅行行程 runtime，核心能力是“生成、编辑、局部重排、评分”。它面向开发者，用作 Web、小程序、API、内部系统的底层行程引擎。

## Core Capabilities | 核心能力

- Structured `TripRequest` and `Itinerary` schemas
- Baseline planner for multi-day itinerary generation
- Natural-language edit parsing into typed edit intents
- Partial replan / patch engine instead of full regeneration
- Provider adapters for POI catalogs, ranking, and future LLM integrations
- Evaluator layer for budget, pacing, and preference alignment

## Why This Project | 为什么要做这个项目

Most travel AI demos stop at chat output. They do not expose a stable schema, edit semantics, patch boundaries, or evaluation hooks. That makes them hard to integrate into products.

大多数“AI 旅行规划”项目最后都停留在聊天文本 demo，缺少稳定 schema、编辑语义、局部 patch 机制和评测层，导致它们无法真正成为产品底层。

`itinerary-engine` focuses on the missing runtime layer:

- not a booking platform
- not a map stack
- not a generic multi-agent framework
- not a thin wrapper around a chat UI

## Use Cases | 适用场景

- Build a travel planning API for SaaS or internal tools
- Provide editable itinerary generation in a consumer app
- Power a mini-program where users tweak one day at a time
- Run itinerary quality evaluation pipelines offline
- Compare providers behind a unified adapter interface

## Quick Example | 快速示例

```python
from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.models import TripRequest

request = TripRequest(
    destination="tokyo",
    days=3,
    total_budget=450,
    interests=["food", "culture", "shopping"],
    pace="balanced",
)

selector = SimpleCandidateSelector(StaticCatalogAdapter())
planner = BaselinePlanner(selector)
itinerary = planner.plan(request)

print(itinerary.summary)
print(itinerary.day_plans[0].activities[0].poi.name)
```

API example:

```bash
curl -X POST http://127.0.0.1:8000/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"trip_request\":{\"destination\":\"tokyo\",\"days\":3,\"total_budget\":450,\"interests\":[\"food\",\"culture\"]}}"
```

## v0.1 Scope | v0.1 范围

- Stable request and itinerary schemas
- Rule-based candidate selection
- Baseline planner
- Rule-based edit intent parser
- Patch engine with partial replan for impacted day(s)
- FastAPI server with `/plan`, `/edit`, `/score`
- Next.js playground for local product demos
- Example payloads and architecture docs

## Roadmap | 路线图

- v0.1: single-destination baseline runtime
- v0.2: richer adapter contracts, ranking signals, constraint bundles
- v0.3: map-aware travel time estimation and benchmarking harness
- v0.4: provider comparison, offline datasets, regression suites

See [docs/roadmap.md](docs/roadmap.md) and [docs/architecture.md](docs/architecture.md).

## Non-goals | 非目标

- Booking, inventory, or payments
- Full GIS or map rendering infrastructure
- Generic agent orchestration framework
- Consumer-facing polished travel app
- Blind full-regeneration on every edit

## Repository Layout | 仓库结构

See [docs/architecture.md](docs/architecture.md) for the full monorepo layout and module responsibilities.

## Docs | 文档

- [Project overview / 项目总览](docs/project-overview.md)
- [Architecture / 架构设计](docs/architecture.md)
- [Data models / 核心数据结构](docs/data-models.md)
- [API / 接口设计](docs/api.md)
- [Roadmap / 路线图](docs/roadmap.md)
- [GitHub launch / 首发设置](docs/github-launch.md)
- [Release checklist / 发布清单](docs/release-checklist.md)
- [Pitfalls / 易失败点](docs/pitfalls.md)

## Getting Started | 启动方式

Python API:

```bash
python -m pip install -e .[dev]
python -m uvicorn app.main:app --app-dir apps/api-server --reload
```

Playground:

```bash
npm install
npm run dev:playground
```

## License | 许可证

Apache-2.0. See [LICENSE](LICENSE).

## Contributing | 参与贡献

Issues and PRs are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md).
