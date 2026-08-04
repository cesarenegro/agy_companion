import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class AuditLogService:
    def __init__(self) -> None:
        data_dir = Path(__file__).resolve().parents[2] / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self._jsonl_path = data_dir / "audit_log.jsonl"
        self._sqlite_path = data_dir / "audit_log.sqlite3"
        self._initialize_sqlite()

    def append(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "eventType": event_type,
            "payload": payload,
        }
        with self._jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
        self._append_sqlite(record)

    def _initialize_sqlite(self) -> None:
        with sqlite3.connect(self._sqlite_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def _append_sqlite(self, record: dict[str, Any]) -> None:
        with sqlite3.connect(self._sqlite_path) as connection:
            connection.execute(
                "INSERT INTO audit_log (timestamp, event_type, payload_json) VALUES (?, ?, ?)",
                (
                    record["timestamp"],
                    record["eventType"],
                    json.dumps(record["payload"], ensure_ascii=True),
                ),
            )
            connection.commit()

    @property
    def jsonl_path(self) -> str:
        return str(self._jsonl_path)

    @property
    def sqlite_path(self) -> str:
        return str(self._sqlite_path)


audit_log = AuditLogService()
