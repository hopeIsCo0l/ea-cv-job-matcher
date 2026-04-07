# Ethiopian Airlines CV-to-Job Similarity

Production-ready baseline AI service for matching one CV to Ethiopian Airlines jobs using **TF-IDF + cosine similarity**.

Release tag: `v1.0.0-phase1-baseline`

## What this delivers
- FastAPI service with `POST /v1/score`
- Ethiopian Airlines-only domain filtering
- Hard cap of 8 jobs per scoring run
- Deterministic ranking with lightweight explainability (`top_terms`)
- Synthetic evaluation pipeline with artifacts
- Dockerized local run

## Quickstart

### 1) Install
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

### 2) Run API
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 3) Run tests
```bash
pytest
```

### 4) Run Phase 1 evaluation
```bash
python scripts/generate_synthetic_data.py
python scripts/run_evaluation.py
```

### 5) Run Phase 2 data and quality pipeline
```bash
python scripts/run_phase2_pipeline.py
```

### 6) Phase 3 — train candidates vs same TF-IDF features (comparison table)
```bash
python scripts/run_phase3_comparison.py
```
See `docs/phase3-training-plan.md`. Outputs: `artifacts/phase3_comparison_table.md`, `artifacts/phase3_comparison.json`, `artifacts/phase3_models/`.

## One-command local run (Docker)
```bash
docker compose up --build
```

## Sample request
```bash
curl -X POST "http://localhost:8000/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Customer-focused graduate with airport operations internship and flight handling exposure.",
    "jobs": [
      {
        "job_id": "et-ground-001",
        "title": "Trainee Ground Operations Officer",
        "description": "Coordinate ramp operations, baggage handling, and turn-around tasks.",
        "company_name": "Ethiopian Airlines"
      },
      {
        "job_id": "et-cabin-001",
        "title": "Trainee Cabin Crew",
        "description": "Deliver in-flight passenger service and ensure onboard safety.",
        "company_name": "Ethiopian Airlines"
      }
    ]
  }'
```

## Outputs
- `artifacts/synthetic_dataset.json`
- `artifacts/eval_results.json`
- `artifacts/eval_summary.md`
- `artifacts/eval_per_sample.csv`
- `data/processed/dataset_v1.jsonl`
- `artifacts/data_quality_report.md`
- `artifacts/data_distribution.json`
- `artifacts/eval_ready_summary.md`
- `artifacts/phase2_baseline_reference.json`
- `artifacts/phase3_comparison.json` / `artifacts/phase3_comparison_table.md` (after Phase 3 script)

## Phase 3 promotion criteria
- Locked criteria are documented in `docs/phase3-promotion-criteria.md`.
- Baseline freeze reference lives in `artifacts/phase2_baseline_reference.json`.

### Phase 4 — registry + promotion gate
- **States:** `candidate` → `staging` → `production` (see `docs/phase4-registry.md`).
- **Promotion criteria (machine-readable):** `config/promotion_criteria.json` (**v2** — separate **Phase 2 full-dataset** vs **Phase 3 same-split** baseline axes; do not mix).
- **Human checklist:** `docs/phase4-promotion-checklist.md`.
- **Registry index:** `registry/registry.json` (includes approval **who / when / why** per transition).
- **Model cards:** `registry/model_cards/*.json` — schema: `registry/model_card.schema.json`.
- **Validate:** `python scripts/validate_registry.py`

### Phase 5 — production serving + rollout
- **Registry at runtime:** `GET /ready` and `POST /v1/score` expose `model_id`, `model_version`, `scorer_source` from `registry/`, plus `rollout_mode` and `serving_backend`.
- **Env:** `SERVING_BACKEND`, `REMOTE_SCORER_URL`, `ROLLOUT_MODE` (`production` \| `shadow` \| `canary` \| `percentage`), `CANARY_PERCENT`, `FALLBACK_ON_ERROR`, `LOG_LEVEL` — see `docs/deployment-guide.md`.
- **Observability:** logs `request_id`, `scorer_source`, `latency_ms`, rollout fields (Phase 6 can add dashboards).
- **Docs:** `docs/deployment-guide.md`, `docs/rollback-runbook.md`, `docs/sla-slo.md`.

### Phase 6 (integration + monitoring)
- See `docs/phase6-roadmap.md` and **Phase 6** in `docs/integration-guide.md` (recruitment app, `request_id`, regression checks).

## Phase 3 roadmap (not implemented)
- Collect real labeled hiring outcomes and human ranking judgments
- Train and compare transformer/reranker models
- Introduce multilingual handling (Amharic/English blending)
- Add calibration and fairness monitoring

## Threshold policy (Phase 1)
- Kept as specified baseline mapping:
  - `good` if score >= `0.40`
  - `medium` if `0.20 <= score < 0.40`
  - `bad` if score < `0.20`
- Tuning is intentionally deferred to Phase 2 after real-label calibration data is collected.
