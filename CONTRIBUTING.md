# Contributing

Thanks for contributing to `itinerary-engine`.

## What We Want

- Schema improvements that preserve backward compatibility where possible
- Better ranking, patching, and evaluation logic
- Adapters that reduce provider lock-in
- Benchmarks, datasets, and reproducible examples
- Documentation that helps developers ship with confidence

## Development Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]

npm install
```

Run the API:

```bash
python -m uvicorn app.main:app --app-dir apps/api-server --reload
```

Run the playground:

```bash
npm run dev:playground
```

## Contribution Rules

- Keep schema changes explicit and documented
- Do not couple core packages to a single LLM, map, or booking provider
- Add examples when you add a new public interface
- Prefer deterministic fallbacks over hidden prompt magic
- Keep patches local: an edit should not silently rewrite the whole trip unless required

## Pull Request Checklist

- Clear problem statement
- Small and reviewable scope
- Updated docs if public behavior changed
- Example payloads or screenshots when relevant
- Notes on compatibility or migration if schema changed

## Issues

Open an issue for:

- bug reports
- missing adapter capabilities
- evaluation gaps
- roadmap proposals
- schema or API ergonomics problems
