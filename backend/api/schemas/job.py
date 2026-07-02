from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from api.schemas.job_intelligence import JobIntelligenceRead

JobStatus = Literal["draft", "analyzed", "searching", "ranked", "archived"]


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    company_name: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=20)
    status: JobStatus = "draft"


class JobRead(BaseModel):
    id: int
    title: str
    company_name: str
    description: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    intelligence: JobIntelligenceRead | None = None

    model_config = ConfigDict(from_attributes=True)
