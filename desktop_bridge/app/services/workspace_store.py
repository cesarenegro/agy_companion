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

    def ensure_within_workspace(self, workspace_id: str, candidate_path: str) -> Path:
        workspace = self.get(workspace_id)
        if workspace is None:
            raise ValueError("Workspace not found")
        root = workspace.resolved_root()
        candidate = Path(candidate_path).resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError("Path escapes the authorized workspace")
        return candidate


workspace_store = InMemoryWorkspaceStore()
