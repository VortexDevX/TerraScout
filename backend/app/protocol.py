from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

PROTOCOL_VERSION = "1"


class Position(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    z: float


class HostileMob(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str
    position: Position
    distance: float


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bot_id: str = "terrascout"
    position: Position
    biome: str = "unknown"
    health: float = Field(ge=0, le=20)
    hunger: float = Field(ge=0, le=20)
    time_of_day: int = Field(ge=0, le=23999)
    light_level: int = Field(ge=0, le=15)
    nearby_hostiles: list[HostileMob] = Field(default_factory=list)
    nearby_lava: bool = False
    nearby_cliff: bool = False
    nearby_deep_water: bool = False
    pathfinding_error: str | None = None


class WorldState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bot_id: str
    position: Position
    biome: str
    health: float
    hunger: float
    is_night: bool
    is_dark: bool
    hostile_count: int
    nearest_hostile_distance: float | None
    hazards: list[str]


class RiskSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    score: int
    detail: str


class RiskReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=100)
    sources: list[RiskSource] = Field(default_factory=list)


class GoalName(str, Enum):
    survive = "survive"
    flee = "flee"
    explore = "explore"
    idle = "idle"
    report = "report"


class SelectedGoal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: GoalName
    utility: float
    reason: str


class CommandType(str, Enum):
    idle = "idle"
    explore = "explore"
    flee = "flee"
    move_to = "move_to"
    report_state = "report_state"


class ActionCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: str
    command: CommandType
    reason: str
    target: Position | None = None
    max_duration_ms: int = Field(default=5000, ge=100)


class ExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: str
    ok: bool
    message: str
    position: Position | None = None


class TelemetrySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connection_status: Literal["offline", "bot_connected", "mock_connected"]
    observation: Observation | None = None
    world_state: WorldState | None = None
    risk_report: RiskReport | None = None
    selected_goal: SelectedGoal | None = None
    action_command: ActionCommand | None = None
    recent_events: list[dict[str, Any]] = Field(default_factory=list)


class Envelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    protocol_version: str = PROTOCOL_VERSION
    payload: dict[str, Any]

    @field_validator("protocol_version")
    @classmethod
    def validate_protocol_version(cls, value: str) -> str:
        if value != PROTOCOL_VERSION:
            raise ValueError(f"Unsupported protocol version: {value}")
        return value


class DebugEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


def envelope(message_type: str, payload: BaseModel | dict[str, Any]) -> Envelope:
    if isinstance(payload, BaseModel):
        body = payload.model_dump(mode="json")
    else:
        body = payload
    return Envelope(type=message_type, payload=body)

