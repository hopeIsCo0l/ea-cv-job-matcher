# Rollback Runbook (Phase 5)

## When to roll back

- Error rate or latency SLO breach on **`/v1/score`** after a config or model change.
- Remote scorer (`REMOTE_SCORER_URL`) consistently failing.
- Canary traffic showing worse ranking metrics than baseline.

## Fast rollback (configuration)

1. **Force local baseline (safest)**  
   - Set `SERVING_BACKEND=local`  
   - Unset or clear `REMOTE_SCORER_URL` and `CANDIDATE_REMOTE_SCORER_URL`  
   - Set `ROLLOUT_MODE=production`  
   - Restart the process / redeploy the same image with updated env.

2. **Disable canary**  
   - Set `CANARY_PERCENT=0` or `ROLLOUT_MODE=production`.

3. **Keep remote but stop traffic to bad URL**  
   - Point `REMOTE_SCORER_URL` to last known good scorer base URL, or switch to local as in (1).

## Registry rollback (model identity)

Production **`scorer_source`** / **`model_version`** come from **`registry/registry.json`** and the production model card.

1. Identify previous good commit or backup of `registry/registry.json` and `registry/model_cards/*.json`.
2. Restore files, commit, redeploy **or** hot-edit in controlled environment with review.
3. Run `python scripts/validate_registry.py`.

## Verification after rollback

- `GET /ready` shows expected `model_version`, `rollout_mode`, `serving_backend`.
- `POST /v1/score` sample returns non-empty `ranked_results` (unless input invalid).
- Logs show `serving_backend=local` or healthy remote.
- `pytest` in CI passes.

## Communication

- Record **who / when / why** in registry history when changing production model (Phase 4 checklist).
