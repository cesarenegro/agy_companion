from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class BridgeEvent(BaseModel):
    event_id: str = Field(alias="eventId")
    type: str
    session_id: str | None = Field(alias="sessionId", default=None)
    task_id: str | None = Field(alias="taskId", default=None)
    timestamp: datetime
    payload: dict[str, Any]

    @classmethod
    def _build(
        cls,
        *,
        event_type: str,
        session_id: str | None,
        task_id: str | None,
        payload: dict[str, Any],
    ) -> "BridgeEvent":
        return cls(
            eventId=f"evt_{uuid4().hex[:12]}",
            type=event_type,
            sessionId=session_id,
            taskId=task_id,
            timestamp=datetime.now(UTC),
            payload=payload,
        )

    @classmethod
    def session_created(cls, *, session_id: str, task_id: str | None, payload: dict[str, Any]) -> "BridgeEvent":
        return cls._build(event_type="session.created", session_id=session_id, task_id=task_id, payload=payload)

    @classmethod
    def assistant_delta(cls, *, session_id: str, task_id: str | None, payload: dict[str, Any]) -> "BridgeEvent":
        return cls._build(event_type="assistant.delta", session_id=session_id, task_id=task_id, payload=payload)

    @classmethod
    def assistant_completed(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        payload: dict[str, Any],
    ) -> "BridgeEvent":
        return cls._build(
            event_type="assistant.completed",
            session_id=session_id,
            task_id=task_id,
            payload=payload,
        )

    @classmethod
    def activity_started(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        payload: dict[str, Any],
    ) -> "BridgeEvent":
        return cls._build(
            event_type="activity.started",
            session_id=session_id,
            task_id=task_id,
            payload=payload,
        )

    @classmethod
    def activity_completed(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        payload: dict[str, Any],
    ) -> "BridgeEvent":
        return cls._build(
            event_type="activity.completed",
            session_id=session_id,
            task_id=task_id,
            payload=payload,
        )

    @classmethod
    def task_status_changed(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        payload: dict[str, Any],
    ) -> "BridgeEvent":
        return cls._build(
            event_type="task.status_changed",
            session_id=session_id,
            task_id=task_id,
            payload=payload,
        )

    @classmethod
    def approval_requested(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        payload: dict[str, Any],
    ) -> "BridgeEvent":
        return cls._build(
            event_type="approval.requested",
            session_id=session_id,
            task_id=task_id,
            payload=payload,
        )

    @classmethod
    def approval_resolved(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        payload: dict[str, Any],
    ) -> "BridgeEvent":
        return cls._build(
            event_type="approval.resolved",
            session_id=session_id,
            task_id=task_id,
            payload=payload,
        )
