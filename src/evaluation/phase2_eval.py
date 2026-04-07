from collections import Counter, defaultdict

from src.config.settings import GOOD_THRESHOLD, MEDIUM_THRESHOLD, SCORER_SOURCE
from src.data.schemas import JobInput
from src.evaluation.metrics import compute_metrics
from src.scoring.engine import TfidfScorer
from src.scoring.labels import label_from_score
from src.scoring.text_utils import normalize_text


def _build_cv_targets(rows: list[dict]) -> dict:
    targets = {}
    cv_texts = {}
    cv_buckets = {}
    for row in rows:
        targets[row["cv_id"]] = row["target_job_id"]
        cv_texts[row["cv_id"]] = row["cv_text"]
        cv_buckets[row["cv_id"]] = row.get("match_bucket", "unknown")
    return targets, cv_texts, cv_buckets


def evaluate_phase2_dataset(rows: list[dict], jobs: list[dict]) -> dict:
    scorer = TfidfScorer()
    job_inputs = [
        JobInput(
            job_id=job["job_id"],
            title=job["title"],
            description=job["description"],
            company_name=job["company_name"],
        )
        for job in jobs
    ]

    targets, cv_texts, cv_buckets = _build_cv_targets(rows)
    pair_expectations = {(row["cv_id"], row["job_id"]): row["expected_label"] for row in rows}

    per_sample = []
    confusion = defaultdict(Counter)
    threshold_sanity = Counter()
    scored_pairs = []
    top1_failures = []
    failure_buckets = Counter()
    error_reason_counts = Counter()

    for cv_id, cv_text in cv_texts.items():
        ranked = scorer.score_jobs(cv_text, job_inputs)
        predicted_ids = [item["job_id"] for item in ranked]
        expected_top1 = targets[cv_id]
        top_label = ranked[0]["label"] if ranked else "bad"

        per_sample.append(
            {
                "sample_id": cv_id,
                "expected_top1_job_id": expected_top1,
                "predicted_top1_job_id": predicted_ids[0] if predicted_ids else None,
                "predicted_ranking": predicted_ids,
                "top_score": ranked[0]["score"] if ranked else 0.0,
                "top_label": top_label,
            }
        )

        expected_result = next((item for item in ranked if item["job_id"] == expected_top1), None)
        expected_rank = predicted_ids.index(expected_top1) + 1 if expected_top1 in predicted_ids else None
        token_count = len(normalize_text(cv_text).split())

        if predicted_ids and predicted_ids[0] != expected_top1:
            failure_bucket = cv_buckets.get(cv_id, "unknown")
            failure_buckets[failure_bucket] += 1

            reasons = []
            if expected_result and not expected_result.get("top_terms"):
                reasons.append("missing_domain_terms")
                error_reason_counts["missing_domain_terms"] += 1
            if token_count < 12:
                reasons.append("short_or_noisy_cv_text")
                error_reason_counts["short_or_noisy_cv_text"] += 1
            if expected_result and expected_result["score"] < MEDIUM_THRESHOLD:
                reasons.append("threshold_effect_below_medium_cutoff")
                error_reason_counts["threshold_effect_below_medium_cutoff"] += 1
            if not reasons:
                reasons.append("ranking_signal_mismatch")
                error_reason_counts["ranking_signal_mismatch"] += 1

            top1_failures.append(
                {
                    "cv_id": cv_id,
                    "match_bucket": failure_bucket,
                    "expected_top1_job_id": expected_top1,
                    "predicted_top1_job_id": predicted_ids[0],
                    "expected_job_rank": expected_rank,
                    "expected_job_score": expected_result["score"] if expected_result else 0.0,
                    "predicted_top1_score": ranked[0]["score"] if ranked else 0.0,
                    "reasons": reasons,
                }
            )

        for row in ranked:
            predicted_label = label_from_score(row["score"])
            expected_label = pair_expectations[(cv_id, row["job_id"])]
            confusion[expected_label][predicted_label] += 1
            threshold_sanity[predicted_label] += 1
            scored_pairs.append(
                {
                    "cv_id": cv_id,
                    "job_id": row["job_id"],
                    "score": row["score"],
                    "expected_label": expected_label,
                    "predicted_label": predicted_label,
                }
            )

    ranking_metrics = compute_metrics(per_sample)
    label_confusion = {expected: dict(predicted_map) for expected, predicted_map in confusion.items()}
    threshold_table = {
        "thresholds": {"good": GOOD_THRESHOLD, "medium": MEDIUM_THRESHOLD},
        "predicted_counts": dict(threshold_sanity),
    }
    medium_low_confusion = {
        "expected_medium_predicted_bad": confusion["medium"].get("bad", 0),
        "expected_bad_predicted_medium": confusion["bad"].get("medium", 0),
    }

    return {
        "scorer_source": SCORER_SOURCE,
        "num_cvs": len(cv_texts),
        "num_pairs": len(scored_pairs),
        "ranking_metrics": ranking_metrics,
        "label_confusion_summary": label_confusion,
        "threshold_sanity_table": threshold_table,
        "per_sample": per_sample,
        "scored_pairs": scored_pairs,
        "error_analysis": {
            "top1_failures_total": len(top1_failures),
            "top1_failures_by_bucket": dict(failure_buckets),
            "medium_vs_low_confusion": medium_low_confusion,
            "failure_reason_counts": dict(error_reason_counts),
            "top1_failure_examples": top1_failures[:25],
        },
    }
