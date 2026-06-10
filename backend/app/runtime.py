from __future__ import annotations

import asyncio
from contextlib import suppress
from itertools import count

from app.engine import decide
from app.protocol import (
    ActionCommand,
    CommandType,
    ExecutionResult,
    GoalName,
    Observation,
    Position,
    RiskReport,
    SelectedGoal,
    TelemetrySnapshot,
    TerrainReport,
    WorldState,
)
from app.storage import EventStore
from app.terrain import analyze_terrain

_status_counter = count(1)
_manual_counter = count(1)
_watchdog_counter = count(1)


class RuntimeState:
    def __init__(self, store: EventStore) -> None:
        self.store = store
        self.connection_status: str = "offline"
        self.autonomy_enabled = False
        self.mission_mode: str = "idle"
        self.command_in_flight: ActionCommand | None = None
        self.queued_command: ActionCommand | None = None
        self._in_flight_positions: list[Position] = []
        self.observation: Observation | None = None
        self.world_state: WorldState | None = None
        self.risk_report: RiskReport | None = None
        self.terrain_report: TerrainReport | None = None
        self.selected_goal: SelectedGoal | None = None
        self.action_command: ActionCommand | None = None
        self.last_execution_result: ExecutionResult | None = None
        self._lock = asyncio.Lock()

    async def handle_observation(
        self,
        observation: Observation,
        connection_status: str = "bot_connected",
    ) -> ActionCommand:
        state, risk, goal, command = decide(observation)
        terrain = analyze_terrain(observation)
        async with self._lock:
            autonomy_enabled = self.autonomy_enabled
            mission_mode = self.mission_mode
            command_in_flight = self.command_in_flight
            queued_command = self.queued_command

        watchdog_stop = False
        if command_in_flight and command_in_flight.command in {CommandType.explore, CommandType.flee, CommandType.move_to}:
            async with self._lock:
                if self.command_in_flight and self.command_in_flight.command_id == command_in_flight.command_id:
                    self._in_flight_positions.append(observation.position)
                    self._in_flight_positions = self._in_flight_positions[-8:]
                    watchdog_stop = self._movement_stuck()

        if command_in_flight and watchdog_stop:
            goal = SelectedGoal(name=GoalName.idle, utility=1.0, reason="movement watchdog stopped stuck command")
            command = ActionCommand(
                command_id=f"watchdog-{next(_watchdog_counter)}",
                command=CommandType.idle,
                reason=f"movement watchdog stopped {command_in_flight.command_id}",
                max_duration_ms=1000,
            )
            self.store.append(
                "movement_watchdog",
                {
                    "stopped_command_id": command_in_flight.command_id,
                    "positions": [position.model_dump(mode="json") for position in self._in_flight_positions],
                },
            )
        elif command_in_flight:
            goal = SelectedGoal(name=GoalName.report, utility=1.0, reason="command in flight")
            command = ActionCommand(
                command_id=f"status-{next(_status_counter)}",
                command=CommandType.report_state,
                reason=f"{command_in_flight.command_id} in flight",
                max_duration_ms=1000,
            )
        elif queued_command:
            goal = SelectedGoal(name=GoalName.explore, utility=1.0, reason="manual queued command")
            command = queued_command
        elif not autonomy_enabled:
            goal = SelectedGoal(name=GoalName.idle, utility=1.0, reason="autonomy paused")
            command = ActionCommand(
                command_id=command.command_id,
                command=CommandType.idle,
                reason="autonomy paused",
                max_duration_ms=1000,
            )
        elif mission_mode == "flee":
            goal = SelectedGoal(name=GoalName.flee, utility=1.0, reason="manual flee mission")
            command = ActionCommand(
                command_id=command.command_id,
                command=CommandType.flee,
                reason="manual flee mission",
                radius=command.radius,
                max_duration_ms=4000,
            )
        elif mission_mode == "explore" and goal.name not in {GoalName.flee, GoalName.survive}:
            goal = SelectedGoal(name=GoalName.explore, utility=1.0, reason="manual explore mission")
            command = ActionCommand(
                command_id=command.command_id,
                command=CommandType.explore,
                reason="manual explore mission",
                radius=command.radius,
                max_duration_ms=5000,
            )

        should_track = command.command in {CommandType.explore, CommandType.flee, CommandType.move_to}
        async with self._lock:
            self.connection_status = connection_status
            self.observation = observation
            self.world_state = state
            self.risk_report = risk
            self.terrain_report = terrain
            self.selected_goal = goal
            self.action_command = command
            if should_track:
                self.command_in_flight = command
                self._in_flight_positions = [observation.position]
            elif watchdog_stop:
                self.command_in_flight = None
                self._in_flight_positions = []
            if queued_command and command.command_id == queued_command.command_id:
                self.queued_command = None
        for event_type, payload in (
            ("observation", observation),
            ("world_state", state),
            ("risk_report", risk),
            ("terrain_report", terrain),
            ("selected_goal", goal),
            ("action_command", command),
        ):
            self.store.append(event_type, payload)
        self.store.append(
            "decision_cycle",
            {
                "schema_version": 1,
                "observation": observation.model_dump(mode="json"),
                "world_state": state.model_dump(mode="json"),
                "risk_report": risk.model_dump(mode="json"),
                "terrain_report": terrain.model_dump(mode="json"),
                "selected_goal": goal.model_dump(mode="json"),
                "action_command": command.model_dump(mode="json"),
            },
        )
        return command

    async def handle_execution_result(self, result: ExecutionResult) -> None:
        async with self._lock:
            self.last_execution_result = result
            if self.command_in_flight and result.command_id == self.command_in_flight.command_id:
                self.command_in_flight = None
                self._in_flight_positions = []
                if not self.autonomy_enabled and not self.queued_command:
                    self.mission_mode = "idle"
        self.store.append("execution_result", result)

    async def set_connection_status(self, connection_status: str) -> None:
        async with self._lock:
            self.connection_status = connection_status

    async def set_autonomy(self, enabled: bool, mode: str = "explore") -> None:
        async with self._lock:
            self.autonomy_enabled = enabled
            self.mission_mode = mode if enabled else "idle"
            if not enabled:
                self.command_in_flight = None
                self.queued_command = None
                self._in_flight_positions = []
            mission_mode = self.mission_mode
        self.store.append("autonomy_changed", {"enabled": enabled, "mode": mission_mode})

    async def queue_move_to(self, target: Position, max_duration_ms: int = 8000) -> ActionCommand:
        command = ActionCommand(
            command_id=f"manual-{next(_manual_counter)}",
            command=CommandType.move_to,
            reason="manual move_to queued from dashboard",
            target=target,
            max_duration_ms=max_duration_ms,
        )
        async with self._lock:
            self.queued_command = command
            self.mission_mode = "manual"
        self.store.append("manual_command_queued", command)
        return command

    def _movement_stuck(self) -> bool:
        if len(self._in_flight_positions) < 6:
            return False
        first = self._in_flight_positions[0]
        last = self._in_flight_positions[-1]
        dx = first.x - last.x
        dy = first.y - last.y
        dz = first.z - last.z
        return (dx * dx + dy * dy + dz * dz) ** 0.5 < 0.75

    async def snapshot(self) -> TelemetrySnapshot:
        async with self._lock:
            return TelemetrySnapshot(
                connection_status=self.connection_status,  # type: ignore[arg-type]
                autonomy_enabled=self.autonomy_enabled,
                mission_mode=self.mission_mode,  # type: ignore[arg-type]
                command_in_flight=self.command_in_flight,
                queued_command=self.queued_command,
                observation=self.observation,
                world_state=self.world_state,
                risk_report=self.risk_report,
                terrain_report=self.terrain_report,
                selected_goal=self.selected_goal,
                action_command=self.action_command,
                last_execution_result=self.last_execution_result,
                recent_events=self.store.recent(20),
            )


class DashboardHub:
    def __init__(self) -> None:
        self._connections: set[asyncio.Queue[TelemetrySnapshot]] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue[TelemetrySnapshot]:
        queue: asyncio.Queue[TelemetrySnapshot] = asyncio.Queue(maxsize=5)
        async with self._lock:
            self._connections.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue[TelemetrySnapshot]) -> None:
        async with self._lock:
            self._connections.discard(queue)

    async def broadcast(self, snapshot: TelemetrySnapshot) -> None:
        async with self._lock:
            queues = list(self._connections)
        for queue in queues:
            with suppress(asyncio.QueueFull):
                queue.put_nowait(snapshot)
