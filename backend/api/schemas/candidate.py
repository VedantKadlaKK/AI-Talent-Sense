from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CandidateSourceRead(BaseModel):
    id: int
    source: str
    external_id: str
    profile_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateProfileRead(BaseModel):
    id: int
    skills: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    github_username: str = ""
    portfolio_url: str = ""
    resume_path: str = ""
    normalized_summary: str | None = None
    source_coverage: dict[str, Any] | None = None
    resume_insights: dict[str, Any] | None = None
    github_insights: dict[str, Any] | None = None
    portfolio_insights: dict[str, Any] | None = None
    api_insights: dict[str, Any] | None = None
    normalized_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateRead(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    location: str
    summary: str
    experience: str
    current_company: str
    sources: list[CandidateSourceRead] = Field(default_factory=list)
    profile: CandidateProfileRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateSearchResponse(BaseModel):
    job_id: int
    source_count: int
    candidate_count: int
    candidates: list[CandidateRead]


class CandidateIntelligenceBatchResponse(BaseModel):
    job_id: int
    normalized_count: int
    candidates: list[CandidateRead]
