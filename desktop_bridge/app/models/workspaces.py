from datetime import UTC, datetime
from typing import Literal

from pathlib import Path

from pydantic import BaseModel


PermissionProfile = Literal["read_only", "standard"]


class WorkspaceRecord(BaseModel):
    workspace_id: str
    display_name: str
    absolute_path: str
    repository_root: str
    default_branch: str
    permission_profile: PermissionProfile
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    def resolved_root(self) -> Path:
        return Path(self.absolute_path).resolve()

    @classmethod
    def sample(cls, *, absolute_path: str) -> "WorkspaceRecord":
        now = datetime.now(UTC)
        return cls(
            workspace_id="ws_local",
            display_name="Authorized Test Workspace",
            absolute_path=absolute_path,
            repository_root=absolute_path,
            default_branch="main",
            permission_profile="standard",
            is_enabled=True,
            created_at=now,
            updated_at=now,
        )
