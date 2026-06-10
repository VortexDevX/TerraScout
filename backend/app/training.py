from __future__ import annotations

import json
from typing import Any


def _bool(payload: dict[str, Any], key: str) -> int:
    return 1 if payload.get(key) else 0


def decision_cycle_to_example(event: dict[str, Any]) -> dict[str, Any] | None:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        return None

    observation = payload.get("observation") or {}
    world_state = payload.get("world_state") or {}
    risk_report = payload.get("risk_report") or {}
    terrain_report = payload.get("terrain_report") or {}
    selected_goal = payload.get("selected_goal") or {}
    action_command = payload.get("action_command") or {}

    if not observation or not world_state or not risk_report:
        return None

    features = {
        "health": observation.get("health", 0),
        "hunger": observation.get("hunger", 0),
        "time_of_day": observation.get("time_of_day", 0),
        "light_level": observation.get("light_level", 0),
        "hostile_count": world_state.get("hostile_count", 0),
        "nearest_hostile_distance": world_state.get("nearest_hostile_distance"),
        "is_night": _bool(world_state, "is_night"),
        "is_dark": _bool(world_state, "is_dark"),
        "nearby_lava": _bool(observation, "nearby_lava"),
        "nearby_cliff": _bool(observation, "nearby_cliff"),
        "nearby_deep_water": _bool(observation, "nearby_deep_water"),
        "feet_block": observation.get("feet_block") or "unknown",
        "floor_block": observation.get("floor_block") or "unknown",
        "terrain_path_iq": terrain_report.get("path_iq"),
        "terrain_base_score": terrain_report.get("base_score"),
        "terrain_wonder_score": terrain_report.get("wonder_score"),
        "terrain_elevation_range": terrain_report.get("elevation_range"),
        "terrain_water_ratio": terrain_report.get("water_ratio"),
        "terrain_passable_ratio": terrain_report.get("passable_ratio"),
        "terrain_personality": terrain_report.get("personality") or "unknown",
        "terrain_fingerprint": terrain_report.get("fingerprint") or "unknown",
    }
    labels = {
        "risk_score": risk_report.get("score", 0),
        "goal": selected_goal.get("name"),
        "command": action_command.get("command"),
    }

    return {
        "event_id": event.get("id"),
        "timestamp": event.get("timestamp"),
        "features": features,
        "labels": labels,
        "raw": payload,
    }


def build_training_examples(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples = []
    for event in events:
        example = decision_cycle_to_example(event)
        if example:
            examples.append(example)
    return examples


def examples_to_jsonl(examples: list[dict[str, Any]]) -> str:
    return "\n".join(json.dumps(example, sort_keys=True) for example in examples)


def summarize_examples(examples: list[dict[str, Any]], event_counts: dict[str, int]) -> dict[str, Any]:
    goal_counts: dict[str, int] = {}
    command_counts: dict[str, int] = {}
    risk_scores: list[int] = []

    for example in examples:
        labels = example["labels"]
        goal = labels.get("goal") or "unknown"
        command = labels.get("command") or "unknown"
        goal_counts[goal] = goal_counts.get(goal, 0) + 1
        command_counts[command] = command_counts.get(command, 0) + 1
        risk_scores.append(int(labels.get("risk_score") or 0))

    avg_risk = round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0
    return {
        "training_examples": len(examples),
        "event_counts": event_counts,
        "goal_counts": goal_counts,
        "command_counts": command_counts,
        "average_risk_score": avg_risk,
        "max_risk_score": max(risk_scores) if risk_scores else 0,
    }
