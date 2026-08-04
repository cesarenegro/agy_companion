from pydantic import BaseModel, Field


class GitStatusEntry(BaseModel):
    path: str
    index_status: str = Field(alias="indexStatus")
    worktree_status: str = Field(alias="worktreeStatus")


class GitStatusResponse(BaseModel):
    repository_root: str = Field(alias="repositoryRoot")
    branch: str | None = None
    is_dirty: bool = Field(alias="isDirty")
    entries: list[GitStatusEntry]


class SessionChangesResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    repository_root: str = Field(alias="repositoryRoot")
    changed_files: list[GitStatusEntry] = Field(alias="changedFiles")


class SessionDiffResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    repository_root: str = Field(alias="repositoryRoot")
    diff: str
