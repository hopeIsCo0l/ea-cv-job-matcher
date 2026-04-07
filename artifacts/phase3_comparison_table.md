# Phase 3 Model Comparison (same train/test split, shared TF-IDF features)

| Model | Top-1 | Top-3 | MRR | Latency ms (median) | Artifact bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| tfidf_cosine_baseline | 0.625 | 0.825 | 0.7446 | 2.0784 | 0 |
| logistic_regression | 0.05 | 0.55 | 0.3403 | 0.538 | 57222 |
| linear_svm_sgd_modified_huber | 0.45 | 0.8 | 0.6383 | 0.5436 | 57482 |
| hist_gradient_boosting | 0.275 | 0.7 | 0.5015 | 5.117 | 1138782 |

- **Best candidate:** `linear_svm_sgd_modified_huber`
- **Beats same-split baseline (+0.05 Top-1, Top-3 not worse, MRR higher):** `False`
- **Recommendation:** `defer_to_tfidf`

If no candidate clearly beats the baseline, keep TF-IDF as production scorer. See `docs/phase3-promotion-criteria.md` for business gates vs frozen Phase 2 numbers.