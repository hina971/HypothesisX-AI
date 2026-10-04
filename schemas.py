"""Shared data contract between agents, the evidence reviewer and the UI.

Every agent fills only its own section of a HypothesisRecord. All structures
serialise to plain JSON so the Orchestrator Agent can pass them around.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

STABILITY_LEVELS = ("stable", "moderately_sensitive", "unstable", "not_assessable")


@dataclass
class RobustnessConfig:
    seed: int = 42
    alpha: float = 0.05
    n_boot: int = 1000
    n_splits: int = 200
    tolerance: float = 0.25          # max relative coefficient change still called "stable"
    outlier_z: float = 3.0
    winsor_pct: float = 0.05
    max_candidate_features: int = 8
    min_std_beta: float = 0.10       # smallest standardised effect treated as non-negligible
    min_delta_r2: float = 0.01       # smallest cross-validated R2 gain treated as meaningful


@dataclass
class RobustnessResult:
    test: str
    method: str
    configuration: Dict[str, Any]
    original_result: Dict[str, Any]
    modified_result: Dict[str, Any]
    stability: str
    changed_materially: Optional[bool]
    interpretation: str
    coefficient: Optional[float] = None
    p_value: Optional[float] = None
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    effect_size: Optional[float] = None
    model_performance: Dict[str, Any] = field(default_factory=dict)
    direction: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HypothesisRecord:
    id: str
    statement: str
    variables: Dict[str, Any]                 # {"x": str, "y": str, "controls": [str]}
    origin: Dict[str, Any] = field(default_factory=dict)   # why it was discovered
    statistical_results: Dict[str, Any] = field(default_factory=dict)
    ml_results: Dict[str, Any] = field(default_factory=dict)
    robustness_results: List[Dict[str, Any]] = field(default_factory=list)
    alternative_explanations: List[Dict[str, Any]] = field(default_factory=list)
    data_quality: Dict[str, Any] = field(default_factory=dict)
    evidence_report: Dict[str, Any] = field(default_factory=dict)
    causal_design: bool = False               # True only if a valid causal design was implemented

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "HypothesisRecord":
        return cls(**d)
