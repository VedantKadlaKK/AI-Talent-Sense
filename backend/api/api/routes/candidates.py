from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.candidate import CandidateIntelligenceBatchResponse, CandidateRead, CandidateSearchResponse
from api.services.candidate_intelligence_service import CandidateIntelligenceService
from api.services.talent_search_service import TalentSearchService

router = APIRouter(tags=["Candidates"])


def get_talent_search_service(db: Session = Depends(get_db)) -> TalentSearchService:
    return TalentSearchService(db)


def get_candidate_intelligence_service(db: Session = Depends(get_db)) -> CandidateIntelligenceService:
    return CandidateIntelligenceService(db)


@router.post("/jobs/{job_id}/search", response_model=CandidateSearchResponse)
def search_candidates_for_job(
    job_id: int,
    limit_per_source: int = Query(default=8, ge=1, le=25),
    service: TalentSearchService = Depends(get_talent_search_service),
) -> CandidateSearchResponse:
    source_count, candidates = service.search_for_job(job_id, limit_per_source)
    return CandidateSearchResponse(
        job_id=job_id,
        source_count=source_count,
        candidate_count=len(candidates),
        candidates=candidates,
    )


@router.post("/jobs/{job_id}/normalize-candidates", response_model=CandidateIntelligenceBatchResponse)
def normalize_candidates_for_job(
    job_id: int,
    service: CandidateIntelligenceService = Depends(get_candidate_intelligence_service),
) -> CandidateIntelligenceBatchResponse:
    candidates = service.normalize_candidates_for_job(job_id)
    return CandidateIntelligenceBatchResponse(
        job_id=job_id,
        normalized_count=len(candidates),
        candidates=candidates,
    )


@router.get("/candidates", response_model=list[CandidateRead])
def list_candidates(service: TalentSearchService = Depends(get_talent_search_service)) -> list[CandidateRead]:
    return service.list_candidates()


@router.get("/candidates/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: int,
    service: TalentSearchService = Depends(get_talent_search_service),
) -> CandidateRead:
    candidate = service.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    return candidate


@router.post("/candidates/{candidate_id}/normalize", response_model=CandidateRead)
def normalize_candidate(
    candidate_id: int,
    service: CandidateIntelligenceService = Depends(get_candidate_intelligence_service),
) -> CandidateRead:
    return service.normalize_candidate(candidate_id)
