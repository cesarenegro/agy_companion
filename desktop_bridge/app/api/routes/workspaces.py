from fastapi import APIRouter, HTTPException, status

from app.models.git import GitStatusResponse
from app.models.workspaces import WorkspaceRecord
from app.services.git_service import GitServiceError, ensure_workspace_exists, get_git_status
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


@router.get("/workspaces/{workspace_id}/git-status", response_model=GitStatusResponse)
async def get_workspace_git_status(workspace_id: str) -> GitStatusResponse:
    workspace = workspace_store.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    try:
        ensure_workspace_exists(workspace.absolute_path)
        return get_git_status(workspace.absolute_path)
    except GitServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
