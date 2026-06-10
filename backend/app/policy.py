from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LearnedPolicy:
    schema_version: int = 2
    source_examples: int = 0
    real_outcomes: int = 0
    ignore_daylight_darkness: bool = True
    explore_radius: int = 8
    flee_radius: int = 12
    min_safe_health: float = 6
    command_success_rates: dict[str, float] = field(default_factory=dict)
    failure_counts: dict[str, int] = field(default_factory=dict)
    feedback_counts: dict[str, int] = field(default_factory=dict)


def _clamp_int(value: object, fallback: int, low: int, high: int) -> int:
    try:
        parsed = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return fallback
    return max(low, min(high, parsed))


def _float(value: object, fallback: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return fallback


def load_policy(path: Path = Path("backend/models/policy.json")) -> LearnedPolicy:
    if not path.exists():
        return LearnedPolicy()
    data = json.loads(path.read_text(encoding="utf-8"))
    return LearnedPolicy(
        schema_version=_clamp_int(data.get("schema_version"), 2, 1, 99),
        source_examples=_clamp_int(data.get("source_examples"), 0, 0, 10_000_000),
        real_outcomes=_clamp_int(data.get("real_outcomes"), 0, 0, 10_000_000),
        ignore_daylight_darkness=bool(data.get("ignore_daylight_darkness", True)),
        explore_radius=_clamp_int(data.get("explore_radius"), 8, 3, 16),
        flee_radius=_clamp_int(data.get("flee_radius"), 12, 4, 24),
        min_safe_health=_float(data.get("min_safe_health"), 6),
        command_success_rates={str(k): _float(v, 0) for k, v in data.get("command_success_rates", {}).items()},
        failure_counts={str(k): int(v) for k, v in data.get("failure_counts", {}).items()},
        feedback_counts={str(k): int(v) for k, v in data.get("feedback_counts", {}).items()},
    )
