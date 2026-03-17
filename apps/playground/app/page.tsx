"use client";

import { useState } from "react";
import { JsonPanel } from "../components/json-panel";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const initialItinerary = {
  itinerary_id: "",
  destination: "",
  days: 0,
  summary: "",
  assumptions: [],
  day_plans: [],
  budget_summary: {
    currency: "USD",
    estimated_total: 0,
    activities_total: 0,
    food_total: 0,
    transport_total: 0,
    buffer_total: 0,
    within_budget: true,
  },
  tags: [],
  version: 1,
};

async function requestJson(path: string, payload: unknown) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? "Request failed");
  }
  return data;
}

export default function Page() {
  const [destination, setDestination] = useState("tokyo");
  const [days, setDays] = useState(3);
  const [budget, setBudget] = useState(450);
  const [interests, setInterests] = useState("food,culture,shopping");
  const [instruction, setInstruction] = useState("Replace the museum on day 2 with a food market.");
  const [result, setResult] = useState<unknown>(null);
  const [itinerary, setItinerary] = useState(initialItinerary);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const tripRequest = {
    destination,
    days,
    total_budget: budget,
    interests: interests
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    pace: "balanced",
  };

  async function handlePlan() {
    setLoading("plan");
    setError(null);
    try {
      const data = await requestJson("/plan", { trip_request: tripRequest });
      setResult(data);
      setItinerary(data.itinerary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(null);
    }
  }

  async function handleEdit() {
    setLoading("edit");
    setError(null);
    try {
      const data = await requestJson("/edit", {
        trip_request: tripRequest,
        itinerary,
        instruction,
      });
      setResult(data);
      setItinerary(data.itinerary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(null);
    }
  }

  async function handleScore() {
    setLoading("score");
    setError(null);
    try {
      const data = await requestJson("/score", {
        trip_request: tripRequest,
        itinerary,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(null);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">developer-first runtime</p>
        <h1>itinerary-engine playground</h1>
        <p className="lede">
          Generate a structured trip, patch it with a natural-language instruction, and score the
          updated itinerary without regenerating everything.
        </p>
      </section>

      <section className="workspace">
        <section className="panel control-panel">
          <div className="panel-header">
            <p className="eyebrow">input</p>
            <h2>Trip request</h2>
          </div>

          <label>
            <span>Destination</span>
            <input value={destination} onChange={(event) => setDestination(event.target.value)} />
          </label>

          <label>
            <span>Days</span>
            <input
              type="number"
              min={1}
              max={14}
              value={days}
              onChange={(event) => setDays(Number(event.target.value))}
            />
          </label>

          <label>
            <span>Budget</span>
            <input
              type="number"
              min={0}
              value={budget}
              onChange={(event) => setBudget(Number(event.target.value))}
            />
          </label>

          <label>
            <span>Interests</span>
            <input value={interests} onChange={(event) => setInterests(event.target.value)} />
          </label>

          <label>
            <span>Edit instruction</span>
            <textarea
              rows={4}
              value={instruction}
              onChange={(event) => setInstruction(event.target.value)}
            />
          </label>

          <div className="actions">
            <button onClick={handlePlan} disabled={Boolean(loading)}>
              {loading === "plan" ? "Planning..." : "POST /plan"}
            </button>
            <button onClick={handleEdit} disabled={Boolean(loading) || !itinerary.itinerary_id}>
              {loading === "edit" ? "Editing..." : "POST /edit"}
            </button>
            <button onClick={handleScore} disabled={Boolean(loading) || !itinerary.itinerary_id}>
              {loading === "score" ? "Scoring..." : "POST /score"}
            </button>
          </div>

          {error ? <p className="error">{error}</p> : null}
        </section>

        <section className="results">
          <JsonPanel title="TripRequest" data={tripRequest} />
          <JsonPanel title="Latest response" data={result ?? { message: "Run /plan first." }} />
        </section>
      </section>
    </main>
  );
}
