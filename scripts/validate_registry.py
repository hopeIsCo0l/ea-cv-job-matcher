"""
Validate registry JSON, promotion criteria, and model cards against Pydantic schemas.
Exit 0 on success; non-zero on validation failure.
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError

from src.registry.schemas import (  # noqa: E402
    ModelCard,
    ModelRegistryEntry,
    PromotionCriteria,
    RegistryState,
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    criteria_path = root / "config" / "promotion_criteria.json"
    if criteria_path.is_file():
        try:
            PromotionCriteria.model_validate_json(criteria_path.read_text(encoding="utf-8"))
        except ValidationError as e:
            errors.append(f"promotion_criteria: {e}")
    else:
        errors.append(f"Missing {criteria_path}")

    reg_path = root / "registry" / "registry.json"
    if reg_path.is_file():
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        for m in data.get("models", []):
            try:
                ModelRegistryEntry.model_validate(m)
            except ValidationError as e:
                errors.append(f"registry entry {m.get('model_id')}: {e}")
    else:
        errors.append(f"Missing {reg_path}")

    cards_dir = root / "registry" / "model_cards"
    if cards_dir.is_dir():
        for p in cards_dir.glob("*.json"):
            try:
                ModelCard.model_validate_json(p.read_text(encoding="utf-8"))
            except ValidationError as e:
                errors.append(f"model card {p.name}: {e}")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print("Registry validation OK")
    print(f"- {criteria_path}")
    print(f"- {reg_path}")
    print(f"- model_cards/*.json ({len(list(cards_dir.glob('*.json')))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
