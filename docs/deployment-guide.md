# Phase 5 — Deployment Guide (Production Serving + Rollout)

## Overview

The API serves **`POST /v1/score`** with:

- **Registry-backed metadata:** `model_id`, `model_version`, `scorer_source` (from `registry/registry.json` + production model card).
- **Optional remote forward:** forward the same JSON to another scorer URL (for side-by-side or migration).
- **Rollout modes:** `production`, `shadow`, `canary`, `percentage` (see below).
- **Fallback:** on remote failure, optional empty result with `scorer_source=fallback_unavailable` (see `docs/integration-guide.md`).

## Container

```bash
docker compose up --build
```

Default listen: `0.0.0.0:8000`.

### Health checks

| Endpoint | Use |
| --- | --- |
| `GET /health` | Liveness (process up). |
| `GET /ready` | Readiness: includes model registry metadata + rollout config. |

Orchestrators should use **`/ready`** for readiness probes after the container starts.

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `SERVING_BACKEND` | `local` | `local` = in-process TF-IDF. `remote` = forward **all** traffic when `ROLLOUT_MODE=production` and `REMOTE_SCORER_URL` set. |
| `REMOTE_SCORER_URL` | (empty) | Base URL of remote scorer (e.g. `http://scorer:8000`). Forward path: `{base}/v1/score`. |
| `REMOTE_SCORER_TIMEOUT_SECONDS` | `5` | HTTP timeout for remote calls. |
| `CANDIDATE_REMOTE_SCORER_URL` | (empty) | Optional candidate URL for canary slice (falls back to `REMOTE_SCORER_URL`). |
| `REGISTRY_PATH` | `registry/registry.json` | Path to registry index (relative to process cwd). |
| `ROLLOUT_MODE` | `production` | `production` \| `shadow` \| `canary` \| `percentage` |
| `CANARY_PERCENT` | `0` | For `canary` / `percentage`: 0–100, deterministic slice by `request_id` hash. |
| `FALLBACK_ON_ERROR` | `true` | If remote fails: return fallback payload instead of 5xx. |
| `LOG_LEVEL` | `INFO` | Python log level. |

### Rollout modes (practical)

- **`production`:** Local TF-IDF unless `SERVING_BACKEND=remote` and `REMOTE_SCORER_URL` is set — then **always** forward to remote.
- **`shadow`:** Never forward; always local scoring. Use for “observe baseline only” while logging; add external metrics/dashboards in Phase 6.
- **`canary` / `percentage`:** For each request, with probability `CANARY_PERCENT/100` (deterministic from `request_id`), forward to `CANDIDATE_REMOTE_SCORER_URL` or `REMOTE_SCORER_URL`; otherwise local.

## Observability (Phase 5)

Structured log line **`score_completed`** includes:

- `request_id`, `scorer_source`, `latency_ms`, `serving_backend`, `rollout_mode`, `model_version` (via `logging` `extra`).

Emit **`X-Request-ID`** on responses (middleware).

## Manual canary (operations)

1. Deploy candidate service with a separate URL or tag.
2. Set `ROLLOUT_MODE=canary`, `CANARY_PERCENT=5`, `REMOTE_SCORER_URL=http://baseline:8000`, `CANDIDATE_REMOTE_SCORER_URL=http://candidate:8000` (example).
3. Monitor logs and error rates; increase `CANARY_PERCENT` gradually or switch to `SERVING_BACKEND=remote` for full cutover.

## Files

- `src/config/serving.py` — env parsing and effective remote URL.
- `src/runtime/score_service.py` — orchestration + fallback.
- `src/runtime/registry_meta.py` — production model metadata.
