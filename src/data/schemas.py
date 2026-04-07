from typing import List

from pydantic import BaseModel, Field


class JobInput(BaseModel):
    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    company_name: str = Field(min_length=1)


class ScoreRequest(BaseModel):
    cv_text: str = Field(min_length=1)
    jobs: List[JobInput] = Field(min_length=1)
    top_k: int = Field(default=8, ge=1, le=8)


class RankedResult(BaseModel):
    rank: int
    job_id: str
    score: float
    label: str
    top_terms: List[str]


class ExcludedJob(BaseModel):
    job_id: str
    reason: str


class ScoreResponse(BaseModel):
    request_id: str
    scorer_source: str
    ranked_results: List[RankedResult]
    excluded_jobs: List[ExcludedJob]
    latency_ms: float
