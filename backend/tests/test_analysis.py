from app.analysis import build_ops_summary


def test_ops_summary_detects_stuck_unfinished_movement() -> None:
    events = []
    for index in range(6):
        events.append(
            {
                "id": index + 1,
                "timestamp": f"2026-01-01T00:00:0{index}Z",
                "event_type": "observation",
                "payload": {
                    "position": {"x": 1.0 + index * 0.02, "y": 64.0, "z": 1.0},
                    "biome": "plains",
                },
            }
        )
    events.append(
        {
            "id": 7,
            "timestamp": "2026-01-01T00:00:06Z",
            "event_type": "decision_cycle",
            "payload": {
                "risk_report": {"score": 20, "sources": []},
                "action_command": {"command_id": "cmd-1", "command": "explore"},
            },
        }
    )

    summary = build_ops_summary(events)

    assert summary["stuck"]["is_stuck"] is True
    assert summary["distance_traveled"] > 0
    assert summary["risk"]["histogram"]["0-24"] == 1


def test_ops_summary_counts_command_outcomes_and_failures() -> None:
    events = [
        {
            "id": 1,
            "timestamp": "2026-01-01T00:00:00Z",
            "event_type": "decision_cycle",
            "payload": {
                "risk_report": {"score": 80, "sources": [{"name": "lava"}]},
                "action_command": {"command_id": "cmd-1", "command": "flee"},
            },
        },
        {
            "id": 2,
            "timestamp": "2026-01-01T00:00:01Z",
            "event_type": "execution_result",
            "payload": {"command_id": "cmd-1", "ok": False, "message": "pathfinding failed"},
        },
    ]

    summary = build_ops_summary(events)

    assert summary["command_stats"]["flee"]["failed"] == 1
    assert summary["command_stats"]["flee"]["success_rate"] == 0
    assert summary["safety_incidents"]["lava"] == 1
    assert summary["recent_failures"][0]["message"] == "pathfinding failed"
