# Phase 6 — Monitoring Dashboard Specification

This spec targets any log/metrics stack (Grafana Loki, CloudWatch Logs Insights, Datadog, ELK). **Data source:** structured application logs and HTTP access logs from the scorer service and its gateway.

## Log fields to parse (minimum)

From **`score_completed`** (Phase 5):

| Field | Type | Use |
| --- | --- | --- |
| `request_id` | string | Trace single request |
| `scorer_source` | string | Model lineage |
| `latency_ms` | number | Latency SLO |
| `serving_backend` | string | `local` / `remote` / `fallback` |
| `rollout_mode` | string | Rollout state |
| `model_version` | string | Registry tie-in |
| `fallback_reason` | string (optional) | Degraded path diagnosis |

From **access logs** (nginx/envoy): status code, path, duration, upstream errors.

## Panels (recommended)

### Row: Availability
- **Request rate** — `count` of `POST /v1/score` per minute.
- **Error rate** — fraction of **5xx** / total requests (warn/critical vs `config/monitoring_thresholds.json`).
- **Readiness** — synthetic or probe success rate for `GET /ready`.

### Row: Latency
- **p50 / p95 / p99** of `latency_ms` from `score_completed` (rolling window per `window_minutes` in config).
- **Compare** remote vs local if both appear in logs (filter by `serving_backend`).

### Row: Degradation
- **Fallback rate** — fraction of responses where `scorer_source=fallback_unavailable` OR `serving_backend=fallback`.
- **Top fallback_reason** — table of top 10 strings (last 24h).

### Row: Model / rollout
- **Traffic by `model_version`** — stacked bar.
- **Traffic by `rollout_mode`** — single stat or pie.

### Row: Drift / quality (proxy until live labels)
- **Scheduled eval Top-1** — manual entry or CI badge from `artifacts/phase3_comparison.json` (updated by `scripts/run_periodic_eval.py`).
- **Registry version** — text panel from last audit export manifest.

## Alerts (wire to thresholds)

| Alert | Condition | Severity |
| --- | --- | --- |
| LatencyP95High | p95 > `latency_ms.p95_warn` | warning |
| LatencyP95Critical | p95 > `latency_ms.p95_critical` | critical |
| ErrorRateHigh | 5xx fraction > `error_rate.http_5xx_fraction_warn` | warning |
| FallbackSpike | fallback fraction > `fallback_rate.fraction_critical` | critical |

Use `config/monitoring_thresholds.json` as the single source of numbers; copy into alert rules or sync via CI.

## Dashboards as code

- Prefer **JSON export** of Grafana dashboard checked into `docs/dashboards/` (optional future).
- Document panel queries in this repo so thesis / ops can reproduce without vendor lock-in.
