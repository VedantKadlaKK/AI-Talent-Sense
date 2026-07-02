# AI Talent Sense

AI-powered talent sourcing platform inspired by Juicebox.ai.

This repository is being built incrementally from the engineering blueprint. Completed slices:

- Module 1: Job Management
- Module 2: JD Intelligence
- Module 3: Talent Source Layer
- Module 4: Candidate Intelligence
- Module 5: Signal Engine
- Module 6: Weighted Scoring
- Module 7: Explainable AI
- Module 8: Dashboard

## Current Capabilities

- Create jobs
- List jobs
- View job details
- Delete jobs
- Analyze job descriptions into structured hiring requirements
- Store and display extracted skills, experience, education, industry, location, seniority, certifications, and nice-to-have skills
- Search mocked talent sources through a unified connector interface
- Persist sourced candidates, candidate sources, normalized profile data, and job-specific search matches
- Display sourced candidates from Job Details
- Normalize sourced candidate data into canonical candidate profiles
- Store candidate intelligence insights for resume, GitHub, portfolio, API source coverage, and profile completeness
- Evaluate candidates against 20 configurable representative signals
- Store per-job/per-candidate signal scores, weights, contributions, and reasons
- Display signal breakdowns for sourced candidates
- Aggregate weighted signal contributions into final candidate scores
- Rank candidates and persist recommendations
- Generate explainable summaries, strengths, weaknesses, missing skills, and recommendation labels
- Browse candidate lists and candidate details
- Review ranked candidates with scores, signal context, and AI-style explanations
- Persist jobs through a FastAPI + SQLAlchemy backend
- Use a React + TypeScript + Tailwind frontend for the recruiter workflow

## Project Layout

```text
backend/
  api/
    core/
    db/
    integrations/
    models/
    repositories/
    schemas/
    services/
    utils/
frontend/
  src/
```

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

The backend reads `DATABASE_URL` from the environment. If it is omitted, it uses a local SQLite database for development. PostgreSQL URLs are supported by SQLAlchemy once `DATABASE_URL` is set.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the API at `http://localhost:8000` by default. Override with `VITE_API_BASE_URL`.
