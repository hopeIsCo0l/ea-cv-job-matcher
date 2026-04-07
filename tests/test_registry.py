import json
from pathlib import Path

import pytest

from src.registry.schemas import ModelCard, ModelRegistryEntry, PromotionCriteria


def test_promotion_criteria_loads():
    root = Path(__file__).resolve().parents[1]
    p = root / "config" / "promotion_criteria.json"
    c = PromotionCriteria.model_validate_json(p.read_text(encoding="utf-8"))
    assert c.version == "2"
    assert "baseline_axes" in c.model_dump()
    assert "phase2_full_dataset" in c.baseline_axes
    assert "phase3_same_split" in c.baseline_axes
    assert "ranking_gates" in c.model_dump()


def test_registry_entries_validate():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "registry" / "registry.json").read_text(encoding="utf-8"))
    for m in data["models"]:
        ModelRegistryEntry.model_validate(m)


def test_baseline_model_card_validates():
    root = Path(__file__).resolve().parents[1]
    p = root / "registry" / "model_cards" / "baseline_tfidf_v1.json"
    card = ModelCard.model_validate_json(p.read_text(encoding="utf-8"))
    assert card.registry_state.value == "production"
    assert len(card.approvals) >= 1


def test_registry_state_enum():
    assert ModelCard(
        model_id="x",
        display_name="X",
        registry_state="candidate",
        scorer_source="s",
        model_type="t",
    ).registry_state.value == "candidate"
