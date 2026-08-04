from dataclasses import dataclass

from app.models.workspaces import WorkspaceRecord


@dataclass(frozen=True)
class ApprovalRequirement:
    required: bool
    action_type: str | None = None
    risk_level: str | None = None
    reason: str | None = None


COMMAND_MARKERS = (
    "run the command",
    "execute command",
    "powershell ",
    "cmd /c",
    "bash ",
    "npm ",
    "pip install",
    "apt ",
)

WRITE_MARKERS = (
    "create a file",
    "modify file",
    "delete file",
    "rename file",
    "write to",
)


def classify_message(message: str, workspace: WorkspaceRecord) -> ApprovalRequirement:
    lower = message.lower()
    if workspace.permission_profile == "read_only":
        return ApprovalRequirement(
            required=True,
            action_type="runtime_message",
            risk_level="high",
            reason="Workspace is read-only.",
        )
    if any(marker in lower for marker in COMMAND_MARKERS):
        return ApprovalRequirement(
            required=True,
            action_type="run_command",
            risk_level="high",
            reason="Message appears to request command execution.",
        )
    if any(marker in lower for marker in WRITE_MARKERS):
        return ApprovalRequirement(
            required=True,
            action_type="write_file",
            risk_level="medium",
            reason="Message appears to request file modification.",
        )
    return ApprovalRequirement(required=False)
