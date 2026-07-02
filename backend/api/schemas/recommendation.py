from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from api.schemas.candidate import CandidateRead
from api.schemas.signal import SignalResultRead


class RecommendationRead(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    overall_score: float
    rank: int
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendation: str
    raw_ai_output: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationCandidateRead(BaseModel):
    recommendation: RecommendationRead
    candidate: CandidateRead
    signals: list[SignalResultRead] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    job_id: int
    recommendation_count: int
    recommendations: list[RecommendationCandidateRead]
