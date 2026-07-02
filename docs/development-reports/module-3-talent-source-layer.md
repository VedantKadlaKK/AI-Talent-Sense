# Module 3 Development Report: Talent Source Layer

Date: 2026-07-02

## Scope Completed

- Added a unified talent source interface with `search_candidates()`.
- Added deterministic mocked talent connectors for:
  - Internal DB
  - GitHub
  - LinkedIn-style profile data
- Implemented job-aware mocked search using job title and extracted JD intelligence.
- Added candidate persistence tables:
  - `candidates`
  - `candidate_sources`
  - `candidate_profiles`
  - `job_candidates`
- Added Alembic migration `0003_create_candidates`.
- Implemented candidate upsert behavior to avoid duplicate people across repeated searches.
- Preserved source-level identity through `source` and `external_id`.
- Added job-specific candidate search matches for later scoring and recommendations.
- Implemented Candidate Search API:
  - `POST /jobs/{id}/search`
- Implemented Candidate retrieval APIs:
  - `GET /candidates`
  - `GET /candidates/{id}`
- Updated job status to `searching` after a successful candidate search.
- Added frontend support to search candidates from Job Details.
- Added frontend candidate result display with summary, company, location, email, source tags, profile link, experience, and skill tags.
- Added backend API tests for candidate search success, repeated-search deduping, candidate listing, and missing-job handling.
- Updated README capabilities to reflect Module 3 completion.

## Key Files

- Talent source interface and mocks: `backend/api/integrations/talent_sources.py`
- Candidate models: `backend/api/models/candidate.py`
- Candidate schemas: `backend/api/schemas/candidate.py`
- Candidate repository: `backend/api/repositories/candidate_repository.py`
- Search service: `backend/api/services/talent_search_service.py`
- Candidate routes: `backend/api/api/routes/candidates.py`
- Migration: `backend/alembic/versions/0003_create_candidates.py`
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

- Talent connectors are mocked and deterministic. Real GitHub, Naukri, LinkedIn, or internal database integrations are intentionally future connector implementations behind the same interface.
- Candidate normalization is represented through the `candidate_profiles` table and source result mapping, but deeper resume/API merging belongs to Module 4.
- Candidate results are shown after search in the current job detail session. A richer persisted candidate list/detail navigation can be expanded in the Dashboard module.
- Search relevance is lightweight and rule-based for now; ranking and explainable scoring are intentionally reserved for later modules.

## Next Module

Module 4: Candidate Intelligence.

Planned next work:

- Normalize multi-source candidate data into one canonical profile.
- Add explicit candidate intelligence service boundaries.
- Prepare profile output for the signal engine.
- Expand candidate detail views around normalized resume, GitHub, portfolio, and API data.
