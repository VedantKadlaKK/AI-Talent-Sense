from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.integrations.grok_client import GrokClient
from api.models.job_intelligence import JobIntelligence
from api.repositories.job_intelligence_repository import JobIntelligenceRepository
from api.repositories.job_repository import JobRepository
from api.schemas.job_intelligence import JobIntelligenceCreate


class JDIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.jobs = JobRepository(db)
        self.repository = JobIntelligenceRepository(db)
        self.grok_client = GrokClient()

    def analyze_job(self, job_id: int) -> JobIntelligence:
        job = self.jobs.get(job_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        analysis = self.grok_client.analyze_job_description(job.title, job.description)
        payload = JobIntelligenceCreate(
            job_id=job.id,
            skills=analysis.get("skills", []),
            experience=analysis.get("experience", ""),
            education=analysis.get("education", ""),
            industry=analysis.get("industry", ""),
            location=analysis.get("location", ""),
            seniority=analysis.get("seniority", ""),
            certifications=analysis.get("certifications", []),
            nice_to_have_skills=analysis.get("nice_to_have_skills", []),
            raw_ai_output=analysis.get("raw_ai_output", analysis),
        )
        job.status = "analyzed"
        intelligence = self.repository.upsert(payload)
        return intelligence
