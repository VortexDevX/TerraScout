import pytest

from app.protocol import Observation, Position
from app.runtime import RuntimeState
from app.storage import EventStore
from app.training import build_training_examples, examples_to_jsonl, summarize_examples
from scripts.train_policy import build_policy, events_to_training_rows


async def _record_cycle(store: EventStore) -> None:
    runtime = RuntimeState(store)
    await runtime.set_autonomy(True)
    observation = Observation(
        position=Position(x=4, y=64, z=8),
        biome="plains",
        health=20,
        hunger=20,
        time_of_day=6000,
        light_level=15,
    )
    await runtime.handle_observation(observation)


@pytest.mark.anyio
async def test_training_examples_from_decision_cycles(tmp_path) -> None:
    store = EventStore(tmp_path / "training.sqlite3")
    await _record_cycle(store)

    examples = build_training_examples(store.list_events(event_type="decision_cycle"))
    summary = summarize_examples(examples, store.count_by_type())
    jsonl = examples_to_jsonl(examples)

    assert len(examples) == 1
    assert examples[0]["features"]["health"] == 20
    assert examples[0]["features"]["terrain_path_iq"] is not None
    assert examples[0]["features"]["terrain_fingerprint"] != "unknown"
    assert examples[0]["labels"]["command"] == "explore"
    assert summary["training_examples"] == 1
    assert '"risk_score": 0' in jsonl


def test_build_policy_detects_bad_daylight_darkness() -> None:
    rows = [
        {
            "features": {"time_of_day": 1000, "light_level": 0, "floor_block": "grass_block"},
            "labels": {"command": "explore", "success": True},
            "execution": {"ok": True, "position": {"x": 5, "z": 0}},
            "raw": {"observation": {"position": {"x": 0, "z": 0}}},
        },
        {
            "features": {"time_of_day": 2000, "light_level": 0, "floor_block": "grass_block"},
            "labels": {"command": "explore", "success": True},
            "execution": {"ok": True, "position": {"x": 7, "z": 0}},
            "raw": {"observation": {"position": {"x": 0, "z": 0}}},
        },
    ]

    policy = build_policy(rows)

    assert policy["ignore_daylight_darkness"] is True
    assert policy["source_examples"] == 2
    assert policy["real_outcomes"] == 2
    assert policy["explore_radius"] == 6


def test_events_to_training_rows_joins_execution_result() -> None:
    events = [
        {
            "id": 1,
            "timestamp": "now",
            "event_type": "decision_cycle",
            "payload": {
                "observation": {
                    "position": {"x": 0, "y": 64, "z": 0},
                    "biome": "plains",
                    "health": 20,
                    "hunger": 20,
                    "time_of_day": 1000,
                    "light_level": 15,
                    "floor_block": "grass_block",
                },
                "world_state": {"is_dark": False, "is_night": False, "hostile_count": 0},
                "risk_report": {"score": 0},
                "terrain_report": {
                    "path_iq": 82,
                    "base_score": 74,
                    "wonder_score": 28,
                    "elevation_range": 2,
                    "water_ratio": 0.12,
                    "passable_ratio": 0.96,
                    "personality": "Settler",
                    "fingerprint": "abc123",
                },
                "selected_goal": {"name": "explore"},
                "action_command": {"command": "explore", "command_id": "cmd-1"},
            },
        },
        {
            "id": 2,
            "timestamp": "now",
            "event_type": "execution_result",
            "payload": {"command_id": "cmd-1", "ok": True, "message": "movement complete", "position": {"x": 4, "z": 0}},
        },
    ]

    rows = events_to_training_rows(events)

    assert len(rows) == 1
    assert rows[0]["labels"]["success"] is True
    assert rows[0]["execution"]["message"] == "movement complete"
    assert rows[0]["features"]["terrain_path_iq"] == 82
