import pytest

from app.mock import mock_observations
from app.runtime import RuntimeState
from app.storage import EventStore


@pytest.mark.anyio
async def test_mock_observation_drives_runtime_and_logging(tmp_path) -> None:
    store = EventStore(tmp_path / "mock.sqlite3")
    runtime = RuntimeState(store)
    stream = mock_observations(interval_ms=1)

    observation = await anext(stream)
    command = await runtime.handle_observation(observation, connection_status="mock_connected")
    snapshot = await runtime.snapshot()

    assert command.command in {"idle", "explore", "flee", "move_to", "report_state"}
    assert snapshot.connection_status == "mock_connected"
    assert snapshot.observation is not None
    assert snapshot.risk_report is not None
    assert {event["event_type"] for event in store.recent()} >= {
        "observation",
        "world_state",
        "risk_report",
        "selected_goal",
        "action_command",
    }

