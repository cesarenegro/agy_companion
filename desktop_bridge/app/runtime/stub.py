from typing import Any

from app.models.workspaces import WorkspaceRecord
from app.runtime.base import AgentRuntimeAdapter, RuntimeMessageResult, RuntimeSession


class StubRuntimeAdapter(AgentRuntimeAdapter):
    """Temporary adapter until the technical spike selects SDK or CLI."""

    async def create_session(self, workspace: WorkspaceRecord, options: dict[str, Any]) -> RuntimeSession:
        return RuntimeSession(runtime_session_id=f"stub::{workspace.workspace_id}")

    async def send_message(self, session_id: str, message: str, attachments: list[str]) -> RuntimeMessageResult:
        _ = (session_id, message, attachments)
        return RuntimeMessageResult(
            message_text="Stub adapter accepted the message.",
            metadata={"adapter": "stub"},
        )

    async def approve_action(self, approval_id: str) -> None:
        _ = approval_id

    async def reject_action(self, approval_id: str, reason: str | None = None) -> None:
        _ = (approval_id, reason)

    async def stop_task(self, task_id: str) -> None:
        _ = task_id

    async def resume_session(self, session_id: str) -> None:
        _ = session_id

    async def close_session(self, session_id: str) -> None:
        _ = session_id
