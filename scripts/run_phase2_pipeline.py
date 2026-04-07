import json
import sys
from hashlib import sha256
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config.settings import (  # noqa: E402
    GOOD_THRESHOLD,
    MEDIUM_THRESHOLD,
    SCORER_SOURCE,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    TFIDF_STOP_WORDS,
    TFIDF_SUBLINEAR_TF,
)
from src.evaluation.dataset import (  # noqa: E402
    PHASE2_CV_BUCKET_TARGETS,
    PHASE2_DATASET_VERSION,
    build_phase2_cvs,
    build_phase2_jobs,
    build_phase2_pairs,
)
from src.evaluation.phase2_eval import evaluate_phase2_dataset  # noqa: E402
from src.evaluation.quality import run_quality_gates  # noqa: E402


def _dataset_hash(rows: list[dict]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    artifacts_dir = Path("artifacts")
    processed_dir = Path("data/processed")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    jobs = build_phase2_jobs()
    cvs = build_phase2_cvs()
    rows = build_phase2_pairs(cvs, jobs)

    dataset_path = processed_dir / f"dataset_{PHASE2_DATASET_VERSION}.jsonl"
    with dataset_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    quality = run_quality_gates(rows)
    distribution = {
        "dataset_version": PHASE2_DATASET_VERSION,
        "cv_bucket_targets": PHASE2_CV_BUCKET_TARGETS,
        "actual_cv_count": len(cvs),
        "actual_pair_count": len(rows),
        "jobs_in_scope": [job["job_id"] for job in jobs],
        "quality_stats": quality["stats"],
        "dataset_sha256": _dataset_hash(rows),
    }
    distribution_path = artifacts_dir / "data_distribution.json"
    distribution_path.write_text(json.dumps(distribution, indent=2), encoding="utf-8")

    quality_md = artifacts_dir / "data_quality_report.md"
    quality_md.write_text(
        "\n".join(
            [
                "# Data Quality Report",
                "",
                f"- Dataset version: `{PHASE2_DATASET_VERSION}`",
                f"- Rows: {quality['stats'].get('rows', 0)}",
                f"- Unique CV IDs: {quality['stats'].get('unique_cv_ids', 0)}",
                f"- Unique jobs: {quality['stats'].get('unique_jobs', 0)}",
                f"- Quality gates passed: `{quality['passed']}`",
                "",
                "## Gate Results",
                "- No empty CV/job text",
                "- No duplicate CV IDs",
                "- No duplicate (cv_id, job_id) pairs",
                "- Ethiopian filter enforced",
                "- Exactly 8 jobs in active evaluation set",
                "- Label distribution (via CV buckets) not heavily imbalanced",
                "",
                "## Errors",
                *(["- None"] if not quality["errors"] else [f"- {err}" for err in quality["errors"]]),
                "",
                "## Distribution",
                f"- Expected label counts: {quality['stats'].get('label_counts', {})}",
                f"- CV bucket counts: {quality['stats'].get('bucket_counts', {})}",
            ]
        ),
        encoding="utf-8",
    )

    if not quality["passed"]:
        raise SystemExit("Quality gates failed. See artifacts/data_quality_report.md")

    evaluation = evaluate_phase2_dataset(rows, jobs)
    baseline_reference = {
        "baseline_name": "phase2_tfidf_reference",
        "dataset_version": PHASE2_DATASET_VERSION,
        "dataset_sha256": distribution["dataset_sha256"],
        "scorer_source": SCORER_SOURCE,
        "tfidf_config": {
            "ngram_range": TFIDF_NGRAM_RANGE,
            "max_features": TFIDF_MAX_FEATURES,
            "stop_words": TFIDF_STOP_WORDS,
            "sublinear_tf": TFIDF_SUBLINEAR_TF,
        },
        "thresholds": {"good": GOOD_THRESHOLD, "medium": MEDIUM_THRESHOLD},
        "metrics": {
            "top1_accuracy": evaluation["ranking_metrics"]["top1_accuracy"],
            "top3_hit_rate": evaluation["ranking_metrics"]["top3_hit_rate"],
            "mrr": evaluation["ranking_metrics"]["mrr"],
        },
    }
    baseline_reference_path = artifacts_dir / "phase2_baseline_reference.json"
    baseline_reference_path.write_text(json.dumps(baseline_reference, indent=2), encoding="utf-8")

    eval_ready_md = artifacts_dir / "eval_ready_summary.md"
    eval_ready_md.write_text(
        "\n".join(
            [
                "# Eval Ready Summary",
                "",
                f"- Dataset version fixed: `{PHASE2_DATASET_VERSION}`",
                f"- CV count: {evaluation['num_cvs']}",
                f"- Pair count: {evaluation['num_pairs']}",
                "",
                "## Ranking Checks",
                f"- Top-1 accuracy: {evaluation['ranking_metrics']['top1_accuracy']}",
                f"- Top-3 hit rate: {evaluation['ranking_metrics']['top3_hit_rate']}",
                f"- MRR: {evaluation['ranking_metrics']['mrr']}",
                "",
                "## Label Confusion Summary",
                f"- {evaluation['label_confusion_summary']}",
                "",
                "## Threshold Sanity (0.40 / 0.20)",
                f"- {evaluation['threshold_sanity_table']}",
                "",
                "## Error Analysis (Top-1 misses)",
                f"- Total Top-1 failures: {evaluation['error_analysis']['top1_failures_total']}",
                f"- Failures by bucket: {evaluation['error_analysis']['top1_failures_by_bucket']}",
                f"- Medium vs Low confusion: {evaluation['error_analysis']['medium_vs_low_confusion']}",
                f"- Failure reason counts: {evaluation['error_analysis']['failure_reason_counts']}",
            ]
        ),
        encoding="utf-8",
    )

    eval_results_path = artifacts_dir / "eval_results.json"
    eval_results_path.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")

    print(f"Wrote {dataset_path}")
    print(f"Wrote {quality_md}")
    print(f"Wrote {distribution_path}")
    print(f"Wrote {eval_ready_md}")
    print(f"Wrote {eval_results_path}")
    print(f"Wrote {baseline_reference_path}")
