from fastapi import APIRouter, HTTPException, status

from app.models.workspaces import WorkspaceRecord
from app.services.workspace_store import workspace_store

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces")
async def list_workspaces() -> list[WorkspaceRecord]:
    return workspace_store.list()


@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str) -> WorkspaceRecord:
    workspace = workspace_store.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace
