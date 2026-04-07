from typing import List, Tuple

from src.config.settings import ETHIOPIAN_COMPANY_TOKEN, MAX_JOBS_PER_REQUEST, SUPPORTED_ROLE_TITLES
from src.data.schemas import JobInput
from src.scoring.text_utils import normalize_text


def is_ethiopian_airlines_job(company_name: str) -> bool:
    return ETHIOPIAN_COMPANY_TOKEN in normalize_text(company_name)


def is_supported_role_title(title: str) -> bool:
    return normalize_text(title) in SUPPORTED_ROLE_TITLES


def _has_required_text(job: JobInput) -> bool:
    return bool(normalize_text(job.title) and normalize_text(job.description) and normalize_text(job.job_id))


def filter_and_cap_jobs(jobs: List[JobInput]) -> Tuple[List[JobInput], List[dict]]:
    valid_jobs: List[JobInput] = []
    excluded_jobs: List[dict] = []

    for job in jobs:
        if not is_ethiopian_airlines_job(job.company_name):
            excluded_jobs.append({"job_id": job.job_id, "reason": "non-ethiopian"})
            continue
        if not is_supported_role_title(job.title):
            excluded_jobs.append({"job_id": job.job_id, "reason": "out-of-scope-role"})
            continue
        if not _has_required_text(job):
            excluded_jobs.append({"job_id": job.job_id, "reason": "missing-text"})
            continue
        valid_jobs.append(job)

    if len(valid_jobs) > MAX_JOBS_PER_REQUEST:
        sorted_jobs = sorted(valid_jobs, key=lambda j: (j.job_id.lower(), j.title.lower()))
        kept = sorted_jobs[:MAX_JOBS_PER_REQUEST]
        trimmed = sorted_jobs[MAX_JOBS_PER_REQUEST:]
        for job in trimmed:
            excluded_jobs.append({"job_id": job.job_id, "reason": "cap-exceeded-deterministic-trim"})
        valid_jobs = kept

    return valid_jobs, excluded_jobs
