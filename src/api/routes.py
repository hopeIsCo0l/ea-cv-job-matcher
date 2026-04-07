import logging
import time
import uuid

from fastapi import APIRouter, HTTPException, Request

from src.config.settings import MAX_JOBS_PER_REQUEST, RELEASE_TAG, SCORER_SOURCE
from src.config.serving import load_serving_config
from src.data.schemas import ScoreRequest, ScoreResponse
from src.runtime.registry_meta import load_production_model_meta
from src.runtime.score_service import execute_score, log_score_completion
from src.scoring.text_utils import normalize_text

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict:
    cfg = load_serving_config()
    meta = load_production_model_meta(cfg.registry_path)
    return {
        "status": "ready",
        "scorer_source": meta.get("scorer_source", SCORER_SOURCE),
        "release_tag": RELEASE_TAG,
        "model_id": meta.get("model_id"),
        "model_version": meta.get("model_version"),
        "rollout_mode": cfg.rollout_mode,
        "serving_backend": cfg.serving_backend,
        "registry_path": cfg.registry_path,
    }


@router.post("/v1/score", response_model=ScoreResponse)
def score(request: Request, payload: ScoreRequest) -> dict:
    started = time.perf_counter()
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if not normalize_text(payload.cv_text):
        raise HTTPException(status_code=400, detail="CV text cannot be empty after normalization")
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="At least one job is required")

    try:
        result = execute_score(request_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log_score_completion(request_id, result)
    latency_ms = result.get("latency_ms")
    logger.debug(
        "score_latency_total_ms=%s request_id=%s",
        round((time.perf_counter() - started) * 1000, 3),
        request_id,
    )
    return result
