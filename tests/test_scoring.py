from src.data.schemas import JobInput
from src.scoring.domain import filter_and_cap_jobs
from src.scoring.engine import TfidfScorer


BASE_JOB = {
    "title": "Trainee Ground Operations Officer",
    "description": "Ramp coordination and baggage operations.",
    "company_name": "Ethiopian Airlines",
}


def _job(job_id: str, description: str | None = None, company_name: str = "Ethiopian Airlines") -> JobInput:
    return JobInput(
        job_id=job_id,
        title="Trainee Pilot",
        description=description or "General aviation support and operations.",
        company_name=company_name,
    )


def test_ethiopian_only_filter_enforced():
    jobs = [
        _job("et-1", company_name="Ethiopian Airlines"),
        _job("other-1", company_name="Other Airline"),
    ]
    valid, excluded = filter_and_cap_jobs(jobs)

    assert len(valid) == 1
    assert valid[0].job_id == "et-1"
    assert excluded[0]["reason"] == "non-ethiopian"


def test_max_8_cap_enforced_deterministically():
    jobs = [_job(f"et-{i:02d}") for i in range(12)]
    valid, excluded = filter_and_cap_jobs(jobs)

    assert len(valid) == 8
    assert [job.job_id for job in valid] == [f"et-{i:02d}" for i in range(8)]
    assert all(row["reason"] == "cap-exceeded-deterministic-trim" for row in excluded)


def test_out_of_scope_role_excluded():
    jobs = [
        JobInput(
            job_id="et-x",
            title="Senior Network Engineer",
            description="Infrastructure and systems",
            company_name="Ethiopian Airlines",
        )
    ]
    valid, excluded = filter_and_cap_jobs(jobs)
    assert valid == []
    assert excluded[0]["reason"] == "out-of-scope-role"


def test_deterministic_ranking_for_fixed_input():
    scorer = TfidfScorer()
    jobs = [
        JobInput(job_id="a", title="A", description="engine turbine propulsion systems", company_name="Ethiopian Airlines"),
        JobInput(job_id="b", title="B", description="passenger support cabin hospitality", company_name="Ethiopian Airlines"),
    ]
    cv = "I studied turbine engine propulsion and aircraft systems"

    first = scorer.score_jobs(cv, jobs)
    second = scorer.score_jobs(cv, jobs)

    assert first == second
    assert first[0]["job_id"] == "a"


def test_score_range_between_zero_and_one():
    scorer = TfidfScorer()
    jobs = [_job("et-1"), _job("et-2", description="finance accounting reporting")]
    results = scorer.score_jobs("aviation support operations", jobs)

    for row in results:
        assert 0.0 <= row["score"] <= 1.0
