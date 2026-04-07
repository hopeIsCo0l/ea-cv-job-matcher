# Runbook

## Local Development
1. Create virtual environment.
2. Install dependencies with `pip install -e .[dev]`.
3. Start server: `uvicorn src.api.main:app --reload`.
4. Run tests: `pytest`.

## Docker
- Build and run: `docker compose up --build`
- Stop: `docker compose down`
- Production-style config, rollout env vars, health checks: `docs/deployment-guide.md`
- Rollback: `docs/rollback-runbook.md`
- SLO starter: `docs/sla-slo.md`

## Evaluation Workflow
1. Generate synthetic dataset: `python scripts/generate_synthetic_data.py`
2. Run deterministic evaluation: `python scripts/run_evaluation.py`
3. Review outputs in `artifacts/`.

## Troubleshooting
- If `/ready` fails, verify dependencies installed and API startup logs.
- If scores are all low, inspect text normalization and job descriptions.
- If inputs fail validation, confirm request payload matches API contract.
