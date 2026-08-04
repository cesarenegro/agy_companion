from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ApprovalStatus = Literal["pending", "approved", "rejected", "expired"]
ApprovalActionType = Literal["run_command", "write_file", "runtime_message"]
RiskLevel = Literal["medium", "high"]


class ApprovalRecord(BaseModel):
    approval_id: str = Field(alias="approvalId")
    session_id: str = Field(alias="sessionId")
    task_id: str | None = Field(alias="taskId", default=None)
    runtime_action_id: str | None = Field(alias="runtimeActionId", default=None)
    action_type: ApprovalActionType = Field(alias="actionType")
    command: str | None = None
    working_directory: str | None = Field(alias="workingDirectory", default=None)
    affected_files: list[str] = Field(alias="affectedFiles", default_factory=list)
    reason: str
    risk_level: RiskLevel = Field(alias="riskLevel")
    status: ApprovalStatus
    message: str | None = None
    created_at: datetime = Field(alias="createdAt")
    expires_at: datetime = Field(alias="expiresAt")
    resolved_at: datetime | None = Field(alias="resolvedAt", default=None)
    resolved_by_device: str | None = Field(alias="resolvedByDevice", default=None)


class ApprovalDecisionResponse(BaseModel):
    approval: ApprovalRecord
    result: str
