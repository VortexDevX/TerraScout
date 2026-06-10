from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

from pydantic import BaseModel


class EventStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._lock = Lock()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS debug_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_debug_events_timestamp ON debug_events(timestamp)"
            )

    def append(self, event_type: str, payload: BaseModel | dict[str, Any]) -> int:
        if isinstance(payload, BaseModel):
            body = payload.model_dump(mode="json")
        else:
            body = payload
        timestamp = datetime.now(UTC).isoformat()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO debug_events (timestamp, event_type, payload_json) VALUES (?, ?, ?)",
                (timestamp, event_type, json.dumps(body, sort_keys=True)),
            )
            return int(cursor.lastrowid)

    def list_events(self, limit: int = 25, event_type: str | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 1000))
        where = ""
        params: tuple[Any, ...]
        if event_type:
            where = "WHERE event_type = ?"
            params = (event_type, limit)
        else:
            params = (limit,)
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, timestamp, event_type, payload_json
                FROM debug_events
                {where}
                ORDER BY id DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
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

    def recent(self, limit: int = 25) -> list[dict[str, Any]]:
        return self.list_events(limit=limit)

    def count_by_type(self) -> dict[str, int]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_type, COUNT(*) AS event_count
                FROM debug_events
                GROUP BY event_type
                ORDER BY event_type
                """
            ).fetchall()
        return {row["event_type"]: int(row["event_count"]) for row in rows}
