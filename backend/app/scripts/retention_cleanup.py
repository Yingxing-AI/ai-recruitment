from __future__ import annotations

import argparse

from app.db.session import SessionLocal
from app.services.retention_service import apply_data_retention


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply data retention rules for AI recruitment data")
    parser.add_argument("--audit-days", type=int, default=180)
    parser.add_argument("--ai-days", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = apply_data_retention(
            db,
            audit_log_days=args.audit_days,
            ai_artifact_days=args.ai_days,
            dry_run=args.dry_run,
        )
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
