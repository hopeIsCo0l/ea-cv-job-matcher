# Phase 3 Promotion Criteria

These gates are locked before training/model comparison to avoid moving goalposts.

## Frozen Phase 2 Baseline
- Dataset version: `v1`
- Baseline reference artifact: `artifacts/phase2_baseline_reference.json`
- Current ranking baseline:
  - Top-1 accuracy: `0.61`
  - Top-3 hit rate: `0.82`
  - MRR: `0.7329`

## Promotion Gates for Candidate Models
- Top-1 accuracy must improve by at least `+0.05` over baseline (>= `0.66`).
- Top-3 hit rate must remain at least baseline (>= `0.82`).
- MRR must improve over baseline (> `0.7329`).
- Quality gates from Phase 2 must continue passing on the same dataset version.

## Evaluation Protocol
- Use identical job scope (same 8 Ethiopian Airlines trainee roles).
- Use dataset `v1` unless a new version is formally introduced.
- Report metrics and confusion in the same artifact format as Phase 2.

## Phase 3 model comparison (train/test split)
- Run `python scripts/run_phase3_comparison.py` after `dataset_v1` exists.
- **Apples-to-apples baseline** for promotion on that run is the `tfidf_cosine_baseline` row in `artifacts/phase3_comparison.json` (same stratified CV split as candidates).
- Frozen Phase 2 numbers in `phase2_baseline_reference.json` are **full-dataset** TF-IDF metrics; they are a historical snapshot, not the same split as Phase 3.
