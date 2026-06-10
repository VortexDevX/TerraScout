from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _path_env(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    protocol_version: str = os.getenv("TERRASCOUT_PROTOCOL_VERSION", "1")
    db_path: Path = _path_env("TERRASCOUT_DB_PATH", "backend/data/terrascout.sqlite3")
    policy_path: Path = _path_env("TERRASCOUT_POLICY_PATH", "backend/models/policy.json")
    mock_mode: bool = _bool_env("TERRASCOUT_MOCK_MODE", False)
    observation_interval_ms: int = _int_env("TERRASCOUT_OBSERVATION_INTERVAL_MS", 1000)
    decision_interval_ms: int = _int_env("TERRASCOUT_DECISION_INTERVAL_MS", 1000)
    dashboard_interval_ms: int = _int_env("TERRASCOUT_DASHBOARD_INTERVAL_MS", 1000)


settings = Settings()
