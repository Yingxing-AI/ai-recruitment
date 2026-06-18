from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import delete, func, select, update

from app.models.ai_analysis import AIResumeAnalysis, JobMatchScore
from app.models.audit_log import AuditLog


def apply_data_retention(
    db,
    *,
    audit_log_days: int = 180,
    ai_artifact_days: int = 90,
    dry_run: bool = False,
) -> dict[str, Any]:
    now = datetime.utcnow()
    audit_cutoff = now - timedelta(days=audit_log_days)
    ai_cutoff = now - timedelta(days=ai_artifact_days)

    audit_count = db.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.created_at < audit_cutoff))
    analysis_count = db.scalar(
        select(func.count()).select_from(AIResumeAnalysis).where(
            AIResumeAnalysis.updated_at < ai_cutoff,
            AIResumeAnalysis.raw_response.is_not(None),
        )
    )
    match_count = db.scalar(
        select(func.count()).select_from(JobMatchScore).where(
            JobMatchScore.updated_at < ai_cutoff,
            JobMatchScore.raw_response.is_not(None),
        )
    )

    if not dry_run:
        db.execute(delete(AuditLog).where(AuditLog.created_at < audit_cutoff))
        db.execute(
            update(AIResumeAnalysis)
            .where(AIResumeAnalysis.updated_at < ai_cutoff, AIResumeAnalysis.raw_response.is_not(None))
            .values(raw_response=None)
        )
        db.execute(
            update(JobMatchScore)
            .where(JobMatchScore.updated_at < ai_cutoff, JobMatchScore.raw_response.is_not(None))
            .values(raw_response=None)
        )
        db.commit()

    return {
        "audit_logs_expired": audit_count or 0,
        "ai_analyses_redacted": analysis_count or 0,
        "job_matches_redacted": match_count or 0,
        "dry_run": dry_run,
        "audit_log_days": audit_log_days,
        "ai_artifact_days": ai_artifact_days,
    }
