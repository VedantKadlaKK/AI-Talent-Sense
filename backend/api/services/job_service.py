from sqlalchemy.orm import Session

from api.models.job import Job
from api.repositories.job_repository import JobRepository
from api.schemas.job import JobCreate


class JobService:
    def __init__(self, db: Session) -> None:
        self.repository = JobRepository(db)

    def create_job(self, payload: JobCreate) -> Job:
        return self.repository.create(payload)

    def list_jobs(self) -> list[Job]:
        return self.repository.list()

    def get_job(self, job_id: int) -> Job | None:
        return self.repository.get(job_id)

    def delete_job(self, job_id: int) -> bool:
        job = self.repository.get(job_id)
        if job is None:
            return False
        self.repository.delete(job)
        return True
