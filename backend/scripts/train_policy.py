from __future__ import annotations

import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any


SURFACE_BLOCKS = {
    "grass_block",
    "dirt",
    "coarse_dirt",
    "sand",
    "red_sand",
    "gravel",
    "stone",
    "snow_block",
    "podzol",
    "mycelium",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_events_from_sqlite(path: Path, limit: int = 20_000) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"SQLite DB not found: {path}")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        """
        SELECT id, timestamp, event_type, payload_json
        FROM debug_events
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    connection.close()
    events = [
        {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "event_type": row["event_type"],
            "payload": json.loads(row["payload_json"]),
        }
        for row in rows
    ]
    events.reverse()
    return events


def events_to_training_rows(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    executions: dict[str, dict[str, Any]] = {}
    feedback: dict[str, list[dict[str, Any]]] = defaultdict(list)
    cycles: list[dict[str, Any]] = []

    for event in events:
        payload = event.get("payload") or {}
        if event.get("event_type") == "execution_result":
            command_id = payload.get("command_id")
            if command_id:
                executions[command_id] = payload
        elif event.get("event_type") == "training_feedback":
            command_id = payload.get("command_id")
            if command_id:
                feedback[command_id].append(payload)
        elif event.get("event_type") == "decision_cycle":
            cycles.append(event)

    rows: list[dict[str, Any]] = []
    for event in cycles:
        raw = event.get("payload") or {}
        command = raw.get("action_command") or {}
        command_id = command.get("command_id")
        execution = executions.get(command_id, {})
        row = decision_cycle_to_row(event)
        if not row:
            continue
        row["execution"] = execution
        row["feedback"] = feedback.get(command_id, [])
        row["labels"]["success"] = bool(execution.get("ok")) if execution else None
        row["labels"]["execution_message"] = execution.get("message")
        rows.append(row)
    return rows


def decision_cycle_to_row(event: dict[str, Any]) -> dict[str, Any] | None:
    raw = event.get("payload") or event.get("raw") or {}
    observation = raw.get("observation") or {}
    state = raw.get("world_state") or {}
    risk = raw.get("risk_report") or {}
    terrain = raw.get("terrain_report") or {}
    goal = raw.get("selected_goal") or {}
    command = raw.get("action_command") or {}
    if not observation or not command:
        return None

    features = {
        "biome": observation.get("biome") or "unknown",
        "health": observation.get("health", 0),
        "hunger": observation.get("hunger", 0),
        "time_of_day": observation.get("time_of_day", 0),
        "light_level": observation.get("light_level", 0),
        "is_dark": 1 if state.get("is_dark") else 0,
        "is_night": 1 if state.get("is_night") else 0,
        "hostile_count": state.get("hostile_count", 0),
        "nearby_lava": 1 if observation.get("nearby_lava") else 0,
        "nearby_cliff": 1 if observation.get("nearby_cliff") else 0,
        "nearby_deep_water": 1 if observation.get("nearby_deep_water") else 0,
        "feet_block": observation.get("feet_block") or "unknown",
        "floor_block": observation.get("floor_block") or "unknown",
        "terrain_path_iq": terrain.get("path_iq"),
        "terrain_base_score": terrain.get("base_score"),
        "terrain_wonder_score": terrain.get("wonder_score"),
        "terrain_elevation_range": terrain.get("elevation_range"),
        "terrain_water_ratio": terrain.get("water_ratio"),
        "terrain_passable_ratio": terrain.get("passable_ratio"),
        "terrain_personality": terrain.get("personality") or "unknown",
        "terrain_fingerprint": terrain.get("fingerprint") or "unknown",
    }
    return {
        "event_id": event.get("id"),
        "timestamp": event.get("timestamp"),
        "features": features,
        "labels": {
            "risk_score": risk.get("score", 0),
            "goal": goal.get("name"),
            "command": command.get("command"),
            "command_id": command.get("command_id"),
        },
        "raw": raw,
    }


def _position(payload: dict[str, Any], path: list[str]) -> dict[str, float] | None:
    value: Any = payload
    for key in path:
        value = value.get(key) if isinstance(value, dict) else None
    if not isinstance(value, dict):
        return None
    if not all(key in value for key in ("x", "z")):
        return None
    return {"x": float(value["x"]), "z": float(value["z"])}


def _move_distance(row: dict[str, Any]) -> float | None:
    start = _position(row, ["raw", "observation", "position"])
    end = _position(row, ["execution", "position"])
    if not start or not end:
        return None
    return math.hypot(end["x"] - start["x"], end["z"] - start["z"])


def _success(row: dict[str, Any]) -> bool | None:
    value = row.get("labels", {}).get("success")
    return value if isinstance(value, bool) else None


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def build_policy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    commands = Counter(row.get("labels", {}).get("command", "unknown") for row in rows)
    outcome_rows = [row for row in rows if _success(row) is not None]
    success_by_command: dict[str, list[bool]] = defaultdict(list)
    failures = Counter()
    feedback = Counter()
    explore_distances: list[float] = []
    daylight_dark_success = 0
    daylight_surface_success = 0
    safe_healths: list[float] = []
    terrain_scores: dict[str, list[float]] = defaultdict(list)

    for row in outcome_rows:
        command = str(row.get("labels", {}).get("command") or "unknown")
        ok = bool(_success(row))
        success_by_command[command].append(ok)
        if not ok:
            message = str(row.get("labels", {}).get("execution_message") or "unknown")
            failures[message.split(":")[0]] += 1
        for note in row.get("feedback", []):
            feedback[str(note.get("rating", "unknown"))] += 1

        features = row.get("features", {})
        for key in ("terrain_path_iq", "terrain_base_score", "terrain_wonder_score"):
            value = features.get(key)
            if isinstance(value, int | float):
                terrain_scores[key].append(float(value))
        if ok:
            safe_healths.append(float(features.get("health") or 0))
        if command == "explore" and ok:
            distance = _move_distance(row)
            if distance and distance >= 1:
                explore_distances.append(distance)

        time_of_day = int(features.get("time_of_day") or 0)
        is_day = 0 <= time_of_day < 12300
        is_surface = str(features.get("floor_block")) in SURFACE_BLOCKS
        if ok and is_day and is_surface:
            daylight_surface_success += 1
            if int(features.get("light_level") or 0) <= 7:
                daylight_dark_success += 1

    command_success_rates = {
        command: round(sum(results) / len(results), 3)
        for command, results in sorted(success_by_command.items())
        if results
    }

    if explore_distances:
        explore_radius = _clamp(round(median(explore_distances)), 4, 12)
    elif command_success_rates.get("explore", 1) < 0.35:
        explore_radius = 4
    else:
        explore_radius = 8

    min_safe_health = 6
    if safe_healths:
        min_safe_health = _clamp(round(min(safe_healths) - 1), 4, 10)

    return {
        "schema_version": 2,
        "source_examples": len(rows),
        "real_outcomes": len(outcome_rows),
        "command_counts": dict(commands),
        "command_success_rates": command_success_rates,
        "failure_counts": dict(failures),
        "feedback_counts": dict(feedback),
        "ignore_daylight_darkness": daylight_surface_success > 0 and daylight_dark_success / daylight_surface_success > 0.2,
        "explore_radius": explore_radius,
        "flee_radius": 12,
        "min_safe_health": min_safe_health,
        "terrain_score_averages": {
            key: round(sum(values) / len(values), 2) for key, values in sorted(terrain_scores.items()) if values
        },
    }


def load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() in {".sqlite", ".sqlite3", ".db"}:
        return events_to_training_rows(load_events_from_sqlite(path))
    exported = load_jsonl(path)
    rows = []
    for row in exported:
        if "features" in row and "labels" in row:
            rows.append(row)
        else:
            converted = decision_cycle_to_row(row)
            if converted:
                rows.append(converted)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Train TerraScout policy from real replay outcomes.")
    parser.add_argument("source", type=Path, help="SQLite replay DB or exported JSONL.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("backend/models/policy.json"),
        help="Output policy path.",
    )
    args = parser.parse_args()

    rows = load_rows(args.source)
    if not rows:
        raise SystemExit("No usable training rows found.")

    policy = build_policy(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(policy, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {args.out} from {len(rows)} rows, {policy['real_outcomes']} real outcomes")


if __name__ == "__main__":
    main()
