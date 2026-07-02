from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.job_intelligence import JobIntelligenceRead
from api.services.jd_intelligence_service import JDIntelligenceService

router = APIRouter(prefix="/jobs", tags=["JD Intelligence"])


def get_jd_intelligence_service(db: Session = Depends(get_db)) -> JDIntelligenceService:
    return JDIntelligenceService(db)


@router.post("/{job_id}/analyze", response_model=JobIntelligenceRead)
def analyze_job(
    job_id: int,
    service: JDIntelligenceService = Depends(get_jd_intelligence_service),
) -> JobIntelligenceRead:
    return service.analyze_job(job_id)
