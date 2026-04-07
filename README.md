# Ethiopian Airlines CV-to-Job Similarity (Phase 1)

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

### 4) Run evaluation
```bash
python scripts/generate_synthetic_data.py
python scripts/run_evaluation.py
```

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

## Phase 2 roadmap (not implemented)
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
