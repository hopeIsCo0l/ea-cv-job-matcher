"""
Load production model metadata from registry (model card JSON).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.config.settings import RELEASE_TAG, SCORER_SOURCE


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=8)
def load_production_model_meta(registry_path: str) -> dict[str, Any]:
    """
    Resolve registry.json, find model with state production, merge model card scorer_source.
    Falls back to built-in defaults if files are missing (dev-friendly).
    """
    default: dict[str, Any] = {
        "model_id": "baseline_tfidf_cosine_v1",
        "model_version": RELEASE_TAG,
        "scorer_source": SCORER_SOURCE,
    }
    root = _repo_root()
    path = root / registry_path
    if not path.is_file():
        return default

    data = json.loads(path.read_text(encoding="utf-8"))
    prod = next((m for m in data.get("models", []) if m.get("state") == "production"), None)
    if not prod:
        return default

    model_id = prod.get("model_id", default["model_id"])
    version_tag = prod.get("current_version_tag") or RELEASE_TAG
    scorer = SCORER_SOURCE

    card_rel = prod.get("model_card_path")
    if card_rel:
        card_path = root / card_rel
        if card_path.is_file():
            card = json.loads(card_path.read_text(encoding="utf-8"))
            scorer = card.get("scorer_source", scorer)

    return {
        "model_id": model_id,
        "model_version": version_tag,
        "scorer_source": scorer,
    }
