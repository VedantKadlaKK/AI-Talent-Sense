from collections import defaultdict
import re
import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.integrations.grok_client import GrokClient
from api.models.candidate import Candidate
from api.models.job import Job
from api.models.recommendation import Recommendation
from api.models.signal import SignalResult
from api.repositories.candidate_repository import CandidateRepository
from api.repositories.job_repository import JobRepository
from api.repositories.recommendation_repository import RecommendationRepository
from api.repositories.signal_repository import SignalRepository
from api.services.signal_engine_service import SignalEngineService


class RecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.jobs = JobRepository(db)
        self.candidates = CandidateRepository(db)
        self.signals = SignalRepository(db)
        self.recommendations = RecommendationRepository(db)
        self.signal_engine = SignalEngineService(db)
        self.grok_client = GrokClient()

    def rank_job(self, job_id: int) -> list[Recommendation]:
        job = self.jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        signal_results = self.signals.list_results_for_job(job_id)
        if not signal_results:
            self.signal_engine.evaluate_job(job_id)
            signal_results = self.signals.list_results_for_job(job_id)

        grouped = self._group_by_candidate(signal_results)
        scored = [
            (candidate_id, self._overall_score(results), results)
            for candidate_id, results in grouped.items()
        ]
        scored.sort(key=lambda item: item[1], reverse=True)

        stored: list[Recommendation] = []
        for index, (candidate_id, overall_score, results) in enumerate(scored, start=1):
            candidate = self.candidates.get(candidate_id)
            if candidate is None:
                continue
            explanation = self._explain_with_retry(job, candidate, results, overall_score)
            stored.append(
                self.recommendations.upsert(
                    candidate_id=candidate_id,
                    job_id=job_id,
                    overall_score=overall_score,
                    rank=index,
                    summary=str(explanation.get("summary", "")),
                    strengths=list(explanation.get("strengths", [])),
                    weaknesses=list(explanation.get("weaknesses", [])),
                    missing_skills=list(explanation.get("missing_skills", [])),
                    recommendation=str(explanation.get("recommendation", "Review")),
                    raw_ai_output=explanation,
                )
            )

        job.status = "ranked"
        self.db.commit()
        return self.recommendations.list_for_job(job_id)

    def list_for_job(self, job_id: int) -> list[Recommendation]:
        job = self.jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return self.recommendations.list_for_job(job_id)

    def signal_results_for_job(self, job_id: int) -> dict[int, list[SignalResult]]:
        return self._group_by_candidate(self.signals.list_results_for_job(job_id))

    def _overall_score(self, results: list[SignalResult]) -> float:
        total_weight = sum(result.weight for result in results)
        if total_weight <= 0:
            return 0
        weighted_score = sum(result.contribution for result in results) / total_weight
        return round(max(0, min(100, weighted_score)), 2)

    def _explain_with_retry(
        self,
        job: Job,
        candidate: Candidate,
        results: list[SignalResult],
        overall_score: float,
        max_retries: int = 2,
    ) -> dict[str, object]:
        for attempt in range(max_retries + 1):
            try:
                return self._explain(job, candidate, results, overall_score)
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

    def _explain(
        self,
        job: Job,
        candidate: Candidate,
        results: list[SignalResult],
        overall_score: float,
    ) -> dict[str, object]:
        job_payload = {
            "title": job.title,
            "company_name": job.company_name,
            "skills": job.intelligence.skills if job.intelligence else [],
            "experience": job.intelligence.experience if job.intelligence else "",
            "education": job.intelligence.education if job.intelligence else "",
            "location": job.intelligence.location if job.intelligence else "",
            "seniority": job.intelligence.seniority if job.intelligence else "",
        }
        candidate_payload = {
            "full_name": candidate.full_name,
            "summary": candidate.summary,
            "experience": candidate.experience,
            "location": candidate.location,
            "current_company": candidate.current_company,
            "skills": candidate.profile.skills if candidate.profile else [],
            "normalized_summary": candidate.profile.normalized_summary if candidate.profile else "",
        }
        signal_payload = [
            {
                "signal_name": result.signal.name,
                "category": result.signal.category,
                "score": result.score,
                "weight": result.weight,
                "contribution": result.contribution,
                "reason": result.reason,
            }
            for result in results
        ]
        return self.grok_client.explain_candidate_recommendation(
            job_payload,
            candidate_payload,
            signal_payload,
            overall_score,
        )

    def _group_by_candidate(self, results: list[SignalResult]) -> dict[int, list[SignalResult]]:
        grouped: dict[int, list[SignalResult]] = defaultdict(list)
        for result in results:
            grouped[result.candidate_id].append(result)
        return dict(grouped)
