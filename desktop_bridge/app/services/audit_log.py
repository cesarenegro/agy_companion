import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class AuditLogService:
    def __init__(self) -> None:
        self._path = Path(__file__).resolve().parents[2] / "data" / "audit_log.jsonl"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "eventType": event_type,
            "payload": payload,
        }
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    @property
    def path(self) -> str:
        return str(self._path)


audit_log = AuditLogService()
