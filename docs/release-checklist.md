# Release Checklist

## Code

- [ ] `pytest` passes
- [ ] `python -m compileall packages apps examples` passes
- [ ] `npm run build:playground` passes
- [ ] no known high-severity dependency vulnerabilities

## Product Surface

- [ ] README matches actual project scope
- [ ] examples still match API behavior
- [ ] `/plan`, `/edit`, `/score` smoke tests pass
- [ ] playground still demonstrates the intended flow

## Open-source Hygiene

- [ ] LICENSE is present
- [ ] CONTRIBUTING, CODE_OF_CONDUCT, SECURITY are present
- [ ] issue templates and PR template are present
- [ ] roadmap and architecture docs are current

## Launch

- [ ] repository description and topics are set on GitHub
- [ ] first release notes are drafted
- [ ] branch protection is configured after initial push
- [ ] a minimal public roadmap exists
