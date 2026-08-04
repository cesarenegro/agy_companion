from typing import Any, Protocol

from pydantic import BaseModel

from app.models.workspaces import WorkspaceRecord


class RuntimeSession(BaseModel):
    runtime_session_id: str | None = None
    metadata: dict[str, Any] = {}


class RuntimeMessageResult(BaseModel):
    message_text: str
    metadata: dict[str, Any] = {}


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
