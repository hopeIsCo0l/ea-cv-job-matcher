# SLA / SLO (Phase 5 Baseline)

This document defines **starter** service objectives. Tune per environment (staging vs production).

## Service scope

- **API:** `POST /v1/score`, `GET /health`, `GET /ready`
- **Deployment:** Single-region container (see `Dockerfile` / `docker-compose.yml`)

## SLOs (targets)

| Metric | Target (initial) | Measurement |
| --- | --- | --- |
| **Availability** | 99.5% monthly | Ratio of successful `GET /ready` or `POST /v1/score` (2xx) to total probes, excluding client 4xx. |
| **Latency p95** | < 3s | Server-side time for `POST /v1/score` (local path); include remote timeout in `REMOTE_SCORER_TIMEOUT_SECONDS`. |
| **Error budget** | 0.5% monthly | 5xx + timeout failures on score path. |

## SLAs (customer-facing — set with stakeholders)

- **Support response** for production incidents: *TBD by org* (e.g. P1 1h, P2 4h).
- **Maintenance window:** *TBD*.

## Indicators (logging — Phase 5)

- Log field **`latency_ms`** per request (score path).
- **`serving_backend`**: `local` \| `remote` \| `fallback`.
- **`scorer_source`** and **`model_version`** for audit.

Phase 6 may add dashboards (aggregate p50/p95, error rate by `scorer_source`).

## Fallback behavior

When `FALLBACK_ON_ERROR=true` and remote scorer fails, the API returns **`scorer_source=fallback_unavailable`** with empty rankings — counts as **degraded success** (2xx), not 5xx. Track **`serving_backend=fallback`** rate separately from hard errors.

## Review cadence

- Revisit SLOs after 30 days of metrics or after major model promotion.
