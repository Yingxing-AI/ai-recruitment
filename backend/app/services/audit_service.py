from __future__ import annotations

from typing import Any

from app.models.audit_log import AuditLog


def log_audit_event(
    db,
    *,
    action: str,
    target_type: str | None = None,
    target_id: int | None = None,
    detail: dict[str, Any] | None = None,
    user_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail_json=detail,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    return log
