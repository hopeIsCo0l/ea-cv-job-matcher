# Phase 3 Training Plan (Practical)

## Goal

Train 2–3 candidate **pair classifiers** on the **same** `dataset_v1` and **same TF-IDF** settings as the baseline, then compare **ranking** metrics on a **held-out CV split** (no leakage: all 8 pairs for a CV stay in train or test).

## Models (current implementation)

| Candidate | Notes |
| --- | --- |
| `logistic_regression` | Multinomial LR on TF-IDF pair text |
| `linear_svm_sgd_modified_huber` | Linear `SGDClassifier` with `modified_huber` loss (multiclass probabilities; practical stand-in for a linear SVM pipeline) |
| `hist_gradient_boosting` | `HistGradientBoostingClassifier` on **dense** TF-IDF (sparse not supported) |

Pair text: `cv_text + " " + job_description` (same vectorizer hyperparameters as `src/config/settings.py`).

## Ranking score (for fair cross-job comparison)

For each pair, class probabilities are mapped to a single **ordinal** relevance:

`score = 2 * P(good) + 1 * P(medium) + 0 * P(bad)`

Jobs for a CV are ranked by this score (ties broken by `job_id`).

## Metrics

- **Top-1 / Top-3 / MRR** on test CVs (target job = `target_job_id` in the dataset).
- **Inference latency:** median time to score **8 jobs** for one CV (micro-benchmark, same machine).
- **Artifact size:** bytes of `artifacts/phase3_models/<name>.joblib` (vectorizer + classifier).

## Run

```bash
python scripts/run_phase2_pipeline.py   # if dataset_v1 not built yet
python scripts/run_phase3_comparison.py
```

Outputs:

- `artifacts/phase3_comparison.json`
- `artifacts/phase3_comparison_table.md`
- `artifacts/phase3_models/*.joblib`

## Decision rule

If no candidate **beats the same-split TF-IDF baseline** under `docs/phase3-promotion-criteria.md` (and your latency budget), **keep TF-IDF** as production scorer and defer promotion.

Note: **Frozen Phase 2** metrics in `artifacts/phase2_baseline_reference.json` are computed on the **full** dataset; Phase 3 compares models on a **stratified train/test split**, so numbers will differ from Phase 2 — use the baseline row inside `phase3_comparison.json` as the apples-to-apples reference for that run.
