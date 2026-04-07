# Phase 4 — Registry + Promotion Gate

## Registry states

| State | Meaning |
| --- | --- |
| **candidate** | Trained or proposed; not deployed to users. |
| **staging** | Shadow / canary / internal only; full metrics required. |
| **production** | Default scorer for live or integrated traffic. |

Transitions are **not** automated in this repo: update `registry/registry.json` and the model card JSON after review.

## Promotion workflow (required)

New models should move in order:

1. **candidate** — Model artifact + model card created; eval metrics recorded.
2. **staging** — Shadow/canary/internal traffic only; add **`history`** entry `promote_to_staging` (who, when, why, ticket).
3. **production** — Default scorer; add **`history`** entry `promote_to_production`; demote or archive prior production per policy.

Each step requires **approval metadata** on the model card and in `registry.json` so the audit trail stays complete.

## Baseline axes (do not mix)

Promotion rules reference **one** baseline context at a time (`config/promotion_criteria.json` **version 2**):

| Axis | Use for | Baseline source |
| --- | --- | --- |
| **phase2_full_dataset** | Full-dataset TF-IDF metrics (Phase 2 style) | `artifacts/phase2_baseline_reference.json` |
| **phase3_same_split** | Learner vs TF-IDF on the same held-out CVs | `artifacts/phase3_comparison.json` → **`tfidf_cosine_baseline`** |

Comparing a candidate to Phase 2 numbers while using Phase 3 split metrics (or vice versa) is an error — declare the axis on the model card.

## Files

| Path | Purpose |
| --- | --- |
| `config/promotion_criteria.json` | Versioned ranking + fairness + quality gates (machine-readable). |
| `registry/registry.json` | Index of models, current `state`, paths to model cards, **approval history**. |
| `registry/model_cards/<id>.json` | **Machine-readable model card** (metrics, fairness block, approvals). |
| `registry/model_card.schema.json` | JSON Schema for model cards (generated from Pydantic). |
| `docs/phase4-promotion-checklist.md` | Human checklist before promotion. |

## Validation

```bash
python scripts/validate_registry.py
python scripts/generate_model_card_schema.py   # after changing ModelCard schema
```

## Fairness: under-sampled buckets

Default behavior is **`fail`** (block promotion) if any bucket has fewer than **`min_eval_samples_per_bucket`** eval CVs. Alternatives **`warn_only`** and **`not_applicable_exempt`** are defined in `promotion_criteria.json` and must be explicit on the model card + approvals.

## Promotion criteria summary

- **Ranking:** Gates are keyed by **baseline axis** — see `ranking_gates.when_using_axis_*` in config.
- **Fairness:** Maximum spread across CV buckets + minimum samples per bucket; under-sample behavior is explicit.
- **Approvals:** Every transition records **who**, **when**, **why** (and ideally **ticket**).

## Integration

Downstream services should read **`scorer_source`** and **`model_id`** from the active production model card; keep API version (`/v1/score`) separate from registry version.
