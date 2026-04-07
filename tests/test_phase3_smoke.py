from pathlib import Path

import pytest

from src.evaluation.phase3_comparison import run_phase3_comparison


def test_phase3_comparison_runs_when_dataset_present():
    root = Path(__file__).resolve().parents[1]
    dataset = root / "data" / "processed" / "dataset_v1.jsonl"
    if not dataset.is_file():
        pytest.skip("dataset_v1.jsonl not generated; run run_phase2_pipeline.py")

    artifacts = root / "artifacts"
    out = run_phase3_comparison(dataset, artifacts)
    assert "results" in out
    assert len(out["results"]) >= 2
    names = {r["model_name"] for r in out["results"]}
    assert "tfidf_cosine_baseline" in names
    assert "promotion" in out
