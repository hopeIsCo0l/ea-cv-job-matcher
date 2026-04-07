"""Pydantic schemas for registry entries and machine-readable model cards."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RegistryState(str, Enum):
    candidate = "candidate"
    staging = "staging"
    production = "production"


class ApprovalRecord(BaseModel):
    """Who moved a model, when, and why (audit trail)."""

    action: str = Field(
        ...,
        description="e.g. promote_to_staging, promote_to_production, demote_to_candidate",
    )
    actor: str = Field(..., description="Identifier: email, service account, or role")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = Field(..., min_length=1)
    ticket: str | None = Field(default=None, description="Issue/PR/ticket reference")


class FairnessReport(BaseModel):
    """Fairness-style checks on synthetic CV buckets (Phase 2/3 eval)."""

    cv_bucket_top1: dict[str, float] | None = Field(
        default=None,
        description="Top-1 accuracy per match_bucket (high/medium/low) if computed",
    )
    cv_bucket_top1_spread: float | None = Field(
        default=None,
        description="max(top1) - min(top1) across buckets",
    )
    insufficient_bucket_behavior: str | None = Field(
        default=None,
        description="fail | warn_only | not_applicable_exempt (see config/promotion_criteria.json)",
    )
    gates_passed: bool | None = None
    notes: str | None = None


class EvaluationMetrics(BaseModel):
    top1_accuracy: float | None = None
    top3_hit_rate: float | None = None
    mrr: float | None = None
    pair_accuracy: float | None = None
    eval_source: str | None = Field(
        default=None,
        description="e.g. phase3_comparison.json, phase2_full_eval",
    )


class ModelCard(BaseModel):
    """
    Machine-readable model card (promotion + audit).
    Serialized to JSON; validate with registry/model_card.schema.json.
    """

    model_config = ConfigDict(protected_namespaces=())

    schema_version: str = "1.0"
    model_id: str
    display_name: str
    registry_state: RegistryState
    scorer_source: str
    model_type: str = Field(
        ...,
        description="e.g. tfidf_cosine, logistic_regression_tfidf",
    )
    artifact_uri: str | None = Field(
        default=None,
        description="Path, URL, or object-store URI to serialized model",
    )
    training: dict[str, Any] = Field(default_factory=dict)
    evaluation: EvaluationMetrics = Field(default_factory=EvaluationMetrics)
    fairness: FairnessReport = Field(default_factory=FairnessReport)
    promotion_criteria_version: str = Field(
        default="1",
        description="Must match config/promotion_criteria.json version",
    )
    gates_satisfied: bool = False
    approvals: list[ApprovalRecord] = Field(default_factory=list)
    risks: str | None = None
    intended_use: str | None = None
    limitations: str | None = None


class ModelRegistryEntry(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: str
    state: RegistryState
    model_card_path: str
    current_version_tag: str | None = None
    history: list[ApprovalRecord] = Field(default_factory=list)


class PromotionCriteria(BaseModel):
    """Loaded from config/promotion_criteria.json."""

    model_config = ConfigDict(extra="allow")

    version: str
    description: str | None = None
    baseline_axes: dict[str, Any] = Field(default_factory=dict)
    ranking_gates: dict[str, Any] = Field(default_factory=dict)
    fairness_gates: dict[str, Any] = Field(default_factory=dict)
    quality_gates: list[str] = Field(default_factory=list)
