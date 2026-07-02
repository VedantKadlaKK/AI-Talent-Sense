# Module 4 Development Report: Candidate Intelligence

Date: 2026-07-02

## Scope Completed

- Added explicit Candidate Intelligence service boundaries.
- Extended canonical candidate profiles with normalized intelligence fields:
  - Normalized summary
  - Source coverage
  - Resume insights
  - GitHub insights
  - Portfolio insights
  - API/source insights
  - Normalization timestamp
- Added Alembic migration `0004_add_candidate_intelligence`.
- Implemented single-candidate normalization:
  - `POST /candidates/{candidate_id}/normalize`
- Implemented job-level batch normalization:
  - `POST /jobs/{job_id}/normalize-candidates`
- Preserved existing sourced profile data while adding derived normalized fields.
- Added source coverage completeness for downstream scoring.
- Added backend API tests for batch normalization, single-candidate normalization, and missing entity handling.
- Added frontend support to normalize sourced candidate profiles from Job Details.
- Added frontend display for normalized profile status, coverage, and candidate intelligence summary.
- Updated README capabilities to reflect Module 4 completion.

## Key Files

- Candidate model: `backend/api/models/candidate.py`
- Candidate schemas: `backend/api/schemas/candidate.py`
- Candidate repository: `backend/api/repositories/candidate_repository.py`
- Candidate intelligence service: `backend/api/services/candidate_intelligence_service.py`
- Candidate routes: `backend/api/api/routes/candidates.py`
- Migration: `backend/alembic/versions/0004_add_candidate_intelligence.py`
- Frontend API client: `frontend/src/api.ts`
- Frontend types: `frontend/src/types.ts`
- Frontend job details UI: `frontend/src/App.tsx`
- Backend tests: `backend/tests/test_jobs_api.py`

## Verification

Completed:

- `npm.cmd run lint`
- `npm.cmd run build`

Not completed locally:

- Backend pytest execution. `py -m pytest` reports that no Python installation is available, and `python` is not on PATH in this environment.

## Current Limitations

- Resume parsing is represented through normalized resume insights from current sourced data. Full PyMuPDF resume ingestion remains a later enhancement.
- GitHub and portfolio insights are derived from mocked source/profile data until real connectors are implemented.
- Candidate detail navigation is still compact inside Job Details. A full Candidate Details page can be expanded during the dashboard module.
- Normalization is deterministic and rule-based; richer AI-assisted candidate profile synthesis can be added behind the same service boundary.

## Next Module

Module 5: Signal Engine.

Planned next work:

- Add signal definitions and default weights.
- Implement approximately 20 representative scoring signals.
- Store signal results per candidate and job.
- Prepare weighted contributions for Module 6 scoring.
