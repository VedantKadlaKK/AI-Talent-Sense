# Module 5 Development Report: Signal Engine

Date: 2026-07-02

## Scope Completed

- Added signal definition and signal result persistence:
  - `signals`
  - `signal_results`
- Added Alembic migration `0005_create_signals`.
- Implemented 20 representative signals from the blueprint:
  - Skill Match
  - Experience Match
  - Education Match
  - Certification Match
  - Project Match
  - Domain Match
  - Location Match
  - Career Growth
  - Resume Quality
  - GitHub Activity
  - Portfolio Quality
  - Employment Stability
  - Keyword Match
  - Technology Freshness
  - Leadership
  - Communication
  - Open Source Activity
  - Company Relevance
  - Role Seniority
  - Availability
- Added configurable default signal weights through seeded signal definitions.
- Implemented deterministic signal evaluation over:
  - Job description intelligence
  - Sourced candidate profile data
  - Normalized candidate intelligence
  - Candidate source coverage
- Stored each signal result with:
  - Score
  - Weight
  - Contribution
  - Reason
- Added Signal Engine APIs:
  - `GET /signals`
  - `POST /jobs/{job_id}/evaluate-signals`
  - `GET /jobs/{job_id}/signal-results`
- Added backend API tests for default signals, signal evaluation, repeated evaluation upsert behavior, and missing-job handling.
- Added frontend support to evaluate candidate signals from Job Details.
- Added frontend signal breakdown cards showing top signal contributions and reasons.
- Updated README capabilities to reflect Module 5 completion.

## Key Files

- Signal models: `backend/api/models/signal.py`
- Signal schemas: `backend/api/schemas/signal.py`
- Signal repository: `backend/api/repositories/signal_repository.py`
- Signal engine service: `backend/api/services/signal_engine_service.py`
- Signal routes: `backend/api/api/routes/signals.py`
- Migration: `backend/alembic/versions/0005_create_signals.py`
- Backend tests: `backend/tests/test_jobs_api.py`
- Frontend API client: `frontend/src/api.ts`
- Frontend types: `frontend/src/types.ts`
- Frontend job details UI: `frontend/src/App.tsx`

## Verification

Completed:

- `npm.cmd run lint`
- `npm.cmd run build`

Not completed locally:

- Backend pytest execution. `py -m pytest` reports that no Python installation is available, and `python` is not on PATH in this environment.

## Current Limitations

- Signal scoring is deterministic and rule-based. This is intentional for explainability and repeatable local demos.
- Signal weights are stored and configurable in the database, but no admin UI exists yet for editing them.
- Module 5 stores weighted contributions, but does not compute final ranking. Final weighted scoring and ranking belong to Module 6.
- Some signals use inferred evidence from mocked connectors until real integrations and richer resume parsing are added.

## Next Module

Module 6: Weighted Scoring.

Planned next work:

- Aggregate signal contributions into final candidate scores.
- Store recommendations with overall score and rank.
- Respect configurable signal weights.
- Prepare ranking data for the dashboard and explainable AI module.
