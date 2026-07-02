from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SignalRead(BaseModel):
    id: int
    name: str
    category: str
    description: str
    default_weight: float
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SignalResultRead(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    signal_id: int
    signal_name: str
    category: str
    score: float
    weight: float
    contribution: float
    reason: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateSignalEvaluation(BaseModel):
    candidate_id: int
    result_count: int
    results: list[SignalResultRead]


class SignalEvaluationResponse(BaseModel):
    job_id: int
    candidate_count: int
    signal_count: int
    results: list[CandidateSignalEvaluation]
