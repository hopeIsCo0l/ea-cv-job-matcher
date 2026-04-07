# Phase 6 — Integration, Monitoring, Retraining Loop

## Wire the main app to this service

| Concern | Guidance |
| --- | --- |
| **Base URL** | Configure the recruitment backend with the deployed scorer URL (or internal service name). |
| **Client** | Use **`POST /v1/score`** with the same JSON body as documented in `docs/api-contract.md`. |
| **Timeouts** | Match or exceed `REMOTE_SCORER_TIMEOUT_SECONDS` (default 5s); client timeout should be slightly higher. |
| **Tracing** | Forward **`X-Request-ID`** from the client or generate at the edge; response includes the same id in JSON and header. |
| **Env (if app embeds a proxy)** | Set **`REMOTE_SCORER_URL`** on a sidecar or worker that calls this API — never commit secrets (see `docs/integration-guide.md`). |

## Monitoring + retraining (deliverables)

| Deliverable | Location |
| --- | --- |
| **Dashboard spec** | `docs/phase6-monitoring-dashboard-spec.md` |
| **Retraining workflow** | `docs/phase6-retraining-workflow.md` |
| **Audit package** | `docs/phase6-audit-package.md` + `scripts/export_audit_package.py` |
| **Policy thresholds (machine-readable)** | `config/monitoring_thresholds.json` |

## Scripts

| Script | Purpose |
| --- | --- |
| `scripts/run_periodic_eval.py` | Regenerate Phase 2/3 eval, validate registry, write `artifacts/periodic_eval_<timestamp>/` |
| `scripts/export_audit_package.py` | Bundle registry, config, eval snapshots for audit / thesis |

## Light monitoring (first iteration)

Track from logs or metrics (see dashboard spec):

| Signal | Why |
| --- | --- |
| **Error rate** on HTTP calls to this service (5xx / timeouts) | Catch outages. |
| **p95 latency** on `POST /v1/score` | SLO in `docs/sla-slo.md`. |
| **`serving_backend=fallback` rate** | When `scorer_source=fallback_unavailable` — capacity or upstream issues. |
| **`score_completed` logs** | Filter by `scorer_source`, `rollout_mode`, `model_version`. |

## Periodic regression

On each **release tag** (or monthly):

1. `python scripts/run_periodic_eval.py` — full eval + manifest.
2. `python scripts/export_audit_package.py` — audit bundle.
3. `pytest` in CI.

## Optional later

- Import `docs/phase6-monitoring-dashboard-spec.md` panels into Grafana / CloudWatch.
- Synthetic probe hitting `/ready` and a minimal `/v1/score` from outside the cluster.
