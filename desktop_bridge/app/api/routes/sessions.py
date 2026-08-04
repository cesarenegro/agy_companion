from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.events import BridgeEvent
from app.models.git import SessionChangesResponse, SessionDiffResponse
from app.services.approval_policy import classify_message
from app.services.approval_store import approval_store
from app.runtime.antigravity_cli import AntigravityCliError
from app.models.sessions import (
    CreateSessionRequest,
    CreateSessionResponse,
    SendMessageRequest,
    SessionRecord,
)
from app.services.git_service import GitServiceError, ensure_workspace_exists, get_git_status, get_unified_diff
from app.services.runtime_registry import get_runtime_adapter
from app.services.session_store import session_store
from app.services.workspace_store import workspace_store

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: CreateSessionRequest) -> CreateSessionResponse:
    workspace = workspace_store.get(request.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    adapter = get_runtime_adapter()
    try:
        runtime_session = await adapter.create_session(workspace=workspace, options=request.options)
    except AntigravityCliError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    record = SessionRecord(
        session_id=f"ses_{uuid4().hex[:12]}",
        runtime_session_id=runtime_session.runtime_session_id,
        workspace_id=workspace.workspace_id,
        desktop_id="desktop_local",
        title=request.title or workspace.display_name,
        status="idle",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        last_message_at=None,
        active_task_id=None,
    )
    session_store.save(record)
    session_store.push_event(
        BridgeEvent.session_created(
            session_id=record.session_id,
            task_id=None,
            payload={"workspaceId": workspace.workspace_id},
        )
    )
    return CreateSessionResponse(session=record)


@router.get("/sessions")
async def list_sessions() -> list[SessionRecord]:
    return session_store.list()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> SessionRecord:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.get("/sessions/{session_id}/events")
async def get_session_events(
    session_id: str,
    after_event_id: str | None = None,
    limit: int = 100,
) -> list[dict]:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    events = session_store.list_events_for_session(
        session_id,
        after_event_id=after_event_id,
        limit=max(1, min(limit, 200)),
    )
    return [event.model_dump(by_alias=True, mode="json") for event in events]


@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, request: SendMessageRequest) -> dict[str, str]:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    workspace = workspace_store.get(session.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    approval_requirement = classify_message(request.message, workspace)
    if approval_requirement.required:
        approval = approval_store.create(
            session_id=session_id,
            action_type=approval_requirement.action_type or "runtime_message",
            reason=approval_requirement.reason or "Sensitive action requires approval.",
            risk_level=approval_requirement.risk_level or "medium",
            message=request.message,
            working_directory=workspace.absolute_path,
            command=request.message,
        )
        updated = session.model_copy(
            update={
                "status": "waiting_approval",
                "updated_at": datetime.now(UTC),
                "pending_approval_id": approval.approval_id,
            }
        )
        session_store.save(updated)
        session_store.push_event(
            BridgeEvent.approval_requested(
                session_id=session_id,
                task_id=None,
                payload={
                    "approvalId": approval.approval_id,
                    "actionType": approval.action_type,
                    "riskLevel": approval.risk_level,
                    "reason": approval.reason,
                },
            )
        )
        return {"status": "waiting_approval", "approvalId": approval.approval_id}

    adapter = get_runtime_adapter()
    session_store.push_event(
        BridgeEvent.activity_started(
            session_id=session_id,
            task_id=None,
            payload={"activityType": "runtime_message", "displayName": request.message[:120]},
        )
    )
    try:
        runtime_result = await adapter.send_message(
            session_id=session.runtime_session_id or session.session_id,
            message=request.message,
            attachments=request.attachments,
        )
    except AntigravityCliError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    updated = session.model_copy(
        update={
            "status": "active",
            "updated_at": datetime.now(UTC),
            "last_message_at": datetime.now(UTC),
            "pending_approval_id": None,
        }
    )
    session_store.save(updated)
    session_store.push_event(
        BridgeEvent.assistant_delta(
            session_id=session_id,
            task_id=None,
            payload={"preview": runtime_result.message_text[:400]},
        )
    )
    session_store.push_event(
        BridgeEvent.assistant_completed(
            session_id=session_id,
            task_id=None,
            payload={"message": runtime_result.message_text},
        )
    )
    session_store.push_event(
        BridgeEvent.activity_completed(
            session_id=session_id,
            task_id=None,
            payload={"activityType": "runtime_message", "status": "completed"},
        )
    )
    return {"status": "accepted", "response": runtime_result.message_text}


@router.post("/sessions/{session_id}/stop")
async def stop_session_task(session_id: str) -> dict[str, str]:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    adapter = get_runtime_adapter()
    try:
        await adapter.stop_task(task_id=session.runtime_session_id or session.active_task_id or session_id)
    except AntigravityCliError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    session_store.push_event(
        BridgeEvent.task_status_changed(
            session_id=session_id,
            task_id=session.active_task_id,
            payload={"status": "stop_requested"},
        )
    )
    return {"status": "stop_requested"}


@router.get("/sessions/{session_id}/changes", response_model=SessionChangesResponse)
async def get_session_changes(session_id: str) -> SessionChangesResponse:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    workspace = workspace_store.get(session.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    try:
        ensure_workspace_exists(workspace.absolute_path)
        git_status = get_git_status(workspace.absolute_path)
    except GitServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SessionChangesResponse(
        sessionId=session_id,
        repositoryRoot=git_status.repository_root,
        changedFiles=git_status.entries,
    )


@router.get("/sessions/{session_id}/diff", response_model=SessionDiffResponse)
async def get_session_diff(session_id: str) -> SessionDiffResponse:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    workspace = workspace_store.get(session.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    try:
        ensure_workspace_exists(workspace.absolute_path)
        diff_text = get_unified_diff(workspace.absolute_path)
        git_status = get_git_status(workspace.absolute_path)
    except GitServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SessionDiffResponse(
        sessionId=session_id,
        repositoryRoot=git_status.repository_root,
        diff=diff_text,
    )
