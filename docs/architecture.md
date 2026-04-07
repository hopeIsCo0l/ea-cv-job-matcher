# Architecture Summary

## Components
- `src/api`: FastAPI HTTP surface (`/v1/score`, `/health`, `/ready`) and error model.
- `src/scoring`: Domain filtering, text normalization, TF-IDF scoring, cosine ranking, score labels, explainability.
- `src/data`: Request/response schemas.
- `src/evaluation`: Synthetic dataset definitions and evaluation metrics.
- `scripts`: Data generation and deterministic evaluation runners.

## Request Flow
1. API validates payload and assigns `request_id`.
2. Jobs are filtered to Ethiopian Airlines and capped to 8.
3. Shared corpus TF-IDF is built for `[cv] + jobs`.
4. Cosine similarity is computed CV vs each job.
5. Results are ranked and labeled (`good` / `medium` / `bad`).
6. Top terms are extracted from overlapping TF-IDF weights.

## Determinism Rules
- If more than 8 valid jobs exist, service keeps the first 8 after sorting by `(job_id.lower(), title.lower())`.
- Ranking ties are broken by `job_id` ascending.

## Non-Goals in Phase 1
- No model training/fine-tuning.
- No external vector DB.
- No multilingual optimization beyond baseline normalization.
