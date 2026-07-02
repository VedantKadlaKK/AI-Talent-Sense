from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.models.signal import SignalResult
from api.schemas.signal import CandidateSignalEvaluation, SignalEvaluationResponse, SignalRead, SignalResultRead
from api.services.signal_engine_service import SignalEngineService

router = APIRouter(tags=["Signals"])


def get_signal_engine_service(db: Session = Depends(get_db)) -> SignalEngineService:
    return SignalEngineService(db)


@router.get("/signals", response_model=list[SignalRead])
def list_signals(service: SignalEngineService = Depends(get_signal_engine_service)) -> list[SignalRead]:
    return service.list_signals()


@router.post("/jobs/{job_id}/evaluate-signals", response_model=SignalEvaluationResponse)
def evaluate_signals_for_job(
    job_id: int,
    service: SignalEngineService = Depends(get_signal_engine_service),
) -> SignalEvaluationResponse:
    grouped = service.evaluate_job(job_id)
    return _build_response(job_id, grouped)


@router.get("/jobs/{job_id}/signal-results", response_model=SignalEvaluationResponse)
def get_signal_results_for_job(
    job_id: int,
    service: SignalEngineService = Depends(get_signal_engine_service),
) -> SignalEvaluationResponse:
    grouped: dict[int, list[SignalResult]] = defaultdict(list)
    for result in service.list_results_for_job(job_id):
        grouped[result.candidate_id].append(result)
    return _build_response(job_id, dict(grouped))


def _build_response(job_id: int, grouped: dict[int, list[SignalResult]]) -> SignalEvaluationResponse:
    candidate_results = [
        CandidateSignalEvaluation(
            candidate_id=candidate_id,
            result_count=len(results),
            results=[_serialize_result(result) for result in results],
        )
        for candidate_id, results in grouped.items()
    ]
    signal_count = max((item.result_count for item in candidate_results), default=0)
    return SignalEvaluationResponse(
        job_id=job_id,
        candidate_count=len(candidate_results),
        signal_count=signal_count,
        results=candidate_results,
    )


def _serialize_result(result: SignalResult) -> SignalResultRead:
    return SignalResultRead(
        id=result.id,
        candidate_id=result.candidate_id,
        job_id=result.job_id,
        signal_id=result.signal_id,
        signal_name=result.signal.name,
        category=result.signal.category,
        score=result.score,
        weight=result.weight,
        contribution=result.contribution,
        reason=result.reason,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
