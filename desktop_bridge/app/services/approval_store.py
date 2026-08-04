from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models.approvals import ApprovalRecord
from app.services.audit_log import audit_log


class InMemoryApprovalStore:
    def __init__(self) -> None:
        self._approvals: dict[str, ApprovalRecord] = {}

    def create(
        self,
        *,
        session_id: str,
        action_type: str,
        reason: str,
        risk_level: str,
        message: str,
        working_directory: str,
        runtime_action_id: str | None = None,
        command: str | None = None,
        affected_files: list[str] | None = None,
    ) -> ApprovalRecord:
        now = datetime.now(UTC)
        approval = ApprovalRecord(
            approvalId=f"apr_{uuid4().hex[:12]}",
            sessionId=session_id,
            taskId=None,
            runtimeActionId=runtime_action_id,
            actionType=action_type,
            command=command,
            workingDirectory=working_directory,
            affectedFiles=affected_files or [],
            reason=reason,
            riskLevel=risk_level,
            status="pending",
            message=message,
            createdAt=now,
            expiresAt=now + timedelta(minutes=10),
            resolvedAt=None,
            resolvedByDevice=None,
        )
        self._approvals[approval.approval_id] = approval
        audit_log.append("approval.created", approval.model_dump(by_alias=True, mode="json"))
        return approval

    def list(self) -> list[ApprovalRecord]:
        return list(self._approvals.values())

    def get(self, approval_id: str) -> ApprovalRecord | None:
        approval = self._approvals.get(approval_id)
        if approval is None:
            return None
        if approval.status == "pending" and approval.expires_at < datetime.now(UTC):
            expired = approval.model_copy(
                update={"status": "expired", "resolved_at": datetime.now(UTC)}
            )
            self._approvals[approval_id] = expired
            audit_log.append("approval.expired", expired.model_dump(by_alias=True, mode="json"))
            return expired
        return approval

    def save(self, approval: ApprovalRecord) -> None:
        self._approvals[approval.approval_id] = approval
        audit_log.append("approval.updated", approval.model_dump(by_alias=True, mode="json"))


approval_store = InMemoryApprovalStore()
