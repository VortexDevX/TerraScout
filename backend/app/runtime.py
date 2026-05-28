from __future__ import annotations

import asyncio
from contextlib import suppress

from app.engine import decide
from app.protocol import (
    ActionCommand,
    ExecutionResult,
    Observation,
    RiskReport,
    SelectedGoal,
    TelemetrySnapshot,
    WorldState,
)
from app.storage import EventStore


class RuntimeState:
    def __init__(self, store: EventStore) -> None:
        self.store = store
        self.connection_status: str = "offline"
        self.observation: Observation | None = None
        self.world_state: WorldState | None = None
        self.risk_report: RiskReport | None = None
        self.selected_goal: SelectedGoal | None = None
        self.action_command: ActionCommand | None = None
        self._lock = asyncio.Lock()

    async def handle_observation(
        self,
        observation: Observation,
        connection_status: str = "bot_connected",
    ) -> ActionCommand:
        state, risk, goal, command = decide(observation)
        async with self._lock:
            self.connection_status = connection_status
            self.observation = observation
            self.world_state = state
            self.risk_report = risk
            self.selected_goal = goal
            self.action_command = command
        for event_type, payload in (
            ("observation", observation),
            ("world_state", state),
            ("risk_report", risk),
            ("selected_goal", goal),
            ("action_command", command),
        ):
            self.store.append(event_type, payload)
        return command

    async def handle_execution_result(self, result: ExecutionResult) -> None:
        self.store.append("execution_result", result)

    async def snapshot(self) -> TelemetrySnapshot:
        async with self._lock:
            return TelemetrySnapshot(
                connection_status=self.connection_status,  # type: ignore[arg-type]
                observation=self.observation,
                world_state=self.world_state,
                risk_report=self.risk_report,
                selected_goal=self.selected_goal,
                action_command=self.action_command,
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

