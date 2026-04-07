import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.evaluation.dataset import build_synthetic_dataset


if __name__ == "__main__":
    output_path = Path("artifacts/synthetic_dataset.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset = build_synthetic_dataset()
    output_path.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    print(f"Wrote synthetic dataset to {output_path}")
