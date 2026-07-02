from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from api.integrations.talent_sources import CandidateSourceResult
from api.models.candidate import Candidate, CandidateProfile, CandidateSource, JobCandidate


class CandidateRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[Candidate]:
        statement = (
            select(Candidate)
            .options(selectinload(Candidate.sources), selectinload(Candidate.profile))
            .order_by(Candidate.created_at.desc(), Candidate.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get(self, candidate_id: int) -> Candidate | None:
        statement = (
            select(Candidate)
            .options(selectinload(Candidate.sources), selectinload(Candidate.profile))
            .where(Candidate.id == candidate_id)
        )
        return self.db.scalars(statement).one_or_none()

    def list_for_job(self, job_id: int) -> list[Candidate]:
        statement = (
            select(Candidate)
            .join(JobCandidate)
            .options(selectinload(Candidate.sources), selectinload(Candidate.profile))
            .where(JobCandidate.job_id == job_id)
            .order_by(JobCandidate.created_at.desc(), Candidate.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_profile_by_candidate_id(self, candidate_id: int) -> CandidateProfile | None:
        statement = select(CandidateProfile).where(CandidateProfile.candidate_id == candidate_id)
        return self.db.scalars(statement).one_or_none()

    def upsert_normalized_profile(
        self,
        candidate_id: int,
        values: dict[str, Any],
    ) -> Candidate:
        profile = self.get_profile_by_candidate_id(candidate_id)
        if profile is None:
            profile = CandidateProfile(candidate_id=candidate_id)
            self.db.add(profile)
            self.db.flush()

        for key, value in values.items():
            setattr(profile, key, value)
        profile.normalized_at = datetime.now(timezone.utc)

        self.db.commit()
        candidate = self.get(candidate_id)
        if candidate is None:
            raise ValueError("Candidate disappeared during profile normalization")
        return candidate

    def upsert_from_source_result(self, job_id: int, result: CandidateSourceResult) -> Candidate:
        candidate = self._get_by_email(result.email)
        if candidate is None:
            candidate = Candidate(
                full_name=result.full_name,
                email=result.email,
                phone=result.phone,
                location=result.location,
                summary=result.summary,
                experience=result.experience,
                current_company=result.current_company,
            )
            self.db.add(candidate)
            self.db.flush()
        else:
            candidate.full_name = result.full_name
            candidate.phone = result.phone
            candidate.location = result.location
            candidate.summary = result.summary
            candidate.experience = result.experience
            candidate.current_company = result.current_company

        self._upsert_source(candidate.id, result)
        self._upsert_profile(candidate.id, result)
        self._upsert_job_match(job_id, candidate.id, result)
        self.db.commit()
        self.db.refresh(candidate)
        return self.get(candidate.id) or candidate

    def _get_by_email(self, email: str) -> Candidate | None:
        statement = select(Candidate).where(Candidate.email == email)
        return self.db.scalars(statement).one_or_none()

    def _upsert_source(self, candidate_id: int, result: CandidateSourceResult) -> None:
        statement = select(CandidateSource).where(
            CandidateSource.source == result.source,
            CandidateSource.external_id == result.external_id,
        )
        source = self.db.scalars(statement).one_or_none()
        if source is None:
            source = CandidateSource(
                candidate_id=candidate_id,
                source=result.source,
                external_id=result.external_id,
                profile_url=result.profile_url,
            )
            self.db.add(source)
            return

        source.candidate_id = candidate_id
        source.profile_url = result.profile_url

    def _upsert_profile(self, candidate_id: int, result: CandidateSourceResult) -> None:
        statement = select(CandidateProfile).where(CandidateProfile.candidate_id == candidate_id)
        profile = self.db.scalars(statement).one_or_none()
        values = {
            "skills": result.skills,
            "projects": result.projects,
            "education": result.education,
            "certifications": result.certifications,
            "github_username": result.github_username,
            "portfolio_url": result.portfolio_url,
            "resume_path": result.resume_path,
        }
        if profile is None:
            self.db.add(CandidateProfile(candidate_id=candidate_id, **values))
            return

        for key, value in values.items():
            setattr(profile, key, value)

    def _upsert_job_match(self, job_id: int, candidate_id: int, result: CandidateSourceResult) -> None:
        statement = select(JobCandidate).where(
            JobCandidate.job_id == job_id,
            JobCandidate.candidate_id == candidate_id,
        )
        match = self.db.scalars(statement).one_or_none()
        if match is None:
            self.db.add(
                JobCandidate(
                    job_id=job_id,
                    candidate_id=candidate_id,
                    source=result.source,
                    match_reasons=result.match_reasons,
                )
            )
            return

        match.source = result.source
        match.match_reasons = result.match_reasons
