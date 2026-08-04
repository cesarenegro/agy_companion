from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.models.workspaces import WorkspaceRecord


class RuntimeAdapterError(RuntimeError):
    """Base bridge error raised by a runtime adapter."""


class RuntimeSession(BaseModel):
    runtime_session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeApprovalRequest(BaseModel):
    runtime_action_id: str | None = None
    action_type: str
    reason: str
    risk_level: str
    message: str | None = None
    command: str | None = None
    working_directory: str | None = None
    affected_files: list[str] = Field(default_factory=list)


class RuntimeStreamChunk(BaseModel):
    text: str
    sequence: int


class RuntimeMessageResult(BaseModel):
    message_text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    stream_chunks: list[RuntimeStreamChunk] = Field(default_factory=list)
    approval_request: RuntimeApprovalRequest | None = None


class AgentRuntimeAdapter(Protocol):
    async def create_session(self, workspace: WorkspaceRecord, options: dict[str, Any]) -> RuntimeSession: ...

    async def send_message(
        self,
        session_id: str,
        message: str,
        attachments: list[str],
    ) -> RuntimeMessageResult: ...

    async def approve_action(self, approval_id: str) -> None: ...

    async def reject_action(self, approval_id: str, reason: str | None = None) -> None: ...

    async def stop_task(self, task_id: str) -> None: ...

    async def resume_session(self, session_id: str) -> None: ...

    async def close_session(self, session_id: str) -> None: ...
