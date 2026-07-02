from dataclasses import dataclass, field
from typing import Protocol

from api.core.config import settings
from api.models.job import Job
from api.models.job_intelligence import JobIntelligence


@dataclass(frozen=True)
class CandidateSourceResult:
    full_name: str
    email: str
    phone: str
    location: str
    summary: str
    experience: str
    current_company: str
    source: str
    external_id: str
    profile_url: str
    skills: list[str] = field(default_factory=list)
    projects: list[dict[str, str]] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    github_username: str = ""
    portfolio_url: str = ""
    resume_path: str = ""
    match_reasons: list[str] = field(default_factory=list)


class TalentSource(Protocol):
    source_name: str

    def search_candidates(
        self,
        job: Job,
        intelligence: JobIntelligence | None,
        limit: int = 8,
    ) -> list[CandidateSourceResult]:
        ...


class MockTalentSource:
    def __init__(self, source_name: str, candidates: list[CandidateSourceResult]) -> None:
        self.source_name = source_name
        self._candidates = candidates

    def search_candidates(
        self,
        job: Job,
        intelligence: JobIntelligence | None,
        limit: int = 8,
    ) -> list[CandidateSourceResult]:
        required_skills = {skill.lower() for skill in intelligence.skills} if intelligence else set()
        title_terms = {term.strip(".,()").lower() for term in job.title.split() if len(term) > 3}

        def relevance(candidate: CandidateSourceResult) -> int:
            candidate_skills = {skill.lower() for skill in candidate.skills}
            summary_terms = set(candidate.summary.lower().split())
            return len(required_skills & candidate_skills) * 3 + len(title_terms & summary_terms)

        ranked = sorted(self._candidates, key=relevance, reverse=True)
        return ranked[:limit]


def get_default_talent_sources() -> list[TalentSource]:
    if settings.use_mock_talent_sources:
        return [
            MockTalentSource(
                "internal_db",
                [
                    CandidateSourceResult(
                        full_name="Aarav Mehta",
                        email="aarav.mehta@example.com",
                        phone="+91-90000-10001",
                        location="Bengaluru",
                        summary="Senior backend engineer building AI recruiter workflows with Python and FastAPI.",
                        experience="6 years",
                        current_company="HireLoop",
                        source="internal_db",
                        external_id="int-aarav-mehta",
                        profile_url="https://talent.internal.example/candidates/aarav-mehta",
                        skills=["Python", "FastAPI", "PostgreSQL", "Machine Learning", "Docker"],
                        projects=[
                            {
                                "name": "Recruiter ranking API",
                                "description": "Built candidate retrieval and scoring services for hiring teams.",
                            }
                        ],
                        education=["B.Tech Computer Science"],
                        certifications=["AWS Certified"],
                        github_username="aaravmehta",
                        portfolio_url="https://aaravmehta.example",
                        match_reasons=["Strong backend skill overlap", "Relevant talent-tech domain work"],
                    ),
                    CandidateSourceResult(
                        full_name="Meera Iyer",
                        email="meera.iyer@example.com",
                        phone="+91-90000-10002",
                        location="Hyderabad",
                        summary="Full-stack engineer focused on React, TypeScript, and analytics-heavy dashboards.",
                        experience="5 years",
                        current_company="PeopleGrid",
                        source="internal_db",
                        external_id="int-meera-iyer",
                        profile_url="https://talent.internal.example/candidates/meera-iyer",
                        skills=["React", "TypeScript", "JavaScript", "PostgreSQL"],
                        projects=[
                            {
                                "name": "Recruiter cockpit",
                                "description": "Designed high-density job and candidate review workflows.",
                            }
                        ],
                        education=["B.E. Information Technology"],
                        certifications=[],
                        github_username="meera-ai",
                        portfolio_url="https://meera.design",
                        match_reasons=["Strong frontend match", "Dashboard product experience"],
                    ),
                ],
            ),
            MockTalentSource(
                "github",
                [
                    CandidateSourceResult(
                        full_name="Kabir Rao",
                        email="kabir.rao@example.com",
                        phone="+91-90000-10003",
                        location="Pune",
                        summary="Open-source contributor in Python, LLM tooling, and data pipelines.",
                        experience="7 years",
                        current_company="DataForge",
                        source="github",
                        external_id="gh-kabirrao",
                        profile_url="https://github.com/kabirrao",
                        skills=["Python", "LLM", "NLP", "Data Engineering", "Kubernetes"],
                        projects=[
                            {
                                "name": "llm-eval-kit",
                                "description": "Open-source toolkit for evaluating language model outputs.",
                            }
                        ],
                        education=["M.Tech Data Science"],
                        certifications=["CKA"],
                        github_username="kabirrao",
                        portfolio_url="https://kabirrao.dev",
                        match_reasons=["High AI and data engineering overlap", "Visible open-source activity"],
                    ),
                    CandidateSourceResult(
                        full_name="Vedant Kadlak",
                        email="vedant.kadlak@example.com",
                        phone="+91-90000-10006",
                        location="Mumbai",
                        summary="Computer Vision Engineer with internship experience building AI applications using Python, OpenCV, YOLO, FastAPI, and MediaPipe.",
                        experience="1 year",
                        current_company="Nilee Games",
                        source="internal_db",
                        external_id="int-vedant-kadlak",
                        profile_url="https://talent.internal.example/candidates/vedant-kadlak",
                        skills=[
                            "Python",
                            "OpenCV",
                            "FastAPI",
                            "YOLO",
                            "MediaPipe",
                            "Machine Learning",
                            "Docker",
                            "PostgreSQL"
                        ],
                        projects=[
                            {
                                "name": "Ball Impact Detection",
                                "description": "Developed a real-time ball tracking and impact detection system."
                            },
                            {
                                "name": "Pose Tracking Engine",
                                "description": "Integrated MediaPipe with Unity for full body tracking."
                            }
                        ],
                        education=["B.E. Computer Engineering"],
                        certifications=[],
                        github_username="vedantkadlakk",
                        portfolio_url="https://vedant.dev",
                        match_reasons=["Strong Computer Vision background", "FastAPI experience"]
                    ),

                    CandidateSourceResult(
                        full_name="Priya Sharma",
                        email="priya.sharma@example.com",
                        phone="+91-90000-10007",
                        location="Pune",
                        summary="Fresher Python developer passionate about backend development and REST APIs.",
                        experience="0 years",
                        current_company="Fresher",
                        source="internal_db",
                        external_id="int-priya",
                        profile_url="https://talent.internal.example/candidates/priya",
                        skills=["Python", "Flask", "SQL", "Git"],
                        projects=[
                            {
                                "name": "Library Management System",
                                "description": "Built CRUD application using Flask and SQLite."
                            }
                        ],
                        education=["B.Tech Information Technology"],
                        certifications=[],
                        github_username="priyasharma",
                        portfolio_url="",
                        match_reasons=["Strong academic projects"]
                    ),

                    CandidateSourceResult(
                        full_name="Arjun Nair",
                        email="arjun.nair@example.com",
                        phone="+91-90000-10008",
                        location="Chennai",
                        summary="Backend developer specializing in FastAPI and PostgreSQL.",
                        experience="2 years",
                        current_company="TechNova",
                        source="internal_db",
                        external_id="int-arjun",
                        profile_url="https://talent.internal.example/candidates/arjun",
                        skills=[
                            "Python",
                            "FastAPI",
                            "Redis",
                            "Docker",
                            "PostgreSQL"
                        ],
                        projects=[
                            {
                                "name": "Order Management API",
                                "description": "Designed scalable REST APIs for logistics."
                            }
                        ],
                        education=["B.E Computer Science"],
                        certifications=["AWS Cloud Practitioner"],
                        github_username="arjunnair",
                        portfolio_url="https://arjun.dev",
                        match_reasons=["Strong backend architecture"]
                    ),

                    CandidateSourceResult(
                        full_name="Sneha Kulkarni",
                        email="sneha.k@example.com",
                        phone="+91-90000-10009",
                        location="Bengaluru",
                        summary="React and Angular frontend developer creating enterprise dashboards.",
                        experience="3 years",
                        current_company="Bluefield Technologies",
                        source="linkedin_mock",
                        external_id="li-sneha",
                        profile_url="https://linkedin.example/in/sneha",
                        skills=[
                            "Angular",
                            "React",
                            "TypeScript",
                            "JavaScript",
                            "HTML",
                            "CSS"
                        ],
                        projects=[
                            {
                                "name": "Analytics Dashboard",
                                "description": "Developed KPI dashboards for enterprise clients."
                            }
                        ],
                        education=["B.Tech Computer Science"],
                        certifications=[],
                        github_username="",
                        portfolio_url="",
                        match_reasons=["Excellent frontend expertise"]
                    ),

                    CandidateSourceResult(
                        full_name="Rahul Gupta",
                        email="rahul.g@example.com",
                        phone="+91-90000-10010",
                        location="Noida",
                        summary="SQL developer experienced in writing optimized queries and stored procedures.",
                        experience="2 years",
                        current_company="HighBeats Tech",
                        source="internal_db",
                        external_id="int-rahul",
                        profile_url="https://talent.internal.example/candidates/rahul",
                        skills=[
                            "SQL",
                            "PostgreSQL",
                            "MySQL",
                            "Database Design",
                            "Performance Tuning"
                        ],
                        projects=[
                            {
                                "name": "Sales Data Warehouse",
                                "description": "Optimized complex SQL queries improving performance by 60%."
                            }
                        ],
                        education=["B.Sc Computer Science"],
                        certifications=[],
                        github_username="rahulsql",
                        portfolio_url="",
                        match_reasons=["Excellent SQL optimization"]
                    ),

                    CandidateSourceResult(
                        full_name="Ananya Patel",
                        email="ananya@example.com",
                        phone="+91-90000-10011",
                        location="Ahmedabad",
                        summary="Machine Learning engineer focused on NLP, LLMs, and recommendation systems.",
                        experience="3 years",
                        current_company="AI Nexus",
                        source="github",
                        external_id="gh-ananya",
                        profile_url="https://github.com/ananyapatel",
                        skills=[
                            "Python",
                            "PyTorch",
                            "LLM",
                            "NLP",
                            "Machine Learning",
                            "Docker"
                        ],
                        projects=[
                            {
                                "name": "Resume Ranking AI",
                                "description": "Built semantic resume ranking system using embeddings."
                            }
                        ],
                        education=["M.Tech Artificial Intelligence"],
                        certifications=["TensorFlow Developer"],
                        github_username="ananyapatel",
                        portfolio_url="https://ananya.ai",
                        match_reasons=["Excellent AI expertise"]
                    ),

                    CandidateSourceResult(
                        full_name="Karan Singh",
                        email="karan@example.com",
                        phone="+91-90000-10012",
                        location="Delhi",
                        summary="Recent graduate with strong Java, Spring Boot and DSA skills.",
                        experience="0 years",
                        current_company="Fresher",
                        source="linkedin_mock",
                        external_id="li-karan",
                        profile_url="https://linkedin.example/in/karan",
                        skills=[
                            "Java",
                            "Spring Boot",
                            "SQL",
                            "Git",
                            "OOP"
                        ],
                        projects=[
                            {
                                "name": "Employee Management System",
                                "description": "Developed backend services using Spring Boot."
                            }
                        ],
                        education=["B.Tech Computer Science"],
                        certifications=[],
                        github_username="karansingh",
                        portfolio_url="",
                        match_reasons=["Strong DSA fundamentals"]
                    ),

                    CandidateSourceResult(
                        full_name="Neha Joshi",
                        email="neha@example.com",
                        phone="+91-90000-10013",
                        location="Hyderabad",
                        summary="DevOps engineer with experience in AWS, Kubernetes and CI/CD pipelines.",
                        experience="4 years",
                        current_company="CloudOps",
                        source="github",
                        external_id="gh-neha",
                        profile_url="https://github.com/nehajoshi",
                        skills=[
                            "AWS",
                            "Docker",
                            "Kubernetes",
                            "Terraform",
                            "CI/CD",
                            "Python"
                        ],
                        projects=[
                            {
                                "name": "Infrastructure Automation",
                                "description": "Automated cloud infrastructure using Terraform."
                            }
                        ],
                        education=["B.Tech Information Technology"],
                        certifications=[
                            "AWS Solutions Architect Associate",
                            "CKA"
                        ],
                        github_username="nehajoshi",
                        portfolio_url="https://nehadevops.dev",
                        match_reasons=["Excellent cloud engineering experience"]
                    ),
                    CandidateSourceResult(
                        full_name="Nisha Shah",
                        email="nisha.shah@example.com",
                        phone="+91-90000-10004",
                        location="Remote",
                        summary="Platform engineer with Docker, Kubernetes, AWS, and production API ownership.",
                        experience="8 years",
                        current_company="CloudNest",
                        source="github",
                        external_id="gh-nishashah",
                        profile_url="https://github.com/nishashah",
                        skills=["AWS", "Docker", "Kubernetes", "Python", "FastAPI"],
                        projects=[
                            {
                                "name": "deployment-control-plane",
                                "description": "Built internal services for repeatable cloud deployments.",
                            }
                        ],
                        education=["Bachelor's degree in Computer Engineering"],
                        certifications=["AWS Certified", "CKA"],
                        github_username="nishashah",
                        portfolio_url="https://nishashah.dev",
                        match_reasons=["Strong infrastructure match", "Senior platform ownership"],
                    ),
                ],
            ),
            MockTalentSource(
                "linkedin_mock",
                [
                    CandidateSourceResult(
                        full_name="Rohan Kapoor",
                        email="rohan.kapoor@example.com",
                        phone="+91-90000-10005",
                        location="Gurugram",
                        summary="Engineering lead for B2B SaaS products with hiring and mentoring experience.",
                        experience="10 years",
                        current_company="SaaSWorks",
                        source="linkedin_mock",
                        external_id="li-rohan-kapoor",
                        profile_url="https://linkedin.example/in/rohan-kapoor",
                        skills=["Leadership", "React", "TypeScript", "AWS", "SaaS"],
                        projects=[
                            {
                                "name": "enterprise onboarding suite",
                                "description": "Led product engineering for a workflow-heavy SaaS platform.",
                            }
                        ],
                        education=["MBA", "B.Tech Computer Science"],
                        certifications=["Scrum Master"],
                        github_username="",
                        portfolio_url="",
                        match_reasons=["Leadership signal", "Relevant SaaS product background"],
                    )
                ],
            ),
            
        ]

    from api.integrations.github_client import GitHubClient
    from api.integrations.github_source import GitHubTalentSource

    return [GitHubTalentSource(GitHubClient(settings.github_token))]
