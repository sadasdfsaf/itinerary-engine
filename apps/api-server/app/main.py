# ruff: noqa: E402

from app.bootstrap import bootstrap_workspace

bootstrap_workspace()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from itinerary_engine.adapters.catalog import StaticCatalogAdapter
from itinerary_engine.candidate_selector.simple import SimpleCandidateSelector
from itinerary_engine.edit_parser.rule_based import EditParseError, RuleBasedEditParser
from itinerary_engine.evaluator.scorer import ItineraryScorer
from itinerary_engine.patcher.engine import PatchConflictError, PatchEngine
from itinerary_engine.planner.baseline import BaselinePlanner
from itinerary_engine.schema.api import (
    EditRequest,
    EditResponse,
    PlanRequest,
    PlanResponse,
    ScoreRequest,
    ScoreResponse,
)

app = FastAPI(
    title="itinerary-engine API",
    version="0.1.0",
    description="Developer-first runtime for structured itinerary planning, editing, and scoring.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

adapter = StaticCatalogAdapter()
selector = SimpleCandidateSelector(adapter)
planner = BaselinePlanner(selector)
parser = RuleBasedEditParser()
patcher = PatchEngine(selector, planner)
scorer = ItineraryScorer()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "itinerary-engine"}


@app.post("/plan", response_model=PlanResponse)
def plan(payload: PlanRequest) -> PlanResponse:
    try:
        itinerary, trace = planner.plan_with_trace(
            payload.trip_request,
            candidate_limit=payload.candidate_limit,
        )
        scores = scorer.score(payload.trip_request, itinerary)
        return PlanResponse(itinerary=itinerary, scores=scores, trace=trace)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post("/edit", response_model=EditResponse)
def edit(payload: EditRequest) -> EditResponse:
    try:
        intent = parser.parse(payload.instruction)
        itinerary, affected_days = patcher.apply(payload.itinerary, intent, payload.trip_request)
        scores = scorer.score(payload.trip_request, itinerary)
        return EditResponse(
            edit_intent=intent,
            itinerary=itinerary,
            affected_days=affected_days,
            scores=scores,
        )
    except EditParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PatchConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.post("/score", response_model=ScoreResponse)
def score(payload: ScoreRequest) -> ScoreResponse:
    scores = scorer.score(payload.trip_request, payload.itinerary)
    return ScoreResponse(scores=scores, summary=scorer.summary(scores))
