# Phase 6 — Audit Package

An **audit package** is a reproducible bundle for thesis defense, compliance review, or release sign-off. Generate it with:

```bash
python scripts/export_audit_package.py
```

Output: `artifacts/audit_export_<UTC-timestamp>/` containing:

| Path | Purpose |
| --- | --- |
| `manifest.json` | Export version, timestamp, optional git SHA, list of included files |
| `registry/` | Copy of `registry/registry.json` and `registry/model_cards/*.json` |
| `config/` | `promotion_criteria.json`, `monitoring_thresholds.json` |
| `evaluation/` | Snapshots: `phase2_baseline_reference.json`, `phase3_comparison.json`, `phase3_comparison_table.md` (if present) |
| `data/` | Optional: `data/processed/dataset_v1.jsonl` if present (large; can exclude with `--no-dataset`) |
| `README_AUDIT.txt` | Short human-readable summary |

## What reviewers verify

- **Registry** production model matches deployed `model_version` / `scorer_source`.
- **Promotion criteria** version and **monitoring thresholds** version.
- **Evaluation** tables show baseline vs candidates on the agreed axis (`docs/phase3-promotion-criteria.md`).

## Periodic evaluation

Scheduled job (cron / CI monthly):

```bash
python scripts/run_periodic_eval.py
```

Writes `artifacts/periodic_eval_<timestamp>/` with manifest + copies of key eval outputs. Use alongside audit export before major releases.

## Retention

- Keep audit exports **outside** git if they contain large datasets; store in object storage or thesis appendix USB.
- Commit **manifest hashes** or checksums in release notes if needed.
