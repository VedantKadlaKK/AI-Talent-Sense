import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.models.candidate import Candidate
from api.models.job import Job
from api.models.signal import Signal, SignalResult
from api.repositories.candidate_repository import CandidateRepository
from api.repositories.job_repository import JobRepository
from api.repositories.signal_repository import SignalRepository


@dataclass(frozen=True)
class SignalScore:
    score: float
    reason: str


class SignalEngineService:
    DEFAULT_SIGNALS: list[dict[str, object]] = [
        {"name": "Skill Match", "category": "Requirements", "description": "Overlap between required job skills and candidate skills.", "default_weight": 1.5},
        {"name": "Experience Match", "category": "Requirements", "description": "Alignment between required and candidate years of experience.", "default_weight": 1.2},
        {"name": "Education Match", "category": "Requirements", "description": "Evidence of required education or comparable background.", "default_weight": 0.7},
        {"name": "Certification Match", "category": "Requirements", "description": "Overlap between required and candidate certifications.", "default_weight": 0.6},
        {"name": "Project Match", "category": "Evidence", "description": "Projects relevant to the job description and required skills.", "default_weight": 1.0},
        {"name": "Domain Match", "category": "Context", "description": "Industry or domain relevance.", "default_weight": 0.8},
        {"name": "Location Match", "category": "Logistics", "description": "Candidate location alignment with job location.", "default_weight": 0.6},
        {"name": "Career Growth", "category": "Trajectory", "description": "Career maturity relative to seniority expectations.", "default_weight": 0.6},
        {"name": "Resume Quality", "category": "Evidence", "description": "Completeness and clarity of resume-derived data.", "default_weight": 0.7},
        {"name": "GitHub Activity", "category": "Evidence", "description": "Availability and depth of GitHub evidence.", "default_weight": 0.7},
        {"name": "Portfolio Quality", "category": "Evidence", "description": "Availability and project depth in portfolio data.", "default_weight": 0.6},
        {"name": "Employment Stability", "category": "Trajectory", "description": "Signals of stable recent employment history.", "default_weight": 0.5},
        {"name": "Keyword Match", "category": "Requirements", "description": "Keyword overlap across job and candidate text.", "default_weight": 0.9},
        {"name": "Technology Freshness", "category": "Requirements", "description": "Modern technology alignment.", "default_weight": 0.8},
        {"name": "Leadership", "category": "Seniority", "description": "Leadership and mentoring evidence.", "default_weight": 0.7},
        {"name": "Communication", "category": "Evidence", "description": "Readable profile summary and communication-oriented evidence.", "default_weight": 0.5},
        {"name": "Open Source Activity", "category": "Evidence", "description": "Open-source or public contribution evidence.", "default_weight": 0.6},
        {"name": "Company Relevance", "category": "Context", "description": "Current or past company/domain relevance.", "default_weight": 0.5},
        {"name": "Role Seniority", "category": "Seniority", "description": "Candidate experience and title alignment with job seniority.", "default_weight": 0.8},
        {"name": "Availability", "category": "Logistics", "description": "Availability inferred from source coverage and remote/location hints.", "default_weight": 0.4},
    ]

    def __init__(self, db: Session) -> None:
        self.jobs = JobRepository(db)
        self.candidates = CandidateRepository(db)
        self.signals = SignalRepository(db)

    def evaluate_job(self, job_id: int) -> dict[int, list[SignalResult]]:
        job = self.jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        candidates = self.candidates.list_for_job(job_id)
        active_signals = self.signals.ensure_defaults(self.DEFAULT_SIGNALS)
        grouped: dict[int, list[SignalResult]] = {}

        for candidate in candidates:
            grouped[candidate.id] = []
            for signal in active_signals:
                score = self._evaluate_signal(signal.name, job, candidate)
                result = self.signals.upsert_result(
                    candidate_id=candidate.id,
                    job_id=job.id,
                    signal_id=signal.id,
                    score=score.score,
                    weight=signal.default_weight,
                    reason=score.reason,
                )
                result.signal = signal
                grouped[candidate.id].append(result)

        return grouped

    def list_signals(self) -> list[Signal]:
        return self.signals.ensure_defaults(self.DEFAULT_SIGNALS)

    def list_results_for_job(self, job_id: int) -> list[SignalResult]:
        job = self.jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return self.signals.list_results_for_job(job_id)

    def _evaluate_signal(self, name: str, job: Job, candidate: Candidate) -> SignalScore:
        evaluators: dict[str, Callable[[Job, Candidate], SignalScore]] = {
            "Skill Match": self._skill_match,
            "Experience Match": self._experience_match,
            "Education Match": self._education_match,
            "Certification Match": self._certification_match,
            "Project Match": self._project_match,
            "Domain Match": self._domain_match,
            "Location Match": self._location_match,
            "Career Growth": self._career_growth,
            "Resume Quality": self._resume_quality,
            "GitHub Activity": self._github_activity,
            "Portfolio Quality": self._portfolio_quality,
            "Employment Stability": self._employment_stability,
            "Keyword Match": self._keyword_match,
            "Technology Freshness": self._technology_freshness,
            "Leadership": self._leadership,
            "Communication": self._communication,
            "Open Source Activity": self._open_source_activity,
            "Company Relevance": self._company_relevance,
            "Role Seniority": self._role_seniority,
            "Availability": self._availability,
        }
        return evaluators[name](job, candidate)

    def _skill_match(self, job: Job, candidate: Candidate) -> SignalScore:
        required = {skill.lower() for skill in (job.intelligence.skills if job.intelligence else [])}
        candidate_skills = {skill.lower() for skill in self._skills(candidate)}
        if not required:
            return SignalScore(60, "No extracted skills are available; neutral score assigned.")
        matched = sorted(required & candidate_skills)
        score = self._percent(len(matched), len(required))
        return SignalScore(score, f"Matched {len(matched)} of {len(required)} required skills: {', '.join(matched) or 'none'}.")

    def _experience_match(self, job: Job, candidate: Candidate) -> SignalScore:
        required_years = self._years(job.intelligence.experience if job.intelligence else "")
        candidate_years = self._years(candidate.experience)
        if required_years == 0:
            return SignalScore(65, "Job experience requirement is not specified.")
        if candidate_years >= required_years:
            return SignalScore(100, f"Candidate experience {candidate_years} years meets requirement of {required_years} years.")
        score = max(20, round((candidate_years / required_years) * 100, 2))
        return SignalScore(score, f"Candidate experience {candidate_years} years is below requirement of {required_years} years.")

    def _education_match(self, job: Job, candidate: Candidate) -> SignalScore:
        required = (job.intelligence.education if job.intelligence else "").lower()
        education = " ".join(candidate.profile.education if candidate.profile else []).lower()
        if not required or required == "not specified":
            return SignalScore(70, "Education requirement is not specified.")
        score = 100 if any(term in education for term in required.replace("'s", "").split()) else 45
        return SignalScore(score, "Candidate education evidence aligns with requirement." if score == 100 else "No clear education match found.")

    def _certification_match(self, job: Job, candidate: Candidate) -> SignalScore:
        required = {cert.lower() for cert in (job.intelligence.certifications if job.intelligence else [])}
        candidate_certs = {cert.lower() for cert in (candidate.profile.certifications if candidate.profile else [])}
        if not required:
            return SignalScore(70, "No required certifications were extracted.")
        matched = required & candidate_certs
        return SignalScore(self._percent(len(matched), len(required)), f"Matched certifications: {', '.join(sorted(matched)) or 'none'}.")

    def _project_match(self, job: Job, candidate: Candidate) -> SignalScore:
        project_text = self._projects_text(candidate)
        required = {skill.lower() for skill in (job.intelligence.skills if job.intelligence else [])}
        matched = [skill for skill in required if skill in project_text]
        score = min(100, 35 + len(matched) * 20 + min(20, len(candidate.profile.projects if candidate.profile else []) * 10))
        return SignalScore(score, f"Projects reference {len(matched)} relevant skills.")

    def _domain_match(self, job: Job, candidate: Candidate) -> SignalScore:
        industry = (job.intelligence.industry if job.intelligence else "").lower()
        text = self._candidate_text(candidate)
        if not industry or industry == "not specified":
            return SignalScore(65, "Job industry is not specified.")
        score = 90 if industry in text else 60 if any(term in text for term in ["recruit", "talent", "saas", "ai"]) else 35
        return SignalScore(score, "Candidate profile shows domain overlap." if score >= 60 else "Limited domain overlap found.")

    def _location_match(self, job: Job, candidate: Candidate) -> SignalScore:
        location = (job.intelligence.location if job.intelligence else "").lower()
        candidate_location = candidate.location.lower()
        if not location or location == "not specified":
            return SignalScore(70, "Job location is not specified.")
        if "remote" in candidate_location or "remote" in location:
            return SignalScore(85, "Remote compatibility found.")
        score = 100 if location in candidate_location or candidate_location in location else 45
        return SignalScore(score, "Candidate location matches job location." if score == 100 else "Candidate location differs from job location.")

    def _career_growth(self, job: Job, candidate: Candidate) -> SignalScore:
        years = self._years(candidate.experience)
        seniority = (job.intelligence.seniority if job.intelligence else "").lower()
        target = 8 if "lead" in seniority or "senior" in seniority else 4
        score = min(100, max(45, round((years / target) * 80, 2)))
        return SignalScore(score, f"Career maturity inferred from {years} years against {seniority or 'unspecified'} seniority.")

    def _resume_quality(self, job: Job, candidate: Candidate) -> SignalScore:
        insights = self._dict(candidate.profile.resume_insights if candidate.profile else None)
        points = 30
        points += 25 if candidate.summary else 0
        points += 20 if candidate.experience else 0
        points += 15 if insights.get("education") else 0
        points += 10 if insights.get("certifications") else 0
        return SignalScore(min(100, points), "Resume-derived fields are present and structured.")

    def _github_activity(self, job: Job, candidate: Candidate) -> SignalScore:
        insights = self._dict(candidate.profile.github_insights if candidate.profile else None)
        username = insights.get("username") or (candidate.profile.github_username if candidate.profile else "")
        project_count = int(insights.get("project_count") or 0)
        score = 25 + (35 if username else 0) + min(40, project_count * 20)
        return SignalScore(min(100, score), "GitHub username and project evidence are available." if username else "Limited GitHub evidence available.")

    def _portfolio_quality(self, job: Job, candidate: Candidate) -> SignalScore:
        insights = self._dict(candidate.profile.portfolio_insights if candidate.profile else None)
        url = insights.get("portfolio_url") or (candidate.profile.portfolio_url if candidate.profile else "")
        project_count = int(insights.get("project_count") or 0)
        score = 30 + (35 if url else 0) + min(35, project_count * 15)
        return SignalScore(min(100, score), "Portfolio and project evidence are available." if url else "No portfolio URL available.")

    def _employment_stability(self, job: Job, candidate: Candidate) -> SignalScore:
        years = self._years(candidate.experience)
        score = 55 + min(35, years * 5) + (10 if candidate.current_company else 0)
        return SignalScore(min(100, score), "Current company and experience provide employment continuity signal.")

    def _keyword_match(self, job: Job, candidate: Candidate) -> SignalScore:
        job_keywords = self._keywords(f"{job.title} {job.description}")
        candidate_keywords = self._keywords(self._candidate_text(candidate))
        matched = job_keywords & candidate_keywords
        score = self._percent(len(matched), max(1, min(15, len(job_keywords))))
        return SignalScore(score, f"Matched {len(matched)} meaningful job keywords.")

    def _technology_freshness(self, job: Job, candidate: Candidate) -> SignalScore:
        modern_terms = {"llm", "nlp", "react", "typescript", "fastapi", "kubernetes", "docker", "aws", "machine learning"}
        candidate_terms = set(self._candidate_text(candidate).split())
        matched = modern_terms & candidate_terms
        return SignalScore(min(100, 40 + len(matched) * 12), f"Modern technology matches: {', '.join(sorted(matched)) or 'none'}.")

    def _leadership(self, job: Job, candidate: Candidate) -> SignalScore:
        text = self._candidate_text(candidate)
        matches = [term for term in ["lead", "leadership", "mentor", "principal", "staff", "manager"] if term in text]
        score = min(100, 35 + len(matches) * 18)
        return SignalScore(score, f"Leadership terms found: {', '.join(matches) or 'none'}.")

    def _communication(self, job: Job, candidate: Candidate) -> SignalScore:
        summary_length = len(candidate.summary.split())
        normalized_length = len((candidate.profile.normalized_summary if candidate.profile and candidate.profile.normalized_summary else "").split())
        score = min(100, 40 + min(35, summary_length * 2) + min(25, normalized_length))
        return SignalScore(score, "Candidate profile has a readable summary and normalized narrative.")

    def _open_source_activity(self, job: Job, candidate: Candidate) -> SignalScore:
        text = self._candidate_text(candidate)
        has_github = bool(candidate.profile and candidate.profile.github_username)
        mentions_open_source = "open-source" in text or "open source" in text
        score = 30 + (40 if has_github else 0) + (30 if mentions_open_source else 0)
        return SignalScore(min(100, score), "Open-source evidence found." if mentions_open_source or has_github else "Limited open-source evidence found.")

    def _company_relevance(self, job: Job, candidate: Candidate) -> SignalScore:
        company = candidate.current_company.lower()
        text = self._candidate_text(candidate)
        score = 80 if any(term in company or term in text for term in ["hire", "people", "talent", "saas", "data", "cloud"]) else 45
        return SignalScore(score, "Company/domain context appears relevant." if score >= 80 else "Company relevance is limited.")

    def _role_seniority(self, job: Job, candidate: Candidate) -> SignalScore:
        years = self._years(candidate.experience)
        seniority = (job.intelligence.seniority if job.intelligence else job.title).lower()
        if any(term in seniority for term in ["lead", "principal", "staff"]):
            score = 95 if years >= 8 else 70 if years >= 5 else 40
        elif "senior" in seniority:
            score = 95 if years >= 5 else 55
        else:
            score = 80 if years >= 2 else 55
        return SignalScore(score, f"Role seniority inferred from {years} years and job seniority '{seniority or 'unspecified'}'.")

    def _availability(self, job: Job, candidate: Candidate) -> SignalScore:
        coverage = self._dict(candidate.profile.source_coverage if candidate.profile else None)
        completeness = float(coverage.get("completeness") or 0)
        remote_bonus = 15 if "remote" in candidate.location.lower() else 0
        score = min(100, 45 + completeness * 40 + remote_bonus)
        return SignalScore(score, "Availability inferred from source completeness and location flexibility.")

    def _skills(self, candidate: Candidate) -> list[str]:
        return candidate.profile.skills if candidate.profile else []

    def _candidate_text(self, candidate: Candidate) -> str:
        profile = candidate.profile
        values: list[str] = [
            candidate.full_name,
            candidate.summary,
            candidate.experience,
            candidate.current_company,
            candidate.location,
        ]
        if profile:
            values.extend(profile.skills)
            values.extend(profile.education)
            values.extend(profile.certifications)
            values.append(profile.normalized_summary or "")
            values.append(self._projects_text(candidate))
        return " ".join(values).lower()

    def _projects_text(self, candidate: Candidate) -> str:
        if not candidate.profile:
            return ""
        return " ".join(
            " ".join(str(value) for value in project.values())
            for project in candidate.profile.projects
        ).lower()

    def _keywords(self, text: str) -> set[str]:
        stop_words = {"with", "and", "the", "for", "from", "this", "that", "using", "need", "build", "role"}
        return {word for word in re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", text.lower()) if word not in stop_words}

    def _years(self, value: str) -> int:
        match = re.search(r"(\d+)", value or "")
        return int(match.group(1)) if match else 0

    def _percent(self, numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0
        return round((numerator / denominator) * 100, 2)

    def _dict(self, value: dict[str, Any] | None) -> dict[str, Any]:
        return value or {}
