from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


SessionStatus = Literal[
    "idle",
    "starting",
    "active",
    "waiting_approval",
    "waiting_user",
    "completed",
    "stopped",
    "failed",
    "disconnected",
]


class SessionRecord(BaseModel):
    session_id: str
    runtime_session_id: str | None = None
    workspace_id: str
    desktop_id: str
    title: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None = None
    active_task_id: str | None = None


class CreateSessionRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    title: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class CreateSessionResponse(BaseModel):
    session: SessionRecord


class SendMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    attachments: list[str] = Field(default_factory=list)
