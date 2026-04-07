"""
Orchestrate scoring: local TF-IDF vs optional remote forward, rollout, fallback.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.config.serving import ServingConfig, effective_remote_url, load_serving_config
from src.config.settings import MAX_JOBS_PER_REQUEST, SCORER_SOURCE
from src.data.schemas import ScoreRequest
from src.runtime.registry_meta import load_production_model_meta
from src.runtime.remote_scorer import forward_score
from src.scoring.domain import filter_and_cap_jobs
from src.scoring.engine import TfidfScorer
from src.scoring.text_utils import normalize_text

logger = logging.getLogger(__name__)

_scorer = TfidfScorer()


def _format_fallback_reason(exc: Exception) -> str:
    """Non-empty string for clients and logs when scorer_source is fallback_unavailable."""
    s = str(exc).strip()
    return s if s else type(exc).__name__


def _score_envelope(
    *,
    request_id: str,
    scorer_source: str,
    ranked_results: list[dict[str, Any]],
    excluded_jobs: list[dict[str, Any]],
    latency_ms: float,
    meta: dict[str, Any],
    cfg: ServingConfig,
    serving_backend: str,
    fallback_reason: str | None,
) -> dict[str, Any]:
    """Single response shape for local, remote, and fallback (contract parity)."""
    return {
        "request_id": request_id,
        "scorer_source": scorer_source,
        "ranked_results": ranked_results,
        "excluded_jobs": excluded_jobs,
        "latency_ms": latency_ms,
        "model_id": meta.get("model_id"),
        "model_version": meta.get("model_version"),
        "rollout_mode": cfg.rollout_mode,
        "serving_backend": serving_backend,
        "fallback_reason": fallback_reason,
    }


def _local_score(
    payload: ScoreRequest,
    request_id: str,
    meta: dict[str, Any],
    cfg: ServingConfig,
    started: float,
) -> dict[str, Any]:
    if not normalize_text(payload.cv_text):
        raise ValueError("CV text cannot be empty after normalization")
    valid_jobs, excluded = filter_and_cap_jobs(payload.jobs)
    if not valid_jobs:
        raise ValueError("No valid Ethiopian Airlines jobs found")

    ranked = _scorer.score_jobs(payload.cv_text, valid_jobs)
    top_k = min(payload.top_k, MAX_JOBS_PER_REQUEST)
    ranked = ranked[:top_k]
    latency_ms = round((time.perf_counter() - started) * 1000, 3)

    return _score_envelope(
        request_id=request_id,
        scorer_source=meta.get("scorer_source", SCORER_SOURCE),
        ranked_results=ranked,
        excluded_jobs=excluded,
        latency_ms=latency_ms,
        meta=meta,
        cfg=cfg,
        serving_backend="local",
        fallback_reason=None,
    )


def _merge_remote_response(
    remote: dict[str, Any],
    *,
    request_id: str,
    meta: dict[str, Any],
    cfg: ServingConfig,
    latency_ms: float,
) -> dict[str, Any]:
    """Normalize remote JSON to the same envelope as local scoring."""
    rid = remote.get("request_id") or request_id
    ranked = remote.get("ranked_results")
    if not isinstance(ranked, list):
        ranked = []
    excluded = remote.get("excluded_jobs")
    if not isinstance(excluded, list):
        excluded = []
    lm = remote.get("latency_ms", latency_ms)
    try:
        lm_f = float(lm)
    except (TypeError, ValueError):
        lm_f = float(latency_ms)
    return _score_envelope(
        request_id=str(rid),
        scorer_source=str(remote.get("scorer_source", meta.get("scorer_source", SCORER_SOURCE))),
        ranked_results=ranked,
        excluded_jobs=excluded,
        latency_ms=lm_f,
        meta={
            "model_id": remote.get("model_id", meta.get("model_id")),
            "model_version": remote.get("model_version", meta.get("model_version")),
        },
        cfg=cfg,
        serving_backend="remote",
        fallback_reason=None,
    )


def execute_score(request_id: str, payload: ScoreRequest) -> dict[str, Any]:
    cfg = load_serving_config()
    meta = load_production_model_meta(cfg.registry_path)
    started = time.perf_counter()

    remote_url = effective_remote_url(cfg, request_id)
    body = {
        "cv_text": payload.cv_text,
        "jobs": [j.model_dump() for j in payload.jobs],
        "top_k": payload.top_k,
    }

    if remote_url:
        try:
            remote = forward_score(remote_url, body, cfg.remote_timeout_seconds)
            latency_ms = round((time.perf_counter() - started) * 1000, 3)
            return _merge_remote_response(
                remote,
                request_id=request_id,
                meta=meta,
                cfg=cfg,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            logger.warning(
                "remote_scorer_failed",
                extra={
                    "request_id": request_id,
                    "error": str(exc),
                    "remote_url": remote_url,
                },
            )
            if cfg.fallback_on_error:
                latency_ms = round((time.perf_counter() - started) * 1000, 3)
                reason = _format_fallback_reason(exc)
                return _score_envelope(
                    request_id=request_id,
                    scorer_source="fallback_unavailable",
                    ranked_results=[],
                    excluded_jobs=[],
                    latency_ms=latency_ms,
                    meta=meta,
                    cfg=cfg,
                    serving_backend="fallback",
                    fallback_reason=reason,
                )
            raise

    return _local_score(
        payload=payload,
        request_id=request_id,
        meta=meta,
        cfg=cfg,
        started=started,
    )


def log_score_completion(request_id: str, result: dict[str, Any]) -> None:
    extra: dict[str, Any] = {
        "request_id": request_id,
        "scorer_source": result.get("scorer_source"),
        "latency_ms": result.get("latency_ms"),
        "serving_backend": result.get("serving_backend"),
        "rollout_mode": result.get("rollout_mode"),
        "model_version": result.get("model_version"),
    }
    if result.get("fallback_reason"):
        extra["fallback_reason"] = result.get("fallback_reason")
    logger.info("score_completed", extra=extra)
