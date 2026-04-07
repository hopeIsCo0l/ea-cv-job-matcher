from collections import Counter

from src.config.settings import ETHIOPIAN_COMPANY_TOKEN, MAX_JOBS_PER_REQUEST
from src.scoring.text_utils import normalize_text


def run_quality_gates(rows: list[dict]) -> dict:
    errors: list[str] = []

    if not rows:
        return {"passed": False, "errors": ["Dataset is empty"], "stats": {}}

    empty_text_rows = 0
    cv_registry = {}
    pair_keys = set()
    duplicate_pair_count = 0
    non_ethiopian_count = 0
    job_ids = set()
    label_counts = Counter()
    bucket_counts = Counter()

    for row in rows:
        cv_id = row["cv_id"]
        job_id = row["job_id"]

        if not normalize_text(row.get("cv_text", "")) or not normalize_text(row.get("job_description", "")):
            empty_text_rows += 1

        if cv_id in cv_registry and cv_registry[cv_id] != row.get("cv_text", ""):
            errors.append(f"Inconsistent cv_text found for cv_id={cv_id}")
        cv_registry[cv_id] = row.get("cv_text", "")

        pair_key = (cv_id, job_id)
        if pair_key in pair_keys:
            duplicate_pair_count += 1
        pair_keys.add(pair_key)

        if ETHIOPIAN_COMPANY_TOKEN not in normalize_text(row.get("company_name", "")):
            non_ethiopian_count += 1

        job_ids.add(job_id)
        label_counts[row["expected_label"]] += 1
        bucket_counts[row.get("match_bucket", "unknown")] += 1

    if empty_text_rows:
        errors.append(f"Found {empty_text_rows} rows with empty cv_text or job_description")
    if duplicate_pair_count:
        errors.append(f"Duplicate (cv_id, job_id) pairs found: {duplicate_pair_count}")
    if non_ethiopian_count:
        errors.append(f"Non-Ethiopian rows found: {non_ethiopian_count}")
    if len(job_ids) != MAX_JOBS_PER_REQUEST:
        errors.append(f"Expected exactly {MAX_JOBS_PER_REQUEST} jobs, found {len(job_ids)}")

    high = bucket_counts.get("high", 0)
    medium = bucket_counts.get("medium", 0)
    low = bucket_counts.get("low", 0)
    if min(high, medium, low) == 0:
        errors.append("One or more CV buckets are empty")
    else:
        imbalance_ratio = max(high, medium, low) / min(high, medium, low)
        if imbalance_ratio > 1.25:
            errors.append(f"CV bucket imbalance ratio too high: {imbalance_ratio:.2f}")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "stats": {
            "rows": len(rows),
            "unique_cv_ids": len(cv_registry),
            "unique_jobs": len(job_ids),
            "label_counts": dict(label_counts),
            "bucket_counts": dict(bucket_counts),
        },
    }
