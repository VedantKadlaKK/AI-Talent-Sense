import json
import re
import time
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
        try:
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
                    "max_tokens": 2048,
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            return self._handle_grok_error(error)
        except requests.exceptions.RequestException as error:
            raise ValueError(f"Grok API request failed: {error}") from error

        body = response.json()
        content = body["choices"][0]["message"]["content"]
        return self._parse_grok_response(content)

    def _request_grok_explanation(
        self,
        job: dict[str, Any],
        candidate: dict[str, Any],
        signal_results: list[dict[str, Any]],
        overall_score: float,
    ) -> dict[str, Any]:
        prompt = self._build_explanation_prompt(job, candidate, signal_results, overall_score)
        try:
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
                    "max_tokens": 2048,
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            return self._handle_grok_error(error)
        except requests.exceptions.RequestException as error:
            raise ValueError(f"Grok API request failed: {error}") from error

        body = response.json()
        content = body["choices"][0]["message"]["content"]
        return self._parse_grok_response(content)

    def _handle_grok_error(self, error: requests.exceptions.HTTPError) -> dict[str, Any]:
        if error.response is not None and error.response.status_code == 429:
            retry_after = 5
            try:
                error_data = error.response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    msg = error_data["error"]["message"]
                    match = re.search(r"try again in ([0-9.]+)s", msg)
                    if match:
                        retry_after = float(match.group(1)) + 1.0
            except (ValueError, KeyError, IndexError):
                pass

            raise ValueError(
                f"Grok rate limit hit (429). Retry after {retry_after:.1f}s. "
                f"Or set USE_MOCK_AI=true to use fallback mode."
            ) from error

        response_text = error.response.text if error.response is not None else "<no response>"
        raise ValueError(
            f"Grok API returned HTTP error {error.response.status_code}: {response_text}"
        ) from error

    def _build_explanation_prompt(
        self,
        job: dict[str, Any],
        candidate: dict[str, Any],
        signal_results: list[dict[str, Any]],
        overall_score: float,
    ) -> str:
        def format_list(items: list[Any], max_items: int = 8) -> str:
            if not items:
                return "None"
            return ", ".join(str(item) for item in items[:max_items])

        def truncate(text: str, max_length: int = 200) -> str:
            return text if len(text) <= max_length else text[: max_length - 3].rstrip() + "..."

        job_fields = [
            f"Title: {job.get('title', '')}",
            f"Company: {job.get('company_name', '')}",
            f"Skills: {format_list(job.get('skills', []), max_items=8)}",
            f"Experience: {job.get('experience', '')}",
            f"Education: {job.get('education', '')}",
            f"Location: {job.get('location', '')}",
            f"Seniority: {job.get('seniority', '')}",
        ]

        candidate_fields = [
            f"Name: {candidate.get('full_name', '')}",
            f"Company: {candidate.get('current_company', '')}",
            f"Location: {candidate.get('location', '')}",
            f"Experience: {candidate.get('experience', '')}",
            f"Skills: {format_list(candidate.get('skills', []), max_items=8)}",
            f"Summary: {truncate(str(candidate.get('summary', '')))}",
        ]

        top_signals = sorted(signal_results, key=lambda item: item.get('contribution', 0), reverse=True)[:5]
        signal_lines = [
            f"{idx + 1}. {signal.get('signal_name', 'Unknown')} (score {round(signal.get('score', 0), 1)}): {signal.get('reason', '')}"
            for idx, signal in enumerate(top_signals)
        ]

        return (
            "Explain this recruiting recommendation. Return only JSON with keys: summary, strengths, weaknesses, missing_skills, recommendation. "
            "Do not include markdown fences or any extra text outside the JSON object.\n\n"
            "Job:\n"
            + "\n".join(job_fields)
            + "\n\nCandidate:\n"
            + "\n".join(candidate_fields)
            + "\n\nOverall score: "
            + str(overall_score)
            + "\n\nTop signals:\n"
            + "\n".join(signal_lines)
        )

    def _parse_grok_response(self, content: str) -> dict[str, Any]:
        content = content.strip()
        fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if fenced_match:
            content = fenced_match.group(1)
        elif content.startswith("json\n") or content.startswith("json\r\n"):
            content = content.splitlines(1)[1]
        elif content.startswith("```") and content.endswith("```"):
            stripped = content.strip("`").strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                content = stripped

        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            inner_match = re.search(r"(\{.*\})", content, re.DOTALL)
            if inner_match:
                try:
                    return json.loads(inner_match.group(1))
                except json.JSONDecodeError:
                    pass
            raise ValueError(
                "Grok API returned invalid JSON. Check the raw response content. "
                f"Response content: {content!r}"
            ) from error

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

    def _parse_grok_response(self, content: str) -> dict[str, Any]:
        content = content.strip()
        fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if fenced_match:
            content = fenced_match.group(1)
        elif content.startswith("json\n") or content.startswith("json\r\n"):
            content = content.splitlines(1)[1]
        elif content.startswith("```") and content.endswith("```"):
            stripped = content.strip("`").strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                content = stripped

        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            inner_match = re.search(r"(\{.*\})", content, re.DOTALL)
            if inner_match:
                try:
                    return json.loads(inner_match.group(1))
                except json.JSONDecodeError:
                    pass
            raise ValueError(
                "Grok API returned invalid JSON. Check the raw response content. "
                f"Response content: {content!r}"
            ) from error

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
