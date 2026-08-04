import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.models.workspaces import WorkspaceRecord
from app.runtime.base import (
    AgentRuntimeAdapter,
    RuntimeAdapterError,
    RuntimeApprovalRequest,
    RuntimeMessageResult,
    RuntimeSession,
    RuntimeStreamChunk,
)


class OfficialSdkError(RuntimeAdapterError):
    """Raised when the official Antigravity SDK adapter cannot satisfy a request."""


@dataclass(frozen=True)
class OfficialSdkConfig:
    project: str
    location: str
    default_conversation_id: str | None = None
    model: str | None = None
    save_dir: str | None = None
    app_data_dir: str | None = None
    runtime_name: str = "official_sdk"

    @classmethod
    def from_env(cls) -> "OfficialSdkConfig | None":
        project = os.getenv("ANTIGRAVITY_VERTEX_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("ANTIGRAVITY_VERTEX_LOCATION") or os.getenv("GOOGLE_CLOUD_LOCATION")
        if not project or not location:
            return None
        return cls(
            project=project,
            location=location,
            default_conversation_id=os.getenv("ANTIGRAVITY_CONVERSATION_ID"),
            model=os.getenv("ANTIGRAVITY_MODEL"),
            save_dir=os.getenv("ANTIGRAVITY_SAVE_DIR"),
            app_data_dir=os.getenv("ANTIGRAVITY_APP_DATA_DIR"),
        )


class OfficialSdkAdapter(AgentRuntimeAdapter):
    def __init__(self, config: OfficialSdkConfig) -> None:
        self._config = config
        self._sessions: dict[str, dict[str, str | None]] = {}
        self._pending_approvals: dict[str, RuntimeApprovalRequest] = {}

    async def create_session(self, workspace: WorkspaceRecord, options: dict[str, Any]) -> RuntimeSession:
        conversation_id = (
            options.get("conversation_id")
            or options.get("runtime_session_id")
            or self._config.default_conversation_id
        )
        bridge_session_key = conversation_id or f"sdk::{uuid4()}"
        self._sessions[bridge_session_key] = {
            "workspace_path": workspace.absolute_path,
            "conversation_id": conversation_id,
        }
        return RuntimeSession(
            runtime_session_id=bridge_session_key,
            metadata={
                "workspacePath": workspace.absolute_path,
                "adapter": self._config.runtime_name,
                "createMode": "resume_existing" if conversation_id else "new_sdk_session",
                "vertexProject": self._config.project,
                "vertexLocation": self._config.location,
            },
        )

    async def send_message(
        self,
        session_id: str,
        message: str,
        attachments: list[str],
    ) -> RuntimeMessageResult:
        Agent, LocalAgentConfig, from_file, policy = self._load_sdk_symbols()

        session_context = self._sessions.setdefault(
            session_id,
            {"workspace_path": None, "conversation_id": session_id if not session_id.startswith("sdk::") else None},
        )
        pending_approvals: list[RuntimeApprovalRequest] = []

        async def approval_handler(tool_call: Any) -> bool:
            approval = RuntimeApprovalRequest(
                runtime_action_id=f"rtact_{uuid4().hex[:12]}",
                action_type=tool_call.name,
                reason=f"SDK policy requested approval for tool '{tool_call.name}'.",
                risk_level="high" if tool_call.name == "run_command" else "medium",
                message=message,
                command=self._stringify_tool_args(tool_call.args),
                working_directory=session_context.get("workspace_path"),
                affected_files=[tool_call.canonical_path] if getattr(tool_call, "canonical_path", None) else [],
            )
            self._pending_approvals[approval.runtime_action_id or ""] = approval
            pending_approvals.append(approval)
            return False

        config = LocalAgentConfig(
            workspaces=[session_context["workspace_path"]] if session_context.get("workspace_path") else None,
            conversation_id=session_context.get("conversation_id"),
            policies=[
                policy.ask_user("run_command", handler=approval_handler, name="bridge_run_command_approval"),
                policy.allow("*", name="bridge_allow_all"),
            ],
            model=self._config.model,
            vertex=True,
            project=self._config.project,
            location=self._config.location,
            save_dir=self._config.save_dir,
            app_data_dir=self._config.app_data_dir,
        )

        prompt: str | list[Any]
        if attachments:
            prompt = [message, *[from_file(path) for path in attachments]]
        else:
            prompt = message

        async with Agent(config) as agent:
            response = await agent.chat(prompt)
            stream_chunks: list[RuntimeStreamChunk] = []
            async for token in response:
                if token:
                    stream_chunks.append(
                        RuntimeStreamChunk(text=token, sequence=len(stream_chunks) + 1)
                    )
            message_text = "".join(chunk.text for chunk in stream_chunks)
            if not message_text:
                message_text = await response.text()
            conversation_id = getattr(agent, "conversation_id", None)

        if conversation_id:
            session_context["conversation_id"] = conversation_id
            if session_id.startswith("sdk::"):
                self._sessions[conversation_id] = session_context

        return RuntimeMessageResult(
            message_text=message_text,
            metadata={
                "adapter": self._config.runtime_name,
                "conversationId": conversation_id or session_context.get("conversation_id"),
                "streamChunkCount": len(stream_chunks),
                "attachmentCount": len(attachments),
                "approvalIntercepted": bool(pending_approvals),
            },
            stream_chunks=stream_chunks,
            approval_request=pending_approvals[0] if pending_approvals else None,
        )

    async def approve_action(self, approval_id: str) -> None:
        approval = self._pending_approvals.get(approval_id)
        if approval is None:
            raise OfficialSdkError(f"Unknown SDK approval id: {approval_id}")
        raise OfficialSdkError(
            "SDK approval interception is wired but runtime resume after external approval "
            "still requires live verification against the official SDK."
        )

    async def reject_action(self, approval_id: str, reason: str | None = None) -> None:
        approval = self._pending_approvals.get(approval_id)
        if approval is None:
            raise OfficialSdkError(f"Unknown SDK approval id: {approval_id}")
        _ = reason

    async def stop_task(self, task_id: str) -> None:
        raise OfficialSdkError(
            "Stop is not implemented yet for the official SDK adapter pending live verification."
        )

    async def resume_session(self, session_id: str) -> None:
        if session_id not in self._sessions:
            raise OfficialSdkError(f"Unknown SDK session id: {session_id}")

    async def close_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    @staticmethod
    def _stringify_tool_args(args: Any) -> str:
        if args is None:
            return ""
        if isinstance(args, str):
            return args
        try:
            return json.dumps(args, ensure_ascii=True, sort_keys=True)
        except TypeError:
            return str(args)

    @staticmethod
    def sdk_installed() -> bool:
        try:
            OfficialSdkAdapter._load_sdk_symbols()
        except OfficialSdkError:
            return False
        return True

    @staticmethod
    def _load_sdk_symbols() -> tuple[Any, Any, Any, Any]:
        try:
            from google.antigravity import Agent, LocalAgentConfig, from_file, hooks
        except ImportError as exc:
            raise OfficialSdkError(
                "Official SDK is not installed. Install google-antigravity to enable this adapter."
            ) from exc
        return Agent, LocalAgentConfig, from_file, hooks.policy


def validate_attachment_paths(workspace: WorkspaceRecord, attachments: list[str]) -> list[str]:
    resolved_paths: list[str] = []
    root = workspace.resolved_root()
    for attachment in attachments:
        candidate = Path(attachment).resolve()
        if candidate != root and root not in candidate.parents:
            raise OfficialSdkError(f"Attachment escapes the authorized workspace: {attachment}")
        if not candidate.exists() or not candidate.is_file():
            raise OfficialSdkError(f"Attachment file not found: {candidate}")
        resolved_paths.append(str(candidate))
    return resolved_paths
