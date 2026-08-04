from fastapi import APIRouter

from app.services.audit_log import audit_log
from app.services.runtime_registry import get_runtime_status

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck() -> dict[str, str | bool]:
    return {"status": "ok", "auditLogPath": audit_log.path, **get_runtime_status()}
