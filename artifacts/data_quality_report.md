# Data Quality Report

- Dataset version: `v1`
- Rows: 1600
- Unique CV IDs: 200
- Unique jobs: 8
- Quality gates passed: `True`

## Gate Results
- No empty CV/job text
- No duplicate CV IDs
- No duplicate (cv_id, job_id) pairs
- Ethiopian filter enforced
- Exactly 8 jobs in active evaluation set
- Label distribution (via CV buckets) not heavily imbalanced

## Errors
- None

## Distribution
- Expected label counts: {'good': 70, 'medium': 350, 'bad': 1180}
- CV bucket counts: {'high': 560, 'medium': 560, 'low': 480}