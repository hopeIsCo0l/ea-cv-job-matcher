from collections import Counter


def compute_metrics(per_sample_results: list[dict]) -> dict:
    if not per_sample_results:
        return {"top1_accuracy": 0.0, "top3_hit_rate": 0.0, "mrr": 0.0, "threshold_sanity": {}}

    n = len(per_sample_results)
    top1_hits = 0
    top3_hits = 0
    reciprocal_sum = 0.0
    labels = Counter()

    for row in per_sample_results:
        predicted_ids = row["predicted_ranking"]
        expected = row["expected_top1_job_id"]
        top_label = row["top_label"]
        labels[top_label] += 1

        if predicted_ids and predicted_ids[0] == expected:
            top1_hits += 1
        if expected in predicted_ids[:3]:
            top3_hits += 1

        if expected in predicted_ids:
            rank = predicted_ids.index(expected) + 1
            reciprocal_sum += 1.0 / rank

    return {
        "top1_accuracy": round(top1_hits / n, 4),
        "top3_hit_rate": round(top3_hits / n, 4),
        "mrr": round(reciprocal_sum / n, 4),
        "threshold_sanity": {
            "good": labels.get("good", 0),
            "medium": labels.get("medium", 0),
            "bad": labels.get("bad", 0),
        },
    }
