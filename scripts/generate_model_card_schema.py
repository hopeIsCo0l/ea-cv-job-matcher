"""Write registry/model_card.schema.json from Pydantic ModelCard (JSON Schema draft 2020-12)."""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.registry.schemas import ModelCard  # noqa: E402


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    out = root / "registry" / "model_card.schema.json"
    schema = ModelCard.model_json_schema()
    out.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
