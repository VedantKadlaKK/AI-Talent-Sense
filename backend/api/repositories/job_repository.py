from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.job import Job
from api.schemas.job import JobCreate


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: JobCreate) -> Job:
        job = Job(**payload.model_dump())
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def list(self) -> list[Job]:
        statement = select(Job).order_by(Job.created_at.desc(), Job.id.desc())
        return list(self.db.scalars(statement).all())

    def get(self, job_id: int) -> Job | None:
        return self.db.get(Job, job_id)

    def delete(self, job: Job) -> None:
        self.db.delete(job)
        self.db.commit()
