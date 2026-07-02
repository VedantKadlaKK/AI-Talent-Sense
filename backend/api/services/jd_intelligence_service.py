import re
import time

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

        analysis = self._analyze_with_retry(job.title, job.description)

        payload = JobIntelligenceCreate(
            job_id=job.id,
            skills=self._to_list_of_strings(analysis.get("skills", [])),
            experience=self._to_string(analysis.get("experience", "")),
            education=self._to_string(analysis.get("education", "")),
            industry=self._to_string(analysis.get("industry", "")),
            location=self._to_string(analysis.get("location", "")),
            seniority=self._to_string(analysis.get("seniority", "")),
            certifications=self._to_list_of_strings(analysis.get("certifications", [])),
            nice_to_have_skills=self._to_list_of_strings(analysis.get("nice_to_have_skills", [])),
            raw_ai_output=analysis.get("raw_ai_output", analysis),
        )
        job.status = "analyzed"
        intelligence = self.repository.upsert(payload)
        return intelligence

    def _analyze_with_retry(self, title: str, description: str, max_retries: int = 2) -> dict:
        for attempt in range(max_retries + 1):
            try:
                return self.grok_client.analyze_job_description(title, description)
            except ValueError as error:
                error_msg = str(error)
                if "rate limit" in error_msg.lower() and attempt < max_retries:
                    match = re.search(r"Retry after ([0-9.]+)s", error_msg)
                    wait_time = float(match.group(1)) if match else 5.0
                    time.sleep(wait_time)
                    continue
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=error_msg,
                ) from error

    def _to_string(self, value: object) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "; ".join(str(item) for item in value if item is not None)
        if value is None:
            return ""
        return str(value)

    def _to_list_of_strings(self, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        if isinstance(value, str):
            normalized = value.strip()
            if normalized.lower() in {"not specified", "none", "n/a", "na", ""}:
                return []
            # split on common delimiters when string contains multiple items
            if "," in normalized or ";" in normalized or "\n" in normalized:
                parts = re.split(r"[,;\n]+", normalized)
                return [part.strip() for part in parts if part.strip()]
            return [normalized]
        return [str(value)]
