# Eval Ready Summary

- Dataset version fixed: `v1`
- CV count: 200
- Pair count: 1600

## Ranking Checks
- Top-1 accuracy: 0.61
- Top-3 hit rate: 0.82
- MRR: 0.7329

## Label Confusion Summary
- {'good': {'bad': 61, 'medium': 9}, 'medium': {'bad': 350}, 'bad': {'bad': 1180}}

## Threshold Sanity (0.40 / 0.20)
- {'thresholds': {'good': 0.4, 'medium': 0.2}, 'predicted_counts': {'bad': 1591, 'medium': 9}}

## Error Analysis (Top-1 misses)
- Total Top-1 failures: 78
- Failures by bucket: {'medium': 27, 'low': 51}
- Medium vs Low confusion: {'expected_medium_predicted_bad': 350, 'expected_bad_predicted_medium': 0}
- Failure reason counts: {'threshold_effect_below_medium_cutoff': 78, 'missing_domain_terms': 51}