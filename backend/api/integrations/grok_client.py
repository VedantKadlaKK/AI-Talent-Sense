import json
import re
from typing import Any

import requests

from api.core.config import settings


class GrokClient:
    def analyze_job_description(self, title: str, description: str) -> dict[str, Any]:
        if settings.use_mock_ai or not settings.grok_api_key:
            return self._heuristic_analysis(title, description)
        return self._request_grok(title, description)

    def explain_candidate_recommendation(
        self,
        job: dict[str, Any],
        candidate: dict[str, Any],
        signal_results: list[dict[str, Any]],
        overall_score: float,
    ) -> dict[str, Any]:
        if settings.use_mock_ai or not settings.grok_api_key:
            return self._heuristic_explanation(job, candidate, signal_results, overall_score)
        return self._request_grok_explanation(job, candidate, signal_results, overall_score)

    def _request_grok(self, title: str, description: str) -> dict[str, Any]:
        prompt = (
            "Extract hiring requirements from this job description. "
            "Return only JSON with keys: skills, experience, education, industry, "
            "location, seniority, certifications, nice_to_have_skills.\n\n"
            f"Title: {title}\n\nDescription:\n{description}"
        )
        response = requests.post(
            settings.grok_api_url,
            headers={
                "Authorization": f"Bearer {settings.grok_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.grok_model,
                "messages": [
                    {"role": "system", "content": "You extract structured recruiting requirements."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            },
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        content = body["choices"][0]["message"]["content"]
        return json.loads(content)

    def _request_grok_explanation(
        self,
        job: dict[str, Any],
        candidate: dict[str, Any],
        signal_results: list[dict[str, Any]],
        overall_score: float,
    ) -> dict[str, Any]:
        prompt = (
            "Explain this recruiting recommendation. Return only JSON with keys: "
            "summary, strengths, weaknesses, missing_skills, recommendation.\n\n"
            f"Job:\n{json.dumps(job)}\n\n"
            f"Candidate:\n{json.dumps(candidate)}\n\n"
            f"Overall score: {overall_score}\n\n"
            f"Signal results:\n{json.dumps(signal_results)}"
        )
        response = requests.post(
            settings.grok_api_url,
            headers={
                "Authorization": f"Bearer {settings.grok_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.grok_model,
                "messages": [
                    {"role": "system", "content": "You explain candidate rankings for recruiters."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        content = body["choices"][0]["message"]["content"]
        return json.loads(content)

    def _heuristic_analysis(self, title: str, description: str) -> dict[str, Any]:
        text = f"{title}\n{description}"
        lowered = text.lower()

        skill_catalog = [
            "Python",
            "React",
            "TypeScript",
            "JavaScript",
            "FastAPI",
            "SQLAlchemy",
            "PostgreSQL",
            "Machine Learning",
            "NLP",
            "LLM",
            "AWS",
            "Docker",
            "Kubernetes",
            "GitHub",
            "Data Engineering",
            "Leadership",
        ]
        skills = [skill for skill in skill_catalog if skill.lower() in lowered]

        nice_to_have_markers = ["nice to have", "preferred", "bonus", "good to have"]
        nice_to_have_skills = [
            skill
            for skill in skill_catalog
            if skill.lower() in lowered and any(marker in lowered for marker in nice_to_have_markers)
        ]

        experience_match = re.search(r"(\d+)\+?\s*(?:years|yrs)", lowered)
        experience = f"{experience_match.group(1)}+ years" if experience_match else "Not specified"

        education = self._first_match(
            lowered,
            {
                "Bachelor's degree": ["bachelor", "b.tech", "b.e."],
                "Master's degree": ["master", "m.tech", "m.s.", "msc"],
                "PhD": ["phd", "doctorate"],
            },
        )
        seniority = self._first_match(
            lowered,
            {
                "Executive": ["chief", "vp ", "vice president", "head of"],
                "Lead": ["lead", "principal", "staff"],
                "Senior": ["senior", "sr."],
                "Mid-level": ["mid", "software engineer", "developer"],
                "Entry-level": ["junior", "graduate", "entry"],
            },
        )
        industry = self._first_match(
            lowered,
            {
                "Talent Technology": ["recruit", "talent", "sourcing", "hiring"],
                "Financial Services": ["fintech", "bank", "payments"],
                "Healthcare": ["healthcare", "clinical", "patient"],
                "SaaS": ["saas", "b2b", "subscription"],
                "AI": ["ai", "machine learning", "llm", "nlp"],
            },
        )
        location = self._extract_location(text)
        certifications = [
            certification
            for certification in ["AWS Certified", "PMP", "CKA", "Scrum Master"]
            if certification.lower() in lowered
        ]

        result = {
            "skills": skills,
            "experience": experience,
            "education": education,
            "industry": industry,
            "location": location,
            "seniority": seniority,
            "certifications": certifications,
            "nice_to_have_skills": nice_to_have_skills,
        }
        return {**result, "raw_ai_output": {"provider": "heuristic", "result": result}}

    def _heuristic_explanation(
        self,
        job: dict[str, Any],
        candidate: dict[str, Any],
        signal_results: list[dict[str, Any]],
        overall_score: float,
    ) -> dict[str, Any]:
        sorted_results = sorted(signal_results, key=lambda result: result["contribution"], reverse=True)
        strongest = sorted_results[:3]
        weakest = sorted(signal_results, key=lambda result: result["score"])[:3]
        required_skills = {skill.lower() for skill in job.get("skills", [])}
        candidate_skills = {skill.lower() for skill in candidate.get("skills", [])}
        missing_skills = sorted(required_skills - candidate_skills)
        candidate_name = candidate.get("full_name", "This candidate")
        role = job.get("title", "this role")
        recommendation = "Strong Match" if overall_score >= 75 else "Review" if overall_score >= 55 else "Low Match"

        return {
            "summary": (
                f"{candidate_name} scored {overall_score:.1f} for {role}. "
                f"The ranking is driven by {', '.join(result['signal_name'] for result in strongest) or 'available signal evidence'}."
            ),
            "strengths": [f"{result['signal_name']}: {result['reason']}" for result in strongest],
            "weaknesses": [f"{result['signal_name']}: {result['reason']}" for result in weakest],
            "missing_skills": missing_skills,
            "recommendation": recommendation,
            "provider": "heuristic",
        }

    def _first_match(self, text: str, patterns: dict[str, list[str]]) -> str:
        for label, keywords in patterns.items():
            if any(keyword in text for keyword in keywords):
                return label
        return "Not specified"

    def _extract_location(self, text: str) -> str:
        match = re.search(r"(?:location|based in|work from)\s*[:\-]?\s*([A-Za-z ,/-]{2,80})", text, re.IGNORECASE)
        if not match:
            return "Not specified"
        return match.group(1).splitlines()[0].strip(" .")
