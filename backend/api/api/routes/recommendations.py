from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.api.routes.signals import _serialize_result
from api.db.session import get_db
from api.repositories.candidate_repository import CandidateRepository
from api.schemas.recommendation import RecommendationCandidateRead, RecommendationResponse
from api.services.recommendation_service import RecommendationService

router = APIRouter(tags=["Recommendations"])


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    return RecommendationService(db)


def get_candidate_repository(db: Session = Depends(get_db)) -> CandidateRepository:
    return CandidateRepository(db)


@router.post("/jobs/{job_id}/rank", response_model=RecommendationResponse)
def rank_candidates_for_job(
    job_id: int,
    service: RecommendationService = Depends(get_recommendation_service),
    candidates: CandidateRepository = Depends(get_candidate_repository),
) -> RecommendationResponse:
    recommendations = service.rank_job(job_id)
    signals_by_candidate = service.signal_results_for_job(job_id)
    return _build_response(job_id, recommendations, signals_by_candidate, candidates)


@router.get("/recommendations/{job_id}", response_model=RecommendationResponse)
def get_recommendations_for_job(
    job_id: int,
    service: RecommendationService = Depends(get_recommendation_service),
    candidates: CandidateRepository = Depends(get_candidate_repository),
) -> RecommendationResponse:
    recommendations = service.list_for_job(job_id)
    signals_by_candidate = service.signal_results_for_job(job_id)
    return _build_response(job_id, recommendations, signals_by_candidate, candidates)


def _build_response(
    job_id: int,
    recommendations,
    signals_by_candidate,
    candidates: CandidateRepository,
) -> RecommendationResponse:
    items: list[RecommendationCandidateRead] = []
    for recommendation in recommendations:
        candidate = candidates.get(recommendation.candidate_id)
        if candidate is None:
            continue
        items.append(
            RecommendationCandidateRead(
                recommendation=recommendation,
                candidate=candidate,
                signals=[
                    _serialize_result(result)
                    for result in signals_by_candidate.get(recommendation.candidate_id, [])
                ],
            )
        )
    return RecommendationResponse(
        job_id=job_id,
        recommendation_count=len(items),
        recommendations=items,
    )
