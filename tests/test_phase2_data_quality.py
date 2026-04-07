from src.evaluation.dataset import build_phase2_cvs, build_phase2_jobs, build_phase2_pairs
from src.evaluation.quality import run_quality_gates


def test_phase2_dataset_counts():
    jobs = build_phase2_jobs()
    cvs = build_phase2_cvs()
    rows = build_phase2_pairs(cvs, jobs)

    assert len(jobs) == 8
    assert len(cvs) == 200
    assert len(rows) == 1600


def test_phase2_quality_gates_pass():
    jobs = build_phase2_jobs()
    cvs = build_phase2_cvs()
    rows = build_phase2_pairs(cvs, jobs)
    quality = run_quality_gates(rows)

    assert quality["passed"] is True
    assert quality["errors"] == []
