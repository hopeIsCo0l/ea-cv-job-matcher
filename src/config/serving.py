"""
Phase 5 — runtime serving configuration (env-driven).

See docs/deployment-guide.md for variable reference.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass


def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default).strip()


def _env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _env_bool(key: str, default: bool) -> bool:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _optional_url(key: str) -> str | None:
    v = os.environ.get(key)
    if v is None:
        return None
    s = v.strip()
    return s if s else None


@dataclass(frozen=True)
class ServingConfig:
    """Runtime serving / rollout configuration."""

    serving_backend: str
    remote_scorer_url: str | None
    remote_timeout_seconds: float
    registry_path: str
    rollout_mode: str
    canary_percent: int
    fallback_on_error: bool
    candidate_remote_url: str | None
    log_level: str


def load_serving_config() -> ServingConfig:
    return ServingConfig(
        serving_backend=_env_str("SERVING_BACKEND", "local").lower(),
        remote_scorer_url=_optional_url("REMOTE_SCORER_URL"),
        remote_timeout_seconds=_env_float("REMOTE_SCORER_TIMEOUT_SECONDS", 5.0),
        registry_path=_env_str("REGISTRY_PATH", "registry/registry.json"),
        rollout_mode=_env_str("ROLLOUT_MODE", "production").lower(),
        canary_percent=max(0, min(100, _env_int("CANARY_PERCENT", 0))),
        fallback_on_error=_env_bool("FALLBACK_ON_ERROR", True),
        candidate_remote_url=_optional_url("CANDIDATE_REMOTE_SCORER_URL"),
        log_level=_env_str("LOG_LEVEL", "INFO").upper(),
    )


def effective_remote_url(cfg: ServingConfig, request_id: str) -> str | None:
    """
    Return remote base URL to forward /v1/score to, or None for local scorer.

    - production + SERVING_BACKEND=remote: always REMOTE_SCORER_URL
    - canary|percentage: CANARY_PERCENT of traffic uses CANDIDATE_REMOTE_SCORER_URL or REMOTE_SCORER_URL
      (local otherwise; does not require SERVING_BACKEND=remote)
    - shadow: never forward (observe local-only; use logs/metrics for shadow experiments)
    """
    mode = cfg.rollout_mode

    if mode == "shadow":
        return None

    if mode == "production":
        if cfg.serving_backend != "remote":
            return None
        return cfg.remote_scorer_url

    if mode in ("canary", "percentage"):
        if cfg.canary_percent <= 0:
            return None
        if not _in_canary_slice(request_id, cfg.canary_percent):
            return None
        return cfg.candidate_remote_url or cfg.remote_scorer_url

    return None


def _in_canary_slice(request_id: str, percent: int) -> bool:
    h = hashlib.sha256(request_id.encode("utf-8")).hexdigest()
    bucket = int(h[:8], 16) % 100
    return bucket < percent
