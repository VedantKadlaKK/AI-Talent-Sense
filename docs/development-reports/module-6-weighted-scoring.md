# Module 6 Development Report: Weighted Scoring

Date: 2026-07-02

## Scope Completed

- Added durable recommendation persistence through the `recommendations` table.
- Added Alembic migration `0006_create_recommendations`.
- Implemented weighted score aggregation from stored signal results.
- Computed final candidate score as normalized weighted contribution:
  - `overall_score = sum(score * weight) / sum(weight)`
- Preserved per-signal contribution for explainability and ranking context.
- Added candidate ranking per job.
- Updated job status to `ranked` after successful ranking.
- Added backend APIs:
  - `POST /jobs/{job_id}/rank`
  - `GET /recommendations/{job_id}`
- Added backend tests for ranking, recommendation retrieval, automatic signal evaluation when needed, and missing-job behavior.
- Added frontend `Rank` action in Job Details.
- Added ranked recommendation display with rank, overall score, recommendation label, and top signal context.

## Key Files

- Recommendation model: `backend/api/models/recommendation.py`
- Recommendation schema: `backend/api/schemas/recommendation.py`
- Recommendation repository: `backend/api/repositories/recommendation_repository.py`
- Recommendation service: `backend/api/services/recommendation_service.py`
- Recommendation routes: `backend/api/api/routes/recommendations.py`
- Migration: `backend/alembic/versions/0006_create_recommendations.py`
- Frontend API client: `frontend/src/api.ts`
- Frontend types: `frontend/src/types.ts`
- Frontend UI: `frontend/src/App.tsx`

## Verification

Completed:

- `npm.cmd run lint`
- `npm.cmd run build`

Not completed locally:

- Backend pytest execution. The backend `.venv` exists, but its Python executable points to `C:\Users\Vedant\AppData\Local\Programs\Python\Python312\python.exe`, which is missing.

## Current Limitations

- Weight editing is database-backed but does not yet have an admin UI.
- Final ranking uses the stored signal weights and deterministic signal scores; no manual recruiter overrides are implemented.
