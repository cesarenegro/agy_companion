import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from app.models.workspaces import WorkspaceRecord
from app.runtime.base import AgentRuntimeAdapter, RuntimeAdapterError, RuntimeMessageResult, RuntimeSession


class AntigravityCliError(RuntimeAdapterError):
    """Raised when the local Antigravity CLI cannot satisfy a bridge request."""


@dataclass(frozen=True)
class AntigravityCliConfig:
    executable_path: str
    ls_address: str
    csrf_token: str
    default_conversation_id: str | None = None

    @classmethod
    def from_env(cls) -> "AntigravityCliConfig | None":
        executable_path = os.getenv("ANTIGRAVITY_CLI_PATH", r"C:\Users\user\AppData\Local\agy\bin\agy.exe")
        ls_address = os.getenv("ANTIGRAVITY_LS_ADDRESS")
        csrf_token = os.getenv("ANTIGRAVITY_CSRF_TOKEN")
        if not ls_address or not csrf_token:
            return None
        return cls(
            executable_path=executable_path,
            ls_address=ls_address,
            csrf_token=csrf_token,
            default_conversation_id=os.getenv("ANTIGRAVITY_CONVERSATION_ID"),
        )


class AntigravityCliAdapter(AgentRuntimeAdapter):
    """
    Bridge adapter for the verified local `agy.exe agentapi` surface.

    Current scope is intentionally narrow:
    - reuse an existing conversation id;
    - send messages through `--print --conversation=...`;
    - issue `stop` as a regular message for cancellation.
    """

    def __init__(self, config: AntigravityCliConfig) -> None:
        self._config = config

    async def create_session(self, workspace: WorkspaceRecord, options: dict[str, Any]) -> RuntimeSession:
        conversation_id = (
            options.get("conversation_id")
            or options.get("runtime_session_id")
            or self._config.default_conversation_id
        )
        metadata: dict[str, Any]
        if not conversation_id:
            conversation_id, bootstrap_text = self._bootstrap_conversation(workspace)
            metadata = {
                "workspacePath": workspace.absolute_path,
                "adapter": "antigravity_cli",
                "createMode": "new_project_bootstrap",
                "bootstrapResponse": bootstrap_text,
            }
        else:
            metadata = {
                "workspacePath": workspace.absolute_path,
                "adapter": "antigravity_cli",
                "createMode": "resume_existing",
            }
        return RuntimeSession(runtime_session_id=conversation_id, metadata=metadata)

    async def send_message(
        self,
        session_id: str,
        message: str,
        attachments: list[str],
    ) -> RuntimeMessageResult:
        if attachments:
            raise AntigravityCliError("Attachments are not implemented in the CLI adapter yet.")
        if not session_id:
            raise AntigravityCliError(
                "No Antigravity conversation id is configured for this bridge session."
            )

        payload = self._run_print_mode(session_id=session_id, message=message, stream=True)
        response_text = self._extract_response_text(payload)
        return RuntimeMessageResult(
            message_text=response_text,
            metadata={"adapter": "antigravity_cli", "conversationId": session_id},
        )

    async def approve_action(self, approval_id: str) -> None:
        raise AntigravityCliError(f"Programmable approval handling is not implemented yet: {approval_id}")

    async def reject_action(self, approval_id: str, reason: str | None = None) -> None:
        raise AntigravityCliError(
            f"Programmable approval handling is not implemented yet: {approval_id} ({reason})"
        )

    async def stop_task(self, task_id: str) -> None:
        if not task_id:
            raise AntigravityCliError("No runtime conversation id is available for stop.")
        self._run_agentapi(["send-message", task_id, "stop"])

    async def resume_session(self, session_id: str) -> None:
        if not session_id:
            raise AntigravityCliError("No runtime conversation id is available for resume.")

    async def close_session(self, session_id: str) -> None:
        _ = session_id

    def _run_agentapi(self, arguments: list[str]) -> dict[str, Any]:
        executable_path = Path(self._config.executable_path)
        if not executable_path.exists():
            raise AntigravityCliError(f"Antigravity CLI executable not found: {executable_path}")

        env = os.environ.copy()
        env["ANTIGRAVITY_LS_ADDRESS"] = self._config.ls_address
        env["ANTIGRAVITY_CSRF_TOKEN"] = self._config.csrf_token

        completed = subprocess.run(
            [str(executable_path), "agentapi", *arguments],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        payload_text = stdout or stderr
        payload = self._parse_payload(payload_text)
        error_text = payload.get("error") if isinstance(payload, dict) else None

        if completed.returncode != 0 or error_text:
            raise AntigravityCliError(
                error_text
                or stderr
                or stdout
                or f"Agent API call failed with exit code {completed.returncode}."
            )

        return payload

    def _run_print_mode(self, *, session_id: str, message: str, stream: bool) -> dict[str, Any]:
        executable_path = Path(self._config.executable_path)
        if not executable_path.exists():
            raise AntigravityCliError(f"Antigravity CLI executable not found: {executable_path}")

        env = os.environ.copy()
        env["ANTIGRAVITY_LS_ADDRESS"] = self._config.ls_address
        env["ANTIGRAVITY_CSRF_TOKEN"] = self._config.csrf_token

        output_format = "stream-json" if stream else "json"
        completed = subprocess.run(
            [
                str(executable_path),
                "--print",
                f"--output-format={output_format}",
                f"--conversation={session_id}",
                "--prompt",
                message,
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if completed.returncode != 0:
            raise AntigravityCliError(stderr or stdout or "Print mode call failed.")

        payload_text = stdout or stderr
        if payload_text.startswith("```json"):
            payload_text = payload_text.removeprefix("```json").removesuffix("```").strip()
        payload = self._parse_print_payload(payload_text)
        return payload

    def _bootstrap_conversation(self, workspace: WorkspaceRecord) -> tuple[str, str]:
        executable_path = Path(self._config.executable_path)
        if not executable_path.exists():
            raise AntigravityCliError(f"Antigravity CLI executable not found: {executable_path}")

        before_ids = self._list_conversation_ids()
        completed = subprocess.run(
            [
                str(executable_path),
                "--print",
                "--output-format=json",
                "--new-project",
                "--prompt",
                "Reply with only: bridge bootstrap ready",
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=workspace.absolute_path,
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if completed.returncode != 0:
            raise AntigravityCliError(stderr or stdout or "Failed to bootstrap a new Antigravity conversation.")

        after_ids = self._list_conversation_ids()
        new_ids = [conversation_id for conversation_id in after_ids if conversation_id not in before_ids]
        if not new_ids:
            newest = self._latest_conversation_id()
            if newest is None:
                raise AntigravityCliError("Unable to discover the new conversation id after bootstrap.")
            conversation_id = newest
        else:
            conversation_id = new_ids[0]
        return conversation_id, stdout or stderr

    @staticmethod
    def _conversation_dir() -> Path:
        return Path(r"C:\Users\user\.gemini\antigravity-cli\conversations")

    def _list_conversation_ids(self) -> list[str]:
        directory = self._conversation_dir()
        if not directory.exists():
            return []
        conversation_ids: list[str] = []
        for item in directory.glob("*.db"):
            try:
                UUID(item.stem)
            except ValueError:
                continue
            conversation_ids.append(item.stem)
        return conversation_ids

    def _latest_conversation_id(self) -> str | None:
        directory = self._conversation_dir()
        if not directory.exists():
            return None
        candidates = []
        for item in directory.glob("*.db"):
            try:
                UUID(item.stem)
            except ValueError:
                continue
            candidates.append(item)
        if not candidates:
            return None
        candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        return candidates[0].stem

    @staticmethod
    def _parse_payload(payload_text: str) -> dict[str, Any]:
        if not payload_text:
            return {}
        try:
            parsed = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            raise AntigravityCliError(f"Unexpected agent API output: {payload_text}") from exc
        if not isinstance(parsed, dict):
            raise AntigravityCliError(f"Unexpected agent API payload type: {type(parsed).__name__}")
        return parsed

    def _parse_print_payload(self, payload_text: str) -> dict[str, Any]:
        stripped = payload_text.strip()
        if not stripped:
            return {}
        try:
            return self._parse_payload(stripped)
        except AntigravityCliError:
            return {"response": stripped}

    @staticmethod
    def _extract_response_text(payload: dict[str, Any]) -> str:
        if not payload:
            return ""
        if "response" in payload and isinstance(payload["response"], str):
            return payload["response"]
        return json.dumps(payload, ensure_ascii=True)
