# Phase 4 — Promotion Checklist (Human Gate)

Use this before moving a model **`candidate` → `staging` → `production`**.  
Machine-readable criteria: `config/promotion_criteria.json` (**version 2** — baseline axes are explicit).  
Registry file: `registry/registry.json`.  
Model card template: `registry/model_cards/*.json` (schema: `registry/model_card.schema.json`).

---

## 0. Baseline axis (pick exactly one per promotion)

**Do not mix** Phase 2 full-dataset numbers with Phase 3 same-split numbers in one decision.

| Axis ID | When to use | Baseline numbers live in |
| --- | --- | --- |
| **`phase2_full_dataset`** | End-to-end parity with Phase 2 eval (all CVs, no split). | `artifacts/phase2_baseline_reference.json` |
| **`phase3_same_split`** | Comparing learners to TF-IDF on the **same** test CVs. | `artifacts/phase3_comparison.json` → row **`tfidf_cosine_baseline`** |

- [ ] Stated on model card: **`evaluation.eval_source`** and which axis applies.
- [ ] Candidate metrics compared using **`ranking_gates.when_using_axis_*`** matching that axis only (`config/promotion_criteria.json`).

---

## 1. Preconditions

- [ ] Dataset version is pinned (e.g. `v1`) and quality report exists (`artifacts/data_quality_report.md` passes).
- [ ] Eval artifacts reproduced (Phase 2/3 scripts) with same `dataset_sha256` as referenced on the model card.
- [ ] `python scripts/validate_registry.py` passes.

---

## 2. Ranking metrics (vs baseline for chosen axis only)

- [ ] **Top-1:** improvement ≥ **+0.05** vs baseline for that axis **or** policy exception documented.
- [ ] **Top-3:** not below baseline for that axis.
- [ ] **MRR:** strictly above baseline for that axis (per `promotion_criteria.json`).

---

## 3. Fairness thresholds (bucket spread)

- [ ] Per **CV match bucket** (`high` / `medium` / `low`) Top-1 (or agreed metric) is computed on the eval set.
- [ ] **Spread** = max(bucket metric) − min(bucket metric) ≤ **`cv_bucket_top1_max_spread`** (default **0.2**).
- [ ] **Under-sampled buckets** (fewer than **`min_eval_samples_per_bucket`** CVs, default **15**): choose one behavior and record it on the model card (`fairness.insufficient_bucket_behavior`) and in approvals:

| Behavior | Meaning |
| --- | --- |
| **`fail`** (default) | Block promotion until buckets meet minimum or eval is augmented. |
| **`warn_only`** | May proceed to staging with gaps documented; **not** for production without explicit sign-off. |
| **`not_applicable_exempt`** | Gate skipped for this run; requires **ticket** + **reason** + approver. |

- [ ] If any bucket is under-sampled, **ticket / reason** is recorded when not using **`fail`**.

---

## 4. Engineering & safety

- [ ] Latency within deployment budget (record on card or runbook).
- [ ] Artifact path / URI documented (`artifact_uri`).
- [ ] Risks, limitations, and intended use filled on model card.
- [ ] API contract tests pass (`pytest`).

---

## 5. Workflow: candidate → staging → production

1. **Candidate:** new model trained; model card `registry_state: candidate`; no traffic.
2. **Staging:** shadow / canary / internal only; full metrics + fairness on agreed axis; **`history`** entry: `promote_to_staging` (actor, time, reason, ticket).
3. **Production:** default scorer; **`history`** entry: `promote_to_production`; previous production model demoted or archived per policy.

- [ ] Each transition has a matching **`approvals`** line on the model card and **`history`** line in `registry.json`.

---

## 6. Approval metadata (required for promotion)

For each state transition, append to **`history`** in `registry/registry.json` and to **`approvals`** on the model card:

| Field | Required |
| --- | --- |
| **action** | e.g. `promote_to_staging`, `promote_to_production` |
| **actor** | Who (email, service account, or role) |
| **timestamp** | ISO-8601 UTC |
| **reason** | Short justification |
| **ticket** | Link/ticket ID (recommended) |

- [ ] **Who** promoted: recorded  
- [ ] **When**: recorded  
- [ ] **Why**: recorded  
- [ ] **Ticket / PR**: linked (if applicable)

---

## 7. Final sign-off

- [ ] Model card JSON validates (CI or `python scripts/validate_registry.py`).
- [ ] `registry_state` in model card matches `state` in `registry.json`.
- [ ] Version tag / release tag updated if applicable.

**Do not promote** if fairness spread is unknown or buckets are under-sampled unless risk is explicitly accepted in writing (`reason` + `ticket`), per chosen **`insufficient_bucket_behavior`**.
