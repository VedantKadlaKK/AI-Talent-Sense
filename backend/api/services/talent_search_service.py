from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.integrations.talent_sources import TalentSource, get_default_talent_sources
from api.models.candidate import Candidate
from api.repositories.candidate_repository import CandidateRepository
from api.repositories.job_repository import JobRepository


class TalentSearchService:
    def __init__(self, db: Session, sources: list[TalentSource] | None = None) -> None:
        self.db = db
        self.jobs = JobRepository(db)
        self.candidates = CandidateRepository(db)
        self.sources = sources or get_default_talent_sources()

    def search_for_job(self, job_id: int, limit_per_source: int = 8) -> tuple[int, list[Candidate]]:
        job = self.jobs.get(job_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        source_results = [
            result
            for source in self.sources
            for result in source.search_candidates(job, job.intelligence, limit_per_source)
        ]

        for result in source_results:
            self.candidates.upsert_from_source_result(job.id, result)

        job.status = "searching"
        self.db.commit()

        return len(self.sources), self.candidates.list_for_job(job.id)

    def list_candidates(self) -> list[Candidate]:
        return self.candidates.get_all()

    def get_candidate(self, candidate_id: int) -> Candidate | None:
        return self.candidates.get(candidate_id)
