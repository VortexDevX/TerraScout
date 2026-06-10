from __future__ import annotations

import math
from typing import Any


def _distance(a: dict[str, Any], b: dict[str, Any]) -> float:
    return math.dist(
        (float(a.get("x", 0)), float(a.get("y", 0)), float(a.get("z", 0))),
        (float(b.get("x", 0)), float(b.get("y", 0)), float(b.get("z", 0))),
    )


def _bucket_risk(score: int) -> str:
    if score < 25:
        return "0-24"
    if score < 50:
        return "25-49"
    if score < 75:
        return "50-74"
    return "75-100"


def _command_for_id(decision_by_command_id: dict[str, dict[str, Any]], command_id: str) -> str:
    command = decision_by_command_id.get(command_id, {}).get("action_command", {})
    return str(command.get("command") or "unknown")


def build_ops_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    observations = [event for event in events if event.get("event_type") == "observation"]
    decision_cycles = [event for event in events if event.get("event_type") == "decision_cycle"]
    execution_results = [event for event in events if event.get("event_type") == "execution_result"]

    positions = [
        event.get("payload", {}).get("position")
        for event in observations
        if isinstance(event.get("payload", {}).get("position"), dict)
    ]
    distance_traveled = 0.0
    for previous, current in zip(positions, positions[1:]):
        distance_traveled += _distance(previous, current)

    decision_by_command_id: dict[str, dict[str, Any]] = {}
    risk_scores: list[int] = []
    risk_histogram = {"0-24": 0, "25-49": 0, "50-74": 0, "75-100": 0}
    safety_incidents: dict[str, int] = {}

    for event in decision_cycles:
        payload = event.get("payload", {})
        action = payload.get("action_command", {})
        command_id = action.get("command_id")
        if command_id:
            decision_by_command_id[str(command_id)] = payload

        risk = payload.get("risk_report", {})
        score = int(risk.get("score") or 0)
        risk_scores.append(score)
        risk_histogram[_bucket_risk(score)] += 1
        for source in risk.get("sources", []):
            name = str(source.get("name") or "unknown")
            safety_incidents[name] = safety_incidents.get(name, 0) + 1

    command_stats: dict[str, dict[str, float | int]] = {}
    recent_failures: list[dict[str, Any]] = []
    result_by_command_id: dict[str, dict[str, Any]] = {}

    for event in execution_results:
        payload = event.get("payload", {})
        command_id = str(payload.get("command_id") or "")
        result_by_command_id[command_id] = payload
        command = _command_for_id(decision_by_command_id, command_id)
        stats = command_stats.setdefault(command, {"ok": 0, "failed": 0, "success_rate": 0.0})
        if payload.get("ok"):
            stats["ok"] = int(stats["ok"]) + 1
        else:
            stats["failed"] = int(stats["failed"]) + 1
            recent_failures.append(
                {
                    "timestamp": event.get("timestamp"),
                    "command_id": command_id,
                    "command": command,
                    "message": payload.get("message") or "unknown failure",
                }
            )

    for stats in command_stats.values():
        total = int(stats["ok"]) + int(stats["failed"])
        stats["success_rate"] = round(float(stats["ok"]) / total, 3) if total else 0.0

    latest_movement = None
    for event in reversed(decision_cycles):
        action = event.get("payload", {}).get("action_command", {})
        if action.get("command") in {"explore", "flee", "move_to"}:
            latest_movement = action
            break

    last_window = positions[-8:]
    recent_displacement = _distance(last_window[0], last_window[-1]) if len(last_window) >= 2 else 0.0
    movement_without_result = bool(
        latest_movement and latest_movement.get("command_id") not in result_by_command_id
    )
    stuck = movement_without_result and len(last_window) >= 5 and recent_displacement < 0.75

    avg_risk = round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0.0
    recommendations: list[str] = []
    if stuck:
        recommendations.append("Stop current movement and issue a smaller nearby move_to target.")
    if recent_failures:
        recommendations.append("Inspect recent pathfinding failures before increasing autonomy.")
    if safety_incidents.get("pathfinding_error", 0) >= 3:
        recommendations.append("Lower explore radius or improve safe target selection.")
    if avg_risk >= 45:
        recommendations.append("Collect safer daylight runs before trusting policy output.")
    if not recommendations:
        recommendations.append("No major operator action needed from recent replay window.")

    return {
        "event_count": len(events),
        "observation_count": len(observations),
        "decision_count": len(decision_cycles),
        "execution_count": len(execution_results),
        "latest_position": positions[-1] if positions else None,
        "distance_traveled": round(distance_traveled, 2),
        "recent_displacement": round(recent_displacement, 2),
        "stuck": {
            "is_stuck": stuck,
            "movement_without_result": movement_without_result,
            "window_observations": len(last_window),
            "reason": "movement command has no result and position barely changed" if stuck else "not stuck",
        },
        "risk": {
            "average": avg_risk,
            "max": max(risk_scores) if risk_scores else 0,
            "histogram": risk_histogram,
        },
        "command_stats": command_stats,
        "safety_incidents": safety_incidents,
        "recent_failures": recent_failures[-8:],
        "recommendations": recommendations,
    }
