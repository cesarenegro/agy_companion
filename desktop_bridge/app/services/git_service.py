import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.models.git import GitStatusEntry, GitStatusResponse


class GitServiceError(RuntimeError):
    """Raised when Git inspection fails for an authorized workspace."""


@dataclass(frozen=True)
class GitInspection:
    repository_root: str
    branch: str | None
    entries: list[GitStatusEntry]


def ensure_workspace_exists(workspace_path: str) -> None:
    resolved = Path(workspace_path).resolve()
    if not resolved.exists():
        raise GitServiceError(f"Workspace path does not exist: {workspace_path}")
    if not resolved.is_dir():
        raise GitServiceError(f"Workspace path is not a directory: {workspace_path}")


def _run_git(workspace_path: str, arguments: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", workspace_path, *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        raise GitServiceError(stderr or stdout or "Git command failed.")
    return completed.stdout


def inspect_repository(workspace_path: str) -> GitInspection:
    repository_root = _run_git(workspace_path, ["rev-parse", "--show-toplevel"]).strip()
    branch = _run_git(workspace_path, ["branch", "--show-current"]).strip() or None
    status_output = _run_git(workspace_path, ["status", "--short"])

    entries: list[GitStatusEntry] = []
    for line in status_output.splitlines():
        if not line.strip():
            continue
        status_code = line[:2]
        path = line[3:].strip()
        entries.append(
            GitStatusEntry(
                path=path,
                indexStatus=status_code[0],
                worktreeStatus=status_code[1],
            )
        )

    return GitInspection(
        repository_root=repository_root,
        branch=branch,
        entries=entries,
    )


def get_git_status(workspace_path: str) -> GitStatusResponse:
    inspection = inspect_repository(workspace_path)
    return GitStatusResponse(
        repositoryRoot=inspection.repository_root,
        branch=inspection.branch,
        isDirty=bool(inspection.entries),
        entries=inspection.entries,
    )


def get_unified_diff(workspace_path: str) -> str:
    inspection = inspect_repository(workspace_path)
    return _run_git(inspection.repository_root, ["diff", "HEAD"])
