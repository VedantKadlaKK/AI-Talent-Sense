from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.models.candidate import Candidate, CandidateProfile
from api.repositories.candidate_repository import CandidateRepository
from api.repositories.job_repository import JobRepository


class CandidateIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.candidates = CandidateRepository(db)
        self.jobs = JobRepository(db)

    def normalize_candidate(self, candidate_id: int) -> Candidate:
        candidate = self.candidates.get(candidate_id)
        if candidate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found",
            )

        values = self._build_normalized_values(candidate)
        return self.candidates.upsert_normalized_profile(candidate.id, values)

    def normalize_candidates_for_job(self, job_id: int) -> list[Candidate]:
        job = self.jobs.get(job_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
        )

        candidates = self.candidates.list_for_job(job_id)
        return [
            self.candidates.upsert_normalized_profile(candidate.id, self._build_normalized_values(candidate))
            for candidate in candidates
        ]

    def _build_normalized_values(self, candidate: Candidate) -> dict[str, Any]:
        profile = candidate.profile
        source_names = sorted({source.source for source in candidate.sources})
        skills = self._dedupe(profile.skills if profile else [])
        projects = profile.projects if profile else []
        education = self._dedupe(profile.education if profile else [])
        certifications = self._dedupe(profile.certifications if profile else [])
        github_username = profile.github_username if profile else ""
        portfolio_url = profile.portfolio_url if profile else ""
        resume_path = profile.resume_path if profile else ""

        return {
            "skills": skills,
            "projects": projects,
            "education": education,
            "certifications": certifications,
            "github_username": github_username,
            "portfolio_url": portfolio_url,
            "resume_path": resume_path,
            "normalized_summary": self._normalized_summary(candidate, profile),
            "source_coverage": self._source_coverage(candidate, profile),
            "resume_insights": self._resume_insights(candidate, profile),
            "github_insights": self._github_insights(candidate, profile),
            "portfolio_insights": self._portfolio_insights(profile),
            "api_insights": self._api_insights(candidate, source_names),
        }

    def _normalized_summary(self, candidate: Candidate, profile: CandidateProfile | None) -> str:
        skills = ", ".join((profile.skills if profile else [])[:5])
        parts = [
            candidate.summary.strip(),
            f"Experience: {candidate.experience}." if candidate.experience else "",
            f"Current company: {candidate.current_company}." if candidate.current_company else "",
            f"Key skills: {skills}." if skills else "",
        ]
        return " ".join(part for part in parts if part).strip()

    def _source_coverage(self, candidate: Candidate, profile: CandidateProfile | None) -> dict[str, Any]:
        source_names = sorted({source.source for source in candidate.sources})
        has_github = bool(profile and profile.github_username) or any("github" in source for source in source_names)
        has_portfolio = bool(profile and profile.portfolio_url)
        has_resume = bool(profile and profile.resume_path) or bool(candidate.summary and candidate.experience)
        has_api_data = bool(source_names)
        available = [has_resume, has_github, has_portfolio, has_api_data]
        return {
            "sources": source_names,
            "resume": has_resume,
            "github": has_github,
            "portfolio": has_portfolio,
            "api_data": has_api_data,
            "completeness": round(sum(1 for item in available if item) / len(available), 2),
        }

    def _resume_insights(self, candidate: Candidate, profile: CandidateProfile | None) -> dict[str, Any]:
        return {
            "summary_available": bool(candidate.summary),
            "experience": candidate.experience,
            "education": profile.education if profile else [],
            "certifications": profile.certifications if profile else [],
            "resume_path": profile.resume_path if profile else "",
        }

    def _github_insights(self, candidate: Candidate, profile: CandidateProfile | None) -> dict[str, Any]:
        github_sources = [source for source in candidate.sources if "github" in source.source]
        return {
            "username": profile.github_username if profile else "",
            "profile_urls": [source.profile_url for source in github_sources if source.profile_url],
            "project_count": len(profile.projects if profile else []),
            "skills": profile.skills if profile else [],
        }

    def _portfolio_insights(self, profile: CandidateProfile | None) -> dict[str, Any]:
        return {
            "portfolio_url": profile.portfolio_url if profile else "",
            "project_count": len(profile.projects if profile else []),
            "projects": profile.projects if profile else [],
        }

    def _api_insights(self, candidate: Candidate, source_names: list[str]) -> dict[str, Any]:
        return {
            "source_count": len(source_names),
            "sources": source_names,
            "external_ids": [
                {
                    "source": source.source,
                    "external_id": source.external_id,
                }
                for source in candidate.sources
            ],
        }

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = value.strip()
            key = normalized.lower()
            if normalized and key not in seen:
                seen.add(key)
                result.append(normalized)
        return result
