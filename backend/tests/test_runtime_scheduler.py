import pytest

from app.protocol import ExecutionResult, Observation, Position
from app.runtime import RuntimeState
from app.storage import EventStore


def observation() -> Observation:
    return Observation(
        position=Position(x=0, y=64, z=0),
        biome="plains",
        health=20,
        hunger=20,
        time_of_day=6000,
        light_level=15,
        floor_block="grass_block",
    )


@pytest.mark.anyio
async def test_autonomy_off_returns_idle(tmp_path) -> None:
    runtime = RuntimeState(EventStore(tmp_path / "events.sqlite3"))

    command = await runtime.handle_observation(observation())
    snapshot = await runtime.snapshot()

    assert command.command == "idle"
    assert snapshot.autonomy_enabled is False
    assert snapshot.mission_mode == "idle"
    assert snapshot.command_in_flight is None


@pytest.mark.anyio
async def test_scheduler_reports_status_while_command_in_flight(tmp_path) -> None:
    runtime = RuntimeState(EventStore(tmp_path / "events.sqlite3"))
    await runtime.set_autonomy(True, mode="explore")

    first = await runtime.handle_observation(observation())
    second = await runtime.handle_observation(observation())

    assert first.command == "explore"
    assert second.command == "report_state"
    assert second.reason == f"{first.command_id} in flight"

    await runtime.handle_execution_result(
        ExecutionResult(command_id=first.command_id, ok=True, message="movement complete", position=Position(x=4, y=64, z=0))
    )
    third = await runtime.handle_observation(observation())

    assert third.command == "explore"
    assert third.command_id != first.command_id


@pytest.mark.anyio
async def test_manual_move_to_runs_once_without_autonomy(tmp_path) -> None:
    runtime = RuntimeState(EventStore(tmp_path / "events.sqlite3"))

    queued = await runtime.queue_move_to(Position(x=6, y=64, z=2), max_duration_ms=3000)
    first = await runtime.handle_observation(observation())
    second = await runtime.handle_observation(observation())
    snapshot = await runtime.snapshot()

    assert queued.command == "move_to"
    assert first.command == "move_to"
    assert first.target == Position(x=6, y=64, z=2)
    assert second.command == "report_state"
    assert snapshot.queued_command is None
    assert snapshot.command_in_flight == first

    await runtime.handle_execution_result(
        ExecutionResult(command_id=first.command_id, ok=True, message="movement complete", position=Position(x=6, y=64, z=2))
    )
    third = await runtime.handle_observation(observation())
    snapshot = await runtime.snapshot()

    assert third.command == "idle"
    assert snapshot.autonomy_enabled is False
    assert snapshot.mission_mode == "idle"
    assert snapshot.command_in_flight is None


@pytest.mark.anyio
async def test_movement_watchdog_stops_stuck_command(tmp_path) -> None:
    runtime = RuntimeState(EventStore(tmp_path / "events.sqlite3"))
    await runtime.set_autonomy(True, mode="explore")

    first = await runtime.handle_observation(observation())
    command = first
    for index in range(5):
        stuck_observation = observation()
        stuck_observation.position.x = index * 0.01
        command = await runtime.handle_observation(stuck_observation)

    snapshot = await runtime.snapshot()
    watchdog_events = runtime.store.list_events(event_type="movement_watchdog")

    assert first.command == "explore"
    assert command.command == "idle"
    assert command.reason == f"movement watchdog stopped {first.command_id}"
    assert snapshot.command_in_flight is None
    assert watchdog_events[0]["payload"]["stopped_command_id"] == first.command_id
