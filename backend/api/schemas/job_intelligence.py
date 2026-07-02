from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobIntelligenceBase(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience: str = ""
    education: str = ""
    industry: str = ""
    location: str = ""
    seniority: str = ""
    certifications: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    raw_ai_output: dict[str, Any] = Field(default_factory=dict)


class JobIntelligenceCreate(JobIntelligenceBase):
    job_id: int


class JobIntelligenceRead(JobIntelligenceBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
