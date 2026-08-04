from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.models.approvals import ApprovalDecisionResponse, ApprovalRecord
from app.models.events import BridgeEvent
from app.runtime.base import RuntimeAdapterError
from app.services.approval_store import approval_store
from app.services.audit_log import audit_log
from app.services.runtime_registry import get_runtime_adapter
from app.services.session_store import session_store

router = APIRouter(tags=["approvals"])


@router.get("/approvals")
async def list_approvals() -> list[ApprovalRecord]:
    return [approval_store.get(item.approval_id) or item for item in approval_store.list()]


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalDecisionResponse)
async def approve_request(approval_id: str) -> ApprovalDecisionResponse:
    approval = approval_store.get(approval_id)
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval is not pending")

    session = session_store.get(approval.session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    adapter = get_runtime_adapter()
    try:
        runtime_result = None
        if approval.runtime_action_id:
            await adapter.approve_action(approval.runtime_action_id)
        else:
            runtime_result = await adapter.send_message(
                session_id=session.runtime_session_id or session.session_id,
                message=approval.message or "",
                attachments=[],
            )
    except RuntimeAdapterError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    resolved = approval.model_copy(
        update={
            "status": "approved",
            "resolved_at": datetime.now(UTC),
            "resolved_by_device": "bridge_local",
        }
    )
    approval_store.save(resolved)
    session_store.save(
        session.model_copy(
            update={
                "status": "active",
                "updated_at": datetime.now(UTC),
                "last_message_at": datetime.now(UTC),
                "pending_approval_id": None,
            }
        )
    )
    session_store.push_event(
        BridgeEvent.approval_resolved(
            session_id=approval.session_id,
            task_id=None,
            payload={"approvalId": approval.approval_id, "status": "approved"},
        )
    )
    session_store.push_event(
        BridgeEvent.assistant_delta(
            session_id=approval.session_id,
            task_id=None,
            payload={"preview": runtime_result.message_text[:400] if runtime_result else ""},
        )
    )
    session_store.push_event(
        BridgeEvent.assistant_completed(
            session_id=approval.session_id,
            task_id=None,
            payload={"message": runtime_result.message_text if runtime_result else ""},
        )
    )
    session_store.push_event(
        BridgeEvent.activity_completed(
            session_id=approval.session_id,
            task_id=None,
            payload={"activityType": approval.action_type, "status": "approved"},
        )
    )
    audit_log.append(
        "approval.executed",
        {
            "approvalId": approval.approval_id,
            "sessionId": approval.session_id,
            "responsePreview": runtime_result.message_text[:400] if runtime_result else "",
        },
    )
    return ApprovalDecisionResponse(approval=resolved, result="approved")


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalDecisionResponse)
async def reject_request(approval_id: str) -> ApprovalDecisionResponse:
    approval = approval_store.get(approval_id)
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval is not pending")
    session = session_store.get(approval.session_id)

    resolved = approval.model_copy(
        update={
            "status": "rejected",
            "resolved_at": datetime.now(UTC),
            "resolved_by_device": "bridge_local",
        }
    )
    approval_store.save(resolved)
    if session is not None:
        session_store.save(
            session.model_copy(
                update={
                    "status": "idle",
                    "updated_at": datetime.now(UTC),
                    "pending_approval_id": None,
                }
            )
        )
    session_store.push_event(
        BridgeEvent.approval_resolved(
            session_id=approval.session_id,
            task_id=None,
            payload={"approvalId": approval.approval_id, "status": "rejected"},
        )
    )
    session_store.push_event(
        BridgeEvent.activity_completed(
            session_id=approval.session_id,
            task_id=None,
            payload={"activityType": approval.action_type, "status": "rejected"},
        )
    )
    return ApprovalDecisionResponse(approval=resolved, result="rejected")
