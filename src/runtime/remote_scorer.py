"""HTTP client for optional remote scorer service (Phase 5)."""

from __future__ import annotations

from typing import Any

import httpx


def forward_score(
    base_url: str,
    payload: dict[str, Any],
    timeout_seconds: float,
) -> dict[str, Any]:
    """
    POST /v1/score to remote service. Returns parsed JSON body.
    Raises on non-2xx or network error.
    """
    url = base_url.rstrip("/") + "/v1/score"
    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
