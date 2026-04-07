import csv
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.schemas import JobInput
from src.evaluation.dataset import build_synthetic_dataset
from src.evaluation.metrics import compute_metrics
from src.scoring.engine import TfidfScorer


if __name__ == "__main__":
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    dataset = build_synthetic_dataset()
    jobs = [JobInput(**job) for job in dataset["jobs"]]

    scorer = TfidfScorer()
    per_sample = []

    for sample in dataset["samples"]:
        ranked = scorer.score_jobs(sample["cv_text"], jobs)
        predicted = [item["job_id"] for item in ranked]
        per_sample.append(
            {
                "sample_id": sample["sample_id"],
                "expected_top1_job_id": sample["expected_top1_job_id"],
                "predicted_top1_job_id": predicted[0],
                "predicted_ranking": predicted,
                "top_score": ranked[0]["score"],
                "top_label": ranked[0]["label"],
            }
        )

    metrics = compute_metrics(per_sample)
    results = {
        "scorer_source": "baseline_tfidf_cosine_v1",
        "num_samples": len(per_sample),
        "metrics": metrics,
        "per_sample": per_sample,
    }

    results_json = artifacts_dir / "eval_results.json"
    results_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    csv_path = artifacts_dir / "eval_per_sample.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sample_id",
                "expected_top1_job_id",
                "predicted_top1_job_id",
                "top_score",
                "top_label",
            ],
        )
        writer.writeheader()
        for row in per_sample:
            writer.writerow(
                {
                    "sample_id": row["sample_id"],
                    "expected_top1_job_id": row["expected_top1_job_id"],
                    "predicted_top1_job_id": row["predicted_top1_job_id"],
                    "top_score": row["top_score"],
                    "top_label": row["top_label"],
                }
            )

    summary_md = artifacts_dir / "eval_summary.md"
    summary_md.write_text(
        "\n".join(
            [
                "# Evaluation Summary",
                "",
                "## Configuration",
                "- Scorer: `baseline_tfidf_cosine_v1`",
                "- Domain: Ethiopian Airlines trainee jobs (max 8)",
                f"- Samples: {len(per_sample)}",
                "",
                "## Metrics",
                f"- Top-1 accuracy: {metrics['top1_accuracy']}",
                f"- Top-3 hit rate: {metrics['top3_hit_rate']}",
                f"- MRR: {metrics['mrr']}",
                "",
                "## Threshold sanity (`good` / `medium` / `bad`)",
                f"- good: {metrics['threshold_sanity']['good']}",
                f"- medium: {metrics['threshold_sanity']['medium']}",
                f"- bad: {metrics['threshold_sanity']['bad']}",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {results_json}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {summary_md}")
