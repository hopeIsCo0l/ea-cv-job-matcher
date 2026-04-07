"""Contract parity: local vs remote merge vs fallback; fallback_reason semantics."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app
from src.data.schemas import JobInput, ScoreRequest
from src.runtime.score_service import _format_fallback_reason, _merge_remote_response, execute_score


class EmptyMsg(Exception):
    def __str__(self) -> str:
        return ""


def test_format_fallback_reason_non_empty_for_empty_exception_message():
    assert _format_fallback_reason(EmptyMsg()) == "EmptyMsg"


def test_merge_remote_minimal_payload_has_same_keys_as_local():
    from src.config.serving import load_serving_config

    cfg = load_serving_config()
    meta = {"model_id": "m1", "model_version": "v1"}
    remote = {"ranked_results": [{"rank": 1, "job_id": "a", "score": 0.5, "label": "medium", "top_terms": []}]}
    out = _merge_remote_response(
        remote,
        request_id="rid",
        meta=meta,
        cfg=cfg,
        latency_ms=12.0,
    )
    assert set(out.keys()) == {
        "request_id",
        "scorer_source",
        "ranked_results",
        "excluded_jobs",
        "latency_ms",
        "model_id",
        "model_version",
        "rollout_mode",
        "serving_backend",
        "fallback_reason",
    }
    assert out["excluded_jobs"] == []
    assert out["serving_backend"] == "remote"
    assert out["fallback_reason"] is None


def test_fallback_envelope_has_reason_and_same_keys(monkeypatch):
    monkeypatch.setenv("SERVING_BACKEND", "remote")
    monkeypatch.setenv("ROLLOUT_MODE", "production")
    monkeypatch.setenv("REMOTE_SCORER_URL", "http://unreachable.invalid")
    monkeypatch.setenv("FALLBACK_ON_ERROR", "true")

    payload = ScoreRequest(
        cv_text="airport ramp baggage coordination",
        jobs=[
            JobInput(
                job_id="et-ground-001",
                title="Trainee Ground Operations Officer",
                description="Ramp coordination",
                company_name="Ethiopian Airlines",
            )
        ],
    )
    with patch("src.runtime.score_service.forward_score", side_effect=ConnectionError("refused")):
        out = execute_score("test-req-fallback", payload)

    assert out["scorer_source"] == "fallback_unavailable"
    assert out["serving_backend"] == "fallback"
    assert out["fallback_reason"] == "refused"
    assert out["ranked_results"] == []
    assert set(out.keys()) == {
        "request_id",
        "scorer_source",
        "ranked_results",
        "excluded_jobs",
        "latency_ms",
        "model_id",
        "model_version",
        "rollout_mode",
        "serving_backend",
        "fallback_reason",
    }


def test_http_local_vs_remote_shape_keys_match(monkeypatch):
    """Same top-level keys when SERVING_BACKEND=local and when remote returns full JSON."""
    jobs = [
        {
            "job_id": "et-ground-001",
            "title": "Trainee Ground Operations Officer",
            "description": "Ramp coordination",
            "company_name": "Ethiopian Airlines",
        }
    ]
    body = {"cv_text": "airport operations", "jobs": jobs}

    client = TestClient(app)
    local = client.post("/v1/score", json=body).json()
    local_keys = set(local.keys())

    remote_payload = {
        "request_id": "remote",
        "scorer_source": "baseline_tfidf_cosine_v1",
        "ranked_results": local["ranked_results"],
        "excluded_jobs": local["excluded_jobs"],
        "latency_ms": 1.0,
        "model_id": local.get("model_id"),
        "model_version": local.get("model_version"),
        "rollout_mode": "production",
        "serving_backend": "remote",
        "fallback_reason": None,
    }
    with patch("src.runtime.score_service.forward_score", return_value=remote_payload):
        monkeypatch.setenv("SERVING_BACKEND", "remote")
        monkeypatch.setenv("ROLLOUT_MODE", "production")
        monkeypatch.setenv("REMOTE_SCORER_URL", "http://mock.example")
        remote = client.post("/v1/score", json=body).json()

    assert set(remote.keys()) == local_keys
    assert remote["serving_backend"] == "remote"
