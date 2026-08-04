from pathlib import Path

from app.models.workspaces import WorkspaceRecord


class InMemoryWorkspaceStore:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[3]
        self._workspaces: dict[str, WorkspaceRecord] = {
            "ws_local": WorkspaceRecord.sample(absolute_path=str(root))
        }

    def get(self, workspace_id: str) -> WorkspaceRecord | None:
        return self._workspaces.get(workspace_id)

    def list(self) -> list[WorkspaceRecord]:
        return list(self._workspaces.values())


workspace_store = InMemoryWorkspaceStore()
