from sqlalchemy.orm import Session

from api.models.job_intelligence import JobIntelligence
from api.schemas.job_intelligence import JobIntelligenceCreate


class JobIntelligenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_job_id(self, job_id: int) -> JobIntelligence | None:
        return (
            self.db.query(JobIntelligence)
            .filter(JobIntelligence.job_id == job_id)
            .one_or_none()
        )

    def upsert(self, payload: JobIntelligenceCreate) -> JobIntelligence:
        intelligence = self.get_by_job_id(payload.job_id)
        values = payload.model_dump()
        if intelligence is None:
            intelligence = JobIntelligence(**values)
            self.db.add(intelligence)
        else:
            for key, value in values.items():
                setattr(intelligence, key, value)

        self.db.commit()
        self.db.refresh(intelligence)
        return intelligence
