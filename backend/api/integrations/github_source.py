import httpx

from api.integrations.github_client import GitHubClient
from api.integrations.talent_sources import CandidateSourceResult, TalentSource
from api.models.job import Job
from api.models.job_intelligence import JobIntelligence


class GitHubTalentSource:
    source_name = "github"

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def search_candidates(
        self,
        job: Job,
        intelligence: JobIntelligence | None,
        limit: int = 8,
    ) -> list[CandidateSourceResult]:
        query = self._build_query(intelligence, job)
        users = self.client.search_users(query, per_page=limit * 2)
        candidates: list[CandidateSourceResult] = []

        for user in users[:limit]:
            login = user.get("login")
            if not login:
                continue

            try:
                profile = self.client.get_user(login)
                repos = self.client.get_repositories(login, per_page=5)
            except httpx.HTTPError:
                continue

            candidates.append(self._to_candidate(profile, repos))

        return candidates

    def _build_query(self, intelligence: JobIntelligence | None, job: Job) -> str:
        query_parts: list[str] = []

        if intelligence is not None:
            location = (intelligence.location or "").strip()
            if location:
                query_parts.append(f"location:{location}")

            primary_language = self._primary_language(intelligence.skills)
            if primary_language:
                query_parts.append(f"language:{primary_language}")

        if not query_parts:
            title = job.title.strip()
            if title:
                query_parts.append(title)

        return " ".join(query_parts) if query_parts else ""

    def _primary_language(self, skills: list[str] | None) -> str | None:
        if not skills:
            return None

        supported = {
            "Python",
            "TypeScript",
            "Go",
            "Rust",
            "JavaScript",
            "Java",
            "C#",
            "C++",
            "Ruby",
            "PHP",
            "Kotlin",
        }

        for skill in skills:
            normalized = skill.strip()
            if normalized in supported:
                return normalized

        for skill in skills:
            if normalized := skill.strip().lower():
                if normalized == "docker":
                    return "Dockerfile"

        return None

    def _detect_skills(self, repositories: list[dict[str, object]]) -> list[str]:
        found: set[str] = set()
        languages = {repo.get("language") for repo in repositories if repo.get("language")}

        if "Python" in languages:
            found.add("Python")
        if "TypeScript" in languages:
            found.add("TypeScript")
        if "Go" in languages:
            found.add("Go")
        if "Rust" in languages:
            found.add("Rust")

        for repo in repositories:
            description = (repo.get("description") or "").lower()
            name = (repo.get("name") or "").lower()
            if "docker" in description or "docker" in name:
                found.add("Docker")

        return sorted(found)

    def _to_candidate(
        self,
        profile: dict[str, object],
        repos: list[dict[str, object]],
    ) -> CandidateSourceResult:
        login = str(profile.get("login", ""))
        full_name = str(profile.get("name") or login)
        location = str(profile.get("location") or "")
        summary = str(profile.get("bio") or f"GitHub profile for {login}")
        current_company = str(profile.get("company") or "")
        portfolio_url = str(profile.get("blog") or "")
        html_url = str(profile.get("html_url") or profile.get("url") or "")

        projects = []
        for repo in repos:
            projects.append(
                {
                    "name": str(repo.get("name", "")),
                    "description": str(repo.get("description") or ""),
                }
            )

        return CandidateSourceResult(
            full_name=full_name,
            email="",
            phone="",
            location=location,
            summary=summary,
            experience="Unknown",
            current_company=current_company,
            source="github",
            external_id=login,
            profile_url=html_url,
            skills=self._detect_skills(repos),
            projects=projects,
            education=[],
            certifications=[],
            github_username=login,
            portfolio_url=portfolio_url,
            match_reasons=["Matched GitHub profile"],
        )
