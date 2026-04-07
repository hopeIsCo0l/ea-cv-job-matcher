# Phase 2 - Data and Quality Foundation

## Objective
Build a reliable, reproducible dataset and validation pipeline so TF-IDF baseline behavior is trusted before model training.

## Fixed Scope
- Exactly 8 Ethiopian Airlines trainee jobs:
  - Trainee Pilot
  - Trainee Cabin Crew
  - Trainee Aircraft Mechanic
  - Trainee Avionics Technician
  - Trainee Power Plant Technician
  - Trainee Ground Operations Officer
  - Trainee Customer Service Agent
  - Trainee Finance / Accounting (College, Trainee)

## Dataset Design
- Version: `v1`
- CV count: `200`
  - High-match: `70`
  - Medium-match: `70`
  - Low/noise: `60`
- Pair count: `200 x 8 = 1600`

## Required Fields
Each row in `data/processed/dataset_v1.jsonl` includes:
- `cv_id`
- `cv_text`
- `job_id`
- `job_title`
- `job_description`
- `company_name`
- `expected_label` (`good|medium|bad`)
- `expected_rank`

## Quality Gates
1. No empty CV/job text
2. No duplicate CV IDs
3. No duplicate `(cv_id, job_id)` pairs
4. Ethiopian filter enforced (`company_name`)
5. Exactly 8 jobs in active evaluation set
6. CV bucket distribution not heavily imbalanced

## Phase 2 Artifacts
- `data/processed/dataset_v1.jsonl`
- `artifacts/data_quality_report.md`
- `artifacts/data_distribution.json`
- `artifacts/eval_ready_summary.md`

## Evaluation Checks
- Top-1 accuracy
- Top-3 hit rate
- MRR
- Label confusion summary (`good/medium/bad`)
- Threshold sanity table (`0.40` / `0.20`)
