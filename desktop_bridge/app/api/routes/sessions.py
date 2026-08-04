from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.events import BridgeEvent
from app.runtime.antigravity_cli import AntigravityCliError
from app.models.sessions import (
    CreateSessionRequest,
    CreateSessionResponse,
    SendMessageRequest,
    SessionRecord,
)
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


@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, request: SendMessageRequest) -> dict[str, str]:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    adapter = get_runtime_adapter()
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
