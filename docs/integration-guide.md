# Integration Guide (External Backend)

## Endpoint
- Base URL: `http://<host>:8000`
- Score API: `POST /v1/score`

## Authentication and secrets

This service does **not** embed API keys. For production:

- Terminate TLS and authenticate at the **gateway** (API gateway, reverse proxy, or your recruitment app) using API keys, JWT, or mTLS.
- Pass **`X-Request-ID`** from the client or generate one at the edge; the API echoes it on responses.
- Store **`REMOTE_SCORER_URL`** and any gateway credentials in a **secret manager** or orchestrator secrets — **not** in `docker-compose.yml` in source control.

Student / dev setups may run open on `localhost`; document any shared demo URL separately.

## Recommended Client Behavior
- Timeout: 3-5 seconds.
- Retries: up to 2 retries with exponential backoff (e.g. 200ms, 500ms).
- Circuit breaker: open if repeated failures exceed threshold.

## Fallback Rule
If AI service is unavailable or times out, caller should return neutral response:
```json
{
  "request_id": "caller-generated-id",
  "scorer_source": "fallback_unavailable",
  "ranked_results": [],
  "excluded_jobs": [],
  "latency_ms": 0,
  "fallback_reason": "timeout_or_upstream_error"
}
```

When using **this** service with `FALLBACK_ON_ERROR=true`, the API sets **`fallback_reason`** to the actual error message (always non-empty).

## Versioning Strategy
- Path-versioned API (`/v1/score`, future `/v2/score`).
- `scorer_source` identifies model/scoring implementation lineage.
- **`model_version`** and **`model_id`** (Phase 5) tie responses to `registry/`; clients may log them for audit.
- Keep contract backward compatible within same `v1` path.

## Phase 5 (same service)
- Readiness: `GET /ready` returns `model_version`, `rollout_mode`, `serving_backend`, and registry path metadata.
- If this process forwards to another scorer (`REMOTE_SCORER_URL`), timeouts apply; on failure it may return **`scorer_source=fallback_unavailable`** when `FALLBACK_ON_ERROR=true` (see `docs/deployment-guide.md`).
- When **`fallback_unavailable`**, **`fallback_reason`** is always set to a non-empty string so callers can detect the degraded path.

## Phase 6 — recruitment app (e.g. fypimp103)

- Point the main app at this service: **`REMOTE_SCORER_URL`**, client timeouts, and propagate **`request_id`** end-to-end if used for tracing.
- Track **remote error rate**, **p95 latency**, and **fallback rate**; align alert thresholds with **`config/monitoring_thresholds.json`** and panel layout in **`docs/phase6-monitoring-dashboard-spec.md`**.
- **Periodic regression:** `python scripts/run_periodic_eval.py` (Phase 2 pipeline → registry validation → Phase 3 comparison; outputs under `artifacts/periodic_eval_<timestamp>/`). Alternatively run `run_phase3_comparison.py` and `validate_registry.py` individually (see `docs/phase6-roadmap.md`).
- **Audit export:** `python scripts/export_audit_package.py` (optional `--no-dataset`); see **`docs/phase6-audit-package.md`**.
- **Retraining / escalation:** **`docs/phase6-retraining-workflow.md`** (policy triggers, not auto-training in this repo).

## Example Request
```json
{
  "cv_text": "Aviation operations graduate with strong customer support exposure.",
  "jobs": [
    {
      "job_id": "et-cs-001",
      "title": "Trainee Customer Service Agent",
      "description": "Airport check-in and passenger issue resolution",
      "company_name": "Ethiopian Airlines"
    }
  ],
  "top_k": 8
}
```
