from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.db.base import Base
from api.db.session import get_db
from api.main import app
from api.models import (  # noqa: F401
    Candidate,
    CandidateProfile,
    CandidateSource,
    Job,
    JobCandidate,
    JobIntelligence,
    Recommendation,
    Signal,
    SignalResult,
)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module() -> None:
    app.dependency_overrides.clear()


def test_create_and_list_jobs() -> None:
    payload = {
        "title": "Senior Machine Learning Engineer",
        "company_name": "MyLynk",
        "description": "Build ranking systems and candidate intelligence workflows for recruiters.",
        "status": "draft",
    }

    created_response = client.post("/jobs", json=payload)

    assert created_response.status_code == 201
    created = created_response.json()
    assert created["id"] == 1
    assert created["title"] == payload["title"]

    list_response = client.get("/jobs")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_get_and_delete_job() -> None:
    payload = {
        "title": "Frontend Platform Engineer",
        "company_name": "MyLynk",
        "description": "Own recruiter-facing workflows using React and TypeScript.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()

    get_response = client.get(f"/jobs/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["company_name"] == "MyLynk"

    delete_response = client.delete(f"/jobs/{created['id']}")

    assert delete_response.status_code == 204
    assert client.get(f"/jobs/{created['id']}").status_code == 404


def test_analyze_job_extracts_and_stores_job_intelligence() -> None:
    payload = {
        "title": "Senior Python FastAPI Engineer",
        "company_name": "MyLynk",
        "description": (
            "We need 5+ years building recruiter workflows with Python, FastAPI, "
            "React, TypeScript, and PostgreSQL.\n"
            "Bachelor's degree required.\n"
            "Location: Bengaluru\n"
            "Preferred AWS Certified engineers with leadership experience."
        ),
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()

    analyze_response = client.post(f"/jobs/{created['id']}/analyze")

    assert analyze_response.status_code == 200
    intelligence = analyze_response.json()
    assert intelligence["job_id"] == created["id"]
    assert "Python" in intelligence["skills"]
    assert "FastAPI" in intelligence["skills"]
    assert intelligence["experience"] == "5+ years"
    assert intelligence["education"] == "Bachelor's degree"
    assert intelligence["location"] == "Bengaluru"
    assert intelligence["raw_ai_output"]["provider"] == "heuristic"

    job_response = client.get(f"/jobs/{created['id']}")

    assert job_response.status_code == 200
    job = job_response.json()
    assert job["status"] == "analyzed"
    assert job["intelligence"]["id"] == intelligence["id"]


def test_analyze_job_upserts_existing_intelligence_record() -> None:
    payload = {
        "title": "React TypeScript Engineer",
        "company_name": "MyLynk",
        "description": "Build recruiter dashboards with React and TypeScript for 3+ years.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()

    first_analysis = client.post(f"/jobs/{created['id']}/analyze").json()
    second_analysis = client.post(f"/jobs/{created['id']}/analyze").json()

    assert second_analysis["id"] == first_analysis["id"]
    assert second_analysis["job_id"] == created["id"]


def test_analyze_missing_job_returns_404() -> None:
    response = client.post("/jobs/999/analyze")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_search_candidates_for_job_persists_candidates_and_marks_job_searching() -> None:
    payload = {
        "title": "Senior Python FastAPI Engineer",
        "company_name": "MyLynk",
        "description": "Build AI recruiting systems with Python, FastAPI, PostgreSQL, and AWS.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    client.post(f"/jobs/{created['id']}/analyze")

    search_response = client.post(f"/jobs/{created['id']}/search")

    assert search_response.status_code == 200
    search_result = search_response.json()
    assert search_result["job_id"] == created["id"]
    assert search_result["source_count"] == 3
    assert search_result["candidate_count"] >= 3
    assert search_result["candidates"][0]["profile"]["skills"]
    assert search_result["candidates"][0]["sources"]

    job_response = client.get(f"/jobs/{created['id']}")

    assert job_response.status_code == 200
    assert job_response.json()["status"] == "searching"


def test_repeated_candidate_search_does_not_duplicate_candidates() -> None:
    payload = {
        "title": "React TypeScript Engineer",
        "company_name": "MyLynk",
        "description": "Build recruiter workflows with React, TypeScript, and PostgreSQL.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()

    first_search = client.post(f"/jobs/{created['id']}/search").json()
    second_search = client.post(f"/jobs/{created['id']}/search").json()
    candidates_response = client.get("/candidates")

    assert second_search["candidate_count"] == first_search["candidate_count"]
    assert candidates_response.status_code == 200
    assert len(candidates_response.json()) == first_search["candidate_count"]


def test_search_missing_job_returns_404() -> None:
    response = client.post("/jobs/999/search")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_normalize_candidates_for_job_updates_canonical_profiles() -> None:
    payload = {
        "title": "Senior Python FastAPI Engineer",
        "company_name": "MyLynk",
        "description": "Build AI recruiting systems with Python, FastAPI, PostgreSQL, and AWS.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    client.post(f"/jobs/{created['id']}/search")

    normalize_response = client.post(f"/jobs/{created['id']}/normalize-candidates")

    assert normalize_response.status_code == 200
    result = normalize_response.json()
    assert result["job_id"] == created["id"]
    assert result["normalized_count"] >= 3
    first_profile = result["candidates"][0]["profile"]
    assert first_profile["normalized_summary"]
    assert first_profile["source_coverage"]["api_data"] is True
    assert "completeness" in first_profile["source_coverage"]
    assert first_profile["resume_insights"]["summary_available"] is True


def test_normalize_single_candidate_updates_profile() -> None:
    payload = {
        "title": "React TypeScript Engineer",
        "company_name": "MyLynk",
        "description": "Build recruiter workflows with React, TypeScript, and PostgreSQL.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    searched = client.post(f"/jobs/{created['id']}/search").json()
    candidate_id = searched["candidates"][0]["id"]

    normalize_response = client.post(f"/candidates/{candidate_id}/normalize")

    assert normalize_response.status_code == 200
    candidate = normalize_response.json()
    assert candidate["id"] == candidate_id
    assert candidate["profile"]["normalized_at"] is not None
    assert candidate["profile"]["api_insights"]["source_count"] >= 1


def test_normalize_missing_entities_return_404() -> None:
    missing_job_response = client.post("/jobs/999/normalize-candidates")
    missing_candidate_response = client.post("/candidates/999/normalize")

    assert missing_job_response.status_code == 404
    assert missing_job_response.json()["detail"] == "Job not found"
    assert missing_candidate_response.status_code == 404
    assert missing_candidate_response.json()["detail"] == "Candidate not found"


def test_signal_engine_lists_default_signals() -> None:
    response = client.get("/signals")

    assert response.status_code == 200
    signals = response.json()
    assert len(signals) == 20
    assert {signal["name"] for signal in signals} >= {"Skill Match", "Experience Match", "Availability"}


def test_evaluate_signals_for_job_stores_twenty_results_per_candidate() -> None:
    payload = {
        "title": "Senior Python FastAPI Engineer",
        "company_name": "MyLynk",
        "description": "Build AI recruiting systems with Python, FastAPI, PostgreSQL, and AWS.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    client.post(f"/jobs/{created['id']}/analyze")
    search_result = client.post(f"/jobs/{created['id']}/search").json()
    client.post(f"/jobs/{created['id']}/normalize-candidates")

    evaluate_response = client.post(f"/jobs/{created['id']}/evaluate-signals")

    assert evaluate_response.status_code == 200
    result = evaluate_response.json()
    assert result["job_id"] == created["id"]
    assert result["candidate_count"] == search_result["candidate_count"]
    assert result["signal_count"] == 20
    assert result["results"][0]["result_count"] == 20
    first_signal = result["results"][0]["results"][0]
    assert first_signal["score"] >= 0
    assert first_signal["weight"] > 0
    assert abs(first_signal["contribution"] - (first_signal["score"] * first_signal["weight"])) < 0.001
    assert first_signal["reason"]


def test_repeated_signal_evaluation_upserts_results() -> None:
    payload = {
        "title": "React TypeScript Engineer",
        "company_name": "MyLynk",
        "description": "Build recruiter workflows with React, TypeScript, and PostgreSQL.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    client.post(f"/jobs/{created['id']}/search")

    first = client.post(f"/jobs/{created['id']}/evaluate-signals").json()
    second = client.post(f"/jobs/{created['id']}/evaluate-signals").json()
    stored = client.get(f"/jobs/{created['id']}/signal-results").json()

    assert second["candidate_count"] == first["candidate_count"]
    assert stored["candidate_count"] == first["candidate_count"]
    assert stored["signal_count"] == 20


def test_evaluate_signals_missing_job_returns_404() -> None:
    response = client.post("/jobs/999/evaluate-signals")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_rank_candidates_creates_recommendations_with_explanations() -> None:
    payload = {
        "title": "Senior Python FastAPI Engineer",
        "company_name": "MyLynk",
        "description": "Build AI recruiting systems with Python, FastAPI, PostgreSQL, and AWS.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    client.post(f"/jobs/{created['id']}/analyze")
    search_result = client.post(f"/jobs/{created['id']}/search").json()
    client.post(f"/jobs/{created['id']}/normalize-candidates")
    client.post(f"/jobs/{created['id']}/evaluate-signals")

    rank_response = client.post(f"/jobs/{created['id']}/rank")

    assert rank_response.status_code == 200
    result = rank_response.json()
    assert result["job_id"] == created["id"]
    assert result["recommendation_count"] == search_result["candidate_count"]
    first = result["recommendations"][0]
    assert first["recommendation"]["rank"] == 1
    assert first["recommendation"]["overall_score"] >= 0
    assert first["recommendation"]["summary"]
    assert first["recommendation"]["strengths"]
    assert first["signals"]
    assert client.get(f"/jobs/{created['id']}").json()["status"] == "ranked"


def test_rank_candidates_can_run_signal_evaluation_when_missing() -> None:
    payload = {
        "title": "React TypeScript Engineer",
        "company_name": "MyLynk",
        "description": "Build recruiter workflows with React, TypeScript, and PostgreSQL.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    client.post(f"/jobs/{created['id']}/search")

    rank_response = client.post(f"/jobs/{created['id']}/rank")

    assert rank_response.status_code == 200
    assert rank_response.json()["recommendation_count"] > 0
    assert client.get(f"/jobs/{created['id']}/signal-results").json()["signal_count"] == 20


def test_get_recommendations_for_job_returns_ranked_results() -> None:
    payload = {
        "title": "Senior Python FastAPI Engineer",
        "company_name": "MyLynk",
        "description": "Build AI recruiting systems with Python, FastAPI, PostgreSQL, and AWS.",
        "status": "draft",
    }
    created = client.post("/jobs", json=payload).json()
    client.post(f"/jobs/{created['id']}/search")
    client.post(f"/jobs/{created['id']}/rank")

    response = client.get(f"/recommendations/{created['id']}")

    assert response.status_code == 200
    result = response.json()
    assert result["recommendation_count"] > 0
    assert result["recommendations"][0]["recommendation"]["rank"] == 1


def test_rank_missing_job_returns_404() -> None:
    response = client.post("/jobs/999/rank")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
