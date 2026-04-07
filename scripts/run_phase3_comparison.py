"""
Train Phase 3 candidates (LR, calibrated linear SVM, HistGradientBoosting) on shared TF-IDF
and write comparison table + JSON artifacts.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.evaluation.phase3_comparison import run_phase3_comparison  # noqa: E402


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    dataset_path = root / "data" / "processed" / "dataset_v1.jsonl"
    artifacts_dir = root / "artifacts"
    if not dataset_path.is_file():
        raise SystemExit(
            f"Missing {dataset_path}. Run: python scripts/run_phase2_pipeline.py"
        )
    run_phase3_comparison(dataset_path, artifacts_dir)
    print(f"Wrote {artifacts_dir / 'phase3_comparison.json'}")
    print(f"Wrote {artifacts_dir / 'phase3_comparison_table.md'}")
