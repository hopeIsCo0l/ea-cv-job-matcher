import time
import uuid

from fastapi import APIRouter, HTTPException, Request

from src.config.settings import MAX_JOBS_PER_REQUEST, RELEASE_TAG, SCORER_SOURCE
from src.data.schemas import ScoreRequest, ScoreResponse
from src.scoring.domain import filter_and_cap_jobs
from src.scoring.engine import TfidfScorer
from src.scoring.text_utils import normalize_text

router = APIRouter()
scorer = TfidfScorer()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict:
    return {"status": "ready", "scorer_source": SCORER_SOURCE, "release_tag": RELEASE_TAG}


@router.post("/v1/score", response_model=ScoreResponse)
def score(request: Request, payload: ScoreRequest) -> dict:
    started = time.perf_counter()
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if not normalize_text(payload.cv_text):
        raise HTTPException(status_code=400, detail="CV text cannot be empty after normalization")
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="At least one job is required")

    valid_jobs, excluded = filter_and_cap_jobs(payload.jobs)
    if not valid_jobs:
        raise HTTPException(status_code=400, detail="No valid Ethiopian Airlines jobs found")

    ranked = scorer.score_jobs(payload.cv_text, valid_jobs)
    top_k = min(payload.top_k, MAX_JOBS_PER_REQUEST)
    ranked = ranked[:top_k]

    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "request_id": request_id,
        "scorer_source": SCORER_SOURCE,
        "ranked_results": ranked,
        "excluded_jobs": excluded,
        "latency_ms": latency_ms,
    }
