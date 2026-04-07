# Phase 6 — Integration & Monitoring (e.g. recruitment app / fypimp103)

## Wire the main app to this service

| Concern | Guidance |
| --- | --- |
| **Base URL** | Configure the recruitment backend with the deployed scorer URL (or internal service name). |
| **Client** | Use **`POST /v1/score`** with the same JSON body as documented in `docs/api-contract.md`. |
| **Timeouts** | Match or exceed `REMOTE_SCORER_TIMEOUT_SECONDS` (default 5s); client timeout should be slightly higher. |
| **Tracing** | Forward **`X-Request-ID`** from the client or generate at the edge; response includes the same id in JSON and header. |
| **Env (if app embeds a proxy)** | Set **`REMOTE_SCORER_URL`** on a sidecar or worker that calls this API — never commit secrets (see `docs/integration-guide.md`). |

## Light monitoring (first iteration)

Even before a full dashboard, track from logs or metrics:

| Signal | Why |
| --- | --- |
| **Error rate** on HTTP calls to this service (5xx / timeouts) | Catch outages. |
| **p95 latency** on `POST /v1/score` | SLO in `docs/sla-slo.md`. |
| **`serving_backend=fallback` rate** | When `scorer_source=fallback_unavailable` — capacity or upstream issues. |
| **`score_completed` logs** | Filter by `scorer_source`, `rollout_mode`, `model_version`. |

## Periodic regression (releases)

On each **release tag** (or monthly):

1. `python scripts/run_phase3_comparison.py` — same-split baseline vs candidates.
2. `python scripts/validate_registry.py` — registry and model cards valid.
3. Optional: `pytest` in CI.

Document results in release notes or a short `artifacts/` snapshot committed only if policy allows.

## Optional later

- Grafana / CloudWatch / similar dashboard from structured logs.
- Synthetic probe hitting `/ready` and a minimal `/v1/score` from outside the cluster.
