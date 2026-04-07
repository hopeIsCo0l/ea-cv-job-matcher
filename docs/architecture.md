# Architecture Summary

## Components
- `src/api`: FastAPI HTTP surface (`/v1/score`, `/health`, `/ready`) and error model.
- `src/scoring`: Domain filtering, text normalization, TF-IDF scoring, cosine ranking, score labels, explainability.
- `src/data`: Request/response schemas.
- `src/evaluation`: Synthetic dataset definitions, quality gates, and evaluation metrics.
- `scripts`: Deterministic dataset/version builders and evaluation runners.

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
- Dataset generation is deterministic and fixed to `v1` composition (`70 high`, `70 medium`, `60 low`).

## Phase 2 Data Quality Flow
1. Build fixed 8-job Ethiopian Airlines scope.
2. Generate 200 synthetic CVs with controlled match buckets.
3. Expand to 1600 `(cv, job)` rows with `expected_label` and `expected_rank`.
4. Run quality gates and emit distribution + quality reports.
5. Run baseline evaluation and export eval-ready summary artifacts.

## Non-Goals in Phase 1 and 2
- No model training/fine-tuning.
- No external vector DB.
- No multilingual optimization beyond baseline normalization.
